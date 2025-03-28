import requests  # for making HTTP requests
from decimal import Decimal, InvalidOperation  # For precise decimal arithmetic and error handling
import logging  # for debugging and monitoring
import boto3
from boto3.dynamodb.conditions import Attr
import json

logger = logging.getLogger(__name__)  # Initialize logger 

class Calculations:
    def __init__(self, api_key):
        """Initializes the Calculations class with an API key."""
        self.api_key = api_key  
        self.base_url = "https://www.carboninterface.com/api/v1/estimates"  # URL for the Carbon Interface API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}", 
            "Content-Type": "application/json",  
        }
        

    def calculate_electricity_emission(self, api_data):
        """Calculates electricity emissions using provided API data."""
        try:
            # Converting the value to a Decimal and removing leading/trailing spaces
            value = Decimal(str(api_data["value"]).strip())
            payload = {
                "type": "electricity", 
                "electricity_unit": api_data["unit"].lower(),  
                "electricity_value": str(value),  
                "country": api_data["location"],  # Country code
            }
            
            logger.debug(f"Sending electricity API request with payload: {payload}")  
            
            response = requests.post(self.base_url, headers=self.headers, json=payload)  # Send POST request to the API
            response.raise_for_status()  # For bad status codes 
            
            data = response.json()  # Parsing the JSON response
            emission = Decimal(data["data"]["attributes"]["carbon_kg"])  # Extract and convert carbon emission to Decimal
            
            logger.debug(f"Electricity API response: {data}") 
            return emission  # Return the calculated emission
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Electricity API request failed: {e}")  
            return None  #in case of failure
            
        except KeyError as e:
            logger.error(f"Electricity API response missing key: {e}") 
            return None #in case of failure
            
        except InvalidOperation as e:
            logger.error(f"Invalid decimal operation in electricity calculation: {e}") 
            return None # in case of failure
            
        except Exception as e:
            logger.exception("Unexpected error in electricity calculation:") # Log all other exceptions.
            return None

    def calculate_flight_emission(self, passengers, legs, distance_unit="km", cabin_class=None):
        """Calculates flight emissions."""
        payload = {
            "type": "flight",
            "passengers": passengers,
            "legs": legs,
            "distance_unit": distance_unit,
        }
        if cabin_class:
            payload["cabin_class"] = cabin_class  

        try:
            logger.debug(f"Sending flight API request with payload: {payload}")
            response = requests.post(self.base_url, headers=self.headers, json=payload)  
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()  # Parse the JSON response
            emission = Decimal(data["data"]["attributes"]["carbon_kg"])  # Extract and convert carbon emission to Decimal
            logger.debug(f"Flight API response: {data}") #log the response
            return emission  # Return the calculated emission
        except requests.exceptions.RequestException as e:
            logger.error(f"Flight API request failed: {e}")  # Log API request failures
            return None
        except KeyError as e:
            logger.error(f"Flight API response missing key: {e}") #log Key errors.
            return None
        except InvalidOperation as e:
            logger.error(f"Invalid decimal operation in flight calculation: {e}") #log decimal errors.
            return None
        except Exception as e:
            logger.exception("Unexpected error in flight calculation:") #log other errors.
            return None

    def calculate_shipping_emission(self, weight_value, weight_unit, distance_value, distance_unit, transport_method):
        """Calculates shipping emissions."""
        try:
            # Convert weight and distance values to Decimal for precise calculations, removing leading/trailing spaces
            weight_value = Decimal(str(weight_value).strip())
            distance_value = Decimal(str(distance_value).strip())

            payload = {
                "type": "shipping",  
                "weight_value": str(weight_value),  
                "weight_unit": weight_unit,
                "distance_value": str(distance_value),
                "distance_unit": distance_unit,
                "transport_method": transport_method,
            }
            logger.debug(f"Sending shipping API request with payload: {payload}")
            response = requests.post(self.base_url, headers=self.headers, json=payload)  # Send POST request to the API
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()  # Parse the JSON response
            emission = Decimal(data["data"]["attributes"]["carbon_kg"])  # Extract and convert carbon emission to Decimal
            logger.debug(f"Shipping API response: {data}") 
            return emission  
        except requests.exceptions.RequestException as e:
            logger.error(f"Shipping API request failed: {e}")
            return None
        except KeyError as e:
            logger.error(f"Shipping API response missing key: {e}")
            return None
        except InvalidOperation as e:
            logger.error(f"Invalid decimal operation in shipping calculation: {e}")
            return None
        except Exception as e:
            logger.exception("Unexpected error in shipping calculation:")
            return None
            
            
    def get_fuel_sources_from_dynamodb(self):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('fuel_sources')
        response = table.scan()
        return response.get('Items', [])
        
    def get_api_name_by_fuel_type(self, fuel_source_type):
        """Retrieves the api_name for a given fuel_source_type from DynamoDB."""
        dynamodb = boto3.resource('dynamodb')
        fuel_sources_table = dynamodb.Table('fuel_sources')
        response = fuel_sources_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('fuel_source_type').eq(fuel_source_type)
        )
        items = response.get('Items', [])
        if items:
            return items[0].get('api_name')
        return None

    def calculate_fuel_combustion_emission(self, fuel_source_type, fuel_source_unit, fuel_source_value):
        """Calculates fuel combustion emissions using the Carbon Interface API."""
        api_name = self.get_api_name_by_fuel_type(fuel_source_type) # get api_name.
        if not api_name:
            print(f"Error: api_name not found for fuel_source_type: {fuel_source_type}")
            return None

        data = {
            "type": "fuel_combustion",
            "fuel_source_type": api_name, #use api_name here.
            "fuel_source_unit": fuel_source_unit,
            "fuel_source_value": float(fuel_source_value)
        }
        print(f"Request Data: {data}")
        try:
            response = requests.post(self.base_url, headers=self.headers, json=data)
            print(f"response: {response}")
            response.raise_for_status()
            result = response.json()
            print(f"result: {result}")
            carbon_kg = result['data']['attributes']['carbon_kg']
            print(f"Carbon emission= {carbon_kg}")
            return Decimal(str(carbon_kg))
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"Error parsing API response: {e}")
            return None

            
    def get_unique_fuel_source_types(self):
        """Retrieves unique fuel source types from DynamoDB."""
        dynamodb = boto3.resource('dynamodb')
        fuel_sources_table = dynamodb.Table('fuel_sources')
        response = fuel_sources_table.scan()
        items = response.get('Items', [])
        fuel_source_types = set(item['fuel_source_type'] for item in items)
        return list(fuel_source_types)

    def get_units_by_fuel_type(self, fuel_type):
        """Retrieves units for a specific fuel type."""
        dynamodb = boto3.resource('dynamodb')
        fuel_sources_table = dynamodb.Table('fuel_sources')
        response = fuel_sources_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('fuel_source_type').eq(fuel_type)
        )
        items = response.get('Items', [])
        units = [item.get('unit') for item in items if item.get('unit')]
        return units
        
    def get_vehicle_makes_from_dynamodb(self):
        """Fetches distinct vehicle makes from DynamoDB."""
        try:
            logger.debug("Fetching vehicle makes from DynamoDB...")
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('VehicleModels')
            logger.debug(f"DynamoDB table: {table.name}")
            response = table.scan(ProjectionExpression='vehicle_make')
            logger.debug(f"DynamoDB scan response: {response}")
            makes = set(item['vehicle_make'] for item in response['Items'])
            logger.debug(f"Distinct vehicle makes found: {makes}")
            sorted_makes = sorted(list(makes))
            logger.debug(f"Sorted vehicle makes: {sorted_makes}")
            return sorted_makes
        except Exception as e:
            logger.error(f"Error fetching vehicle makes from DynamoDB: {e}")
            print(f"Error fetching vehicle makes: {e}")
            return []

    def get_vehicle_models_from_dynamodb(self, vehicle_make):
        """Fetches vehicle models for a given make from DynamoDB."""
        try:
            logger.debug(f"Fetching vehicle models for make: {vehicle_make} from DynamoDB...")
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('VehicleModels')
            logger.debug(f"DynamoDB table: {table.name}")
            response = table.scan(
                FilterExpression=Attr('vehicle_make').eq(vehicle_make),
                ProjectionExpression='#n, model_id',
                ExpressionAttributeNames={'#n': 'name'}
            )
            logger.debug(f"DynamoDB scan response: {response}")
            models = [{'name': item['name'], 'id': item['model_id']} for item in response['Items']]
            logger.debug(f"Vehicle models found: {models}")
            return models
        except Exception as e:
            logger.error(f"Error fetching vehicle models from DynamoDB: {e}")
            print(f"Error fetching vehicle models: {e}")
            return []

    def calculate_vehicle_emission(self, distance_value, distance_unit, vehicle_model_id):
        """Calculates vehicle emissions using the Carbon Interface API."""
        logger.debug(f"Calculating vehicle emission for distance: {distance_value} {distance_unit}, model ID: {vehicle_model_id}")
        print(f"Calculating vehicle emission for distance: {distance_value} {distance_unit}, model ID: {vehicle_model_id}")
        #distance_value_decimal = Decimal(str(distance_value).strip())
        #logger.debug(f"Distance value as Decimal: {distance_value_decimal}")

        payload = {
                "type": "vehicle",
                "distance_unit": distance_unit,
                "distance_value": float(distance_value),
                "vehicle_model_id": vehicle_model_id,
        }
        logger.debug(f"API payload: {payload}")
        print(f"Request Payload: {payload}")
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            print(f"response: {response}")
            response.raise_for_status()
            result = response.json()
            print(f"result: {result}")
            carbon_kg = result['data']['attributes']['carbon_kg']
            print(f"Carbon emission= {carbon_kg}")
            return Decimal(str(carbon_kg))
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"Error parsing API response: {e}")
            return None
                