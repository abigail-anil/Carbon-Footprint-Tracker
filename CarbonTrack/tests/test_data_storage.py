import unittest
from unittest.mock import patch, MagicMock
import boto3
boto3.setup_default_session(region_name='us-east-1')
from carbon_footprint_cal.data_storage.data_storage import DataStorage
from decimal import Decimal

class TestDataStorage(unittest.TestCase):

    @patch('boto3.resource')  # Mock the boto3 DynamoDB resource
    def test_store_emission_data_success(self, mock_resource):
        """
        Test that store_emission_data() successfully writes an item to DynamoDB.
        """
        # Create a mock table and mock the resource to return it
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        mock_table.put_item.return_value = {}  # Simulate successful write

        # Instantiate the DataStorage class
        storage = DataStorage(table_name="CarbonFootprint")

        # Attempt to store a sample emission record
        success = storage.store_emission_data(
            user_id="testuser",
            activity_type="electricity",
            input_params={"value": "100", "unit": "kwh"},
            carbon_kg=Decimal("15.25")
        )

        # Assert that the function returns success and actually called put_item
        self.assertTrue(success)
        mock_table.put_item.assert_called_once()


    @patch('boto3.resource') # Mock the boto3 DynamoDB resource
    @patch('boto3.dynamodb.conditions.Key')
    def test_get_user_emissions(self, mock_key, mock_resource):
        """
        Test that get_user_emissions() correctly retrieves and parses a record from DynamoDB.
        """
        # Set up a mock DynamoDB table with pre-filled query return data
        mock_table = MagicMock()
        mock_table.query.return_value = {
            "Items": [{
                "userId": "testuser",
                "timestamp": "2024-01-01T00:00:00",
                "activityType": "electricity",
                "carbonKg": "15.25",
                "inputParams": {"value": "100", "unit": "kwh"}
            }]
        }

        # Mock the resource to return this table
        mock_resource.return_value.Table.return_value = mock_table

        # Instantiate the DataStorage class
        storage = DataStorage(table_name="CarbonFootprint")

        # Fetch emissions for test user
        items = storage.get_user_emissions("testuser")

        # Assert the data was retrieved and converted correctly
        self.assertEqual(len(items), 1)  # One record
        self.assertEqual(items[0]["carbonKg"], Decimal("15.25"))  # String converted to Decimal
        self.assertEqual(items[0]["inputParams"]["unit"], "kwh")  # Input params remain intact
