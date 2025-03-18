import requests  # for making HTTP requests
from decimal import Decimal, InvalidOperation  # For precise decimal arithmetic and error handling
import logging  # for debugging and monitoring

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
                "electricity_unit": api_data["unit"],  
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