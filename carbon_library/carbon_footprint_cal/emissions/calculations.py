import requests
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)

class Calculations:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.carboninterface.com/api/v1/estimates"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def calculate_electricity_emission(self, api_data):
        """Calculates electricity emissions using api_data."""
        try:
            value = Decimal(str(api_data["value"]).strip())
            payload = {
                "type": "electricity",
                "electricity_unit": api_data["unit"],
                "electricity_value": str(value),  # Convert to string for API
                "country": api_data["location"],
            }
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return Decimal(data["data"]["attributes"]["carbon_kg"]) #convert to Decimal
        except (requests.exceptions.RequestException, KeyError, InvalidOperation) as e:
            logger.error(f"API error or Decimal conversion error: {e}")
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
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return Decimal(data["data"]["attributes"]["carbon_kg"]) #convert to Decimal
        except (requests.exceptions.RequestException, KeyError, InvalidOperation) as e:
            logger.error(f"API error or Decimal conversion error: {e}")
            return None

    def calculate_shipping_emission(self, weight_value, weight_unit, distance_value, distance_unit, transport_method):
        """Calculates shipping emissions."""
        try:
            weight_value = Decimal(str(weight_value).strip())
            distance_value = Decimal(str(distance_value).strip())

            payload = {
                "type": "shipping",
                "weight_value": str(weight_value),  # Convert to string for API
                "weight_unit": weight_unit,
                "distance_value": str(distance_value),  # Convert to string for API
                "distance_unit": distance_unit,
                "transport_method": transport_method,
            }
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return Decimal(data["data"]["attributes"]["carbon_kg"]) #convert to Decimal
        except (requests.exceptions.RequestException, KeyError, InvalidOperation) as e:
            logger.error(f"API error or Decimal conversion error: {e}")
            return None