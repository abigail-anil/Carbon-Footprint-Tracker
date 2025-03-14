import boto3
import time
import os
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

class DataStorage:
    def __init__(self, table_name=None, region_name="us-east-1"):
        # Use environment variable for table name, or default to 'CarbonFootprint'
        self.table_name = table_name or os.getenv('CARBON_TABLE', 'CarbonFootprint')
        
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb.Table(self.table_name)

    def store_emission_data(self, user_id, activity_type, input_params, carbon_kg, timestamp=None):
        """"Stores emission data in DynamoDB."""
        print(f"Username inside store_emission_data: {user_id}") 
        
        timestamp = datetime.utcnow().isoformat()  # Store in ISO 8601 format
        
        input_params_str = {}
        for key, value in input_params.items():
            if isinstance(value, Decimal):
                input_params_str[key] = str(value)
            else:
                input_params_str[key] = value
        
        rounded_carbon_kg = carbon_kg.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        item = {
            "userId": user_id,
            "timestamp": timestamp,
            "activityType": activity_type,
            "inputParams": input_params_str,
            "carbonKg": str(rounded_carbon_kg),  # Convert Decimal to string
        }
        try:
            self.table.put_item(Item=item)
        except Exception as e:
            print(f"Error storing data: {e}")
            return False
        return True

    def get_user_emissions(self, user_id):
        """Retrieves emission data for a user."""
        try:
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("userId").eq(user_id)
            )
            items = response.get("Items", [])
            # Convert string Decimal values back to Decimal objects
            for item in items:
                if "carbonKg" in item:
                    item["carbonKg"] = Decimal(item["carbonKg"])
                if "inputParams" in item:
                    for key, value in item["inputParams"].items():
                        try:
                            item["inputParams"][key] = Decimal(value)
                        except:
                            pass # if not a decimal string, leave as is.
                if "timestamp" in item:
                    try:
                        item["timestamp"] = datetime.fromisoformat(item["timestamp"])  # Convert ISO string to datetime
                    except ValueError:
                        print(f"Invalid ISO format for timestamp: {item['timestamp']}")  # Debugging log

                if "timestamp_unix" in item:
                    try:
                        item["timestamp_unix"] = datetime.utcfromtimestamp(int(item["timestamp_unix"]))  # Convert Unix timestamp
                    except ValueError:
                        print(f"Invalid Unix format for timestamp_unix: {item['timestamp_unix']}")  # Debugging log
            return items
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return []

