import boto3
import requests
import logging
from decimal import Decimal
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Replace with your actual Carbon Interface API key
API_KEY = "ly0WhDdNgcDOHFmQK4Fw"
BASE_URL = "https://www.carboninterface.com/api/v1/estimates"

class Calculations:
    def __init__(self, api_key, base_url=BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

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
                FilterExpression=boto3.dynamodb.conditions.Attr('vehicle_make').eq(vehicle_make),
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
        # ... (Your existing calculate_vehicle_emission code)
        try:
            logger.debug(f"Calculating vehicle emission for distance: {distance_value} {distance_unit}, model ID: {vehicle_model_id}")
            distance_value_decimal = Decimal(str(distance_value).strip())
            logger.debug(f"Distance value as Decimal: {distance_value_decimal}")

            payload = {
                "type": "vehicle",
                "distance_unit": distance_unit,
                "distance_value": str(distance_value_decimal),
                "vehicle_model_id": vehicle_model_id,
            }
            logger.debug(f"API payload: {payload}")

            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            logger.debug(f"API response status code: {response.status_code}")
            data = response.json()
            logger.debug(f"API response data: {data}")

            if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict) and "attributes" in data["data"]:
                emission_kg = data["data"]["attributes"].get("carbon_kg")
                if emission_kg is not None:
                    logger.debug(f"Vehicle emission calculated successfully: {emission_kg} kg")
                    return emission_kg
                else:
                    logger.error("carbon_kg not found in API response.")
                    print("carbon_kg not found in API response.")
                    return None
            else:
                logger.error(f"Unexpected API response format for emission calculation. Response: {data}")
                print(f"Unexpected API response format: {data}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to calculate vehicle emission: {e}")
            print(f"Failed to calculate vehicle emission: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode json response for emission calculation: {e}")
            print(f"Failed to decode json response: {e}")
            return None
        except KeyError as e:
            logger.error(f"Missing key in API response for emission calculation: {e}")
            print(f"Missing key in API response: {e}")
            return None
        except Exception as e:
            logger.exception("Unexpected error calculating vehicle emission:")
            print(f"Unexpected error calculating vehicle emission: {e}")
            return None

# Create an instance of the Calculations class
calculator = Calculations(API_KEY)

# Test get_vehicle_makes_from_dynamodb
makes = calculator.get_vehicle_makes_from_dynamodb()
print("Vehicle Makes:", makes)

# Test get_vehicle_models_from_dynamodb
if makes:
    test_make = makes[0]  # Use the first make from the list
    models = calculator.get_vehicle_models_from_dynamodb(test_make)
    print(f"Models for {test_make}:", models)

# test calculate_vehicle_emission
if models:
    test_model_id = models[0]['id']
    emission = calculator.calculate_vehicle_emission(100, 'mi', test_model_id)
    print(f"emission for {test_model_id}: {emission}")