import boto3 
import time
import os 
from decimal import Decimal, ROUND_HALF_UP  # For precise decimal arithmetic and rounding
from datetime import datetime  # For working with dates and times
import logging # for logging

logger = logging.getLogger(__name__) #initialize logger

class DataStorage:
    def __init__(self, table_name=None, region_name="us-east-1"):
        """Initializes the DataStorage class with DynamoDB table and region."""
        # Use environment variable for table name, or default to 'CarbonFootprint'
        self.table_name = table_name or os.getenv('CARBON_TABLE', 'CarbonFootprint')

        self.dynamodb = boto3.resource("dynamodb", region_name=region_name) # Create a DynamoDB resource
        self.table = self.dynamodb.Table(self.table_name) # Get the DynamoDB table object

    def store_emission_data(self, user_id, activity_type, input_params, carbon_kg, timestamp=None):
        """Stores emission data in DynamoDB."""
        logger.debug(f"Storing emission data for user: {user_id}") #debug log.
        timestamp = datetime.utcnow().isoformat()  # Store timestamp in ISO 8601 format

        input_params_str = {}
        for key, value in input_params.items():
            if isinstance(value, Decimal):
                input_params_str[key] = str(value) #convert decimal to string before storing.
            else:
                input_params_str[key] = value

        rounded_carbon_kg = carbon_kg.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP) # round the carbon emission.

        item = {
            "userId": user_id,
            "timestamp": timestamp,
            "activityType": activity_type,
            "inputParams": input_params_str,
            "carbonKg": str(rounded_carbon_kg),  # Convert Decimal to string before storing.
        }
        try:
            self.table.put_item(Item=item) # Store the item in DynamoDB.
            logger.info(f"Successfully stored emission data for user: {user_id}")
        except Exception as e:
            logger.error(f"Error storing data for user {user_id}: {e}")
            return False
        return True

    def get_user_emissions(self, user_id):
        """Retrieves emission data for a user."""
        try:
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("userId").eq(user_id) # Query DynamoDB for user's data.
            )
            items = response.get("Items", []) # Get the items from the response.
            # Convert string Decimal values back to Decimal objects
            for item in items:
                if "carbonKg" in item:
                    item["carbonKg"] = Decimal(item["carbonKg"]) #convert string to decimal.
                if "inputParams" in item:
                    for key, value in item["inputParams"].items():
                        try:
                            item["inputParams"][key] = Decimal(value) #convert string to decimal.
                        except:
                            pass  # if not a decimal string, do nothing
                if "timestamp" in item:
                    try:
                        item["timestamp"] = datetime.fromisoformat(item["timestamp"])  # Convert ISO string to datetime.
                    except ValueError:
                        logger.warning(f"Invalid ISO format for timestamp: {item['timestamp']} for user {user_id}")

                if "timestamp_unix" in item:
                    try:
                        item["timestamp_unix"] = datetime.utcfromtimestamp(int(item["timestamp_unix"]))  # Convert Unix timestamp.
                    except ValueError:
                        logger.warning(f"Invalid Unix format for timestamp_unix: {item['timestamp_unix']} for user {user_id}") #warning log.
            return items
        except Exception as e:
            logger.error(f"Error retrieving data for user {user_id}: {e}")
            return []