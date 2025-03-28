import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from carbon_footprint_cal.data_storage.data_storage import DataStorage

class TestDataStorage(unittest.TestCase):

    @patch('boto3.resource')  # Mock the boto3 DynamoDB resource
    def test_store_emission_data_success(self, mock_boto):
        """
        Test that store_emission_data() successfully writes an item to DynamoDB.
        """
        # Create a mock table
        mock_table = MagicMock()
        mock_boto.return_value.Table.return_value = mock_table
        mock_table.put_item.return_value = {}  # Simulate successful write

        # Create instance of DataStorage
        storage = DataStorage(table_name="CarbonFootprint")

        # Store a sample record
        result = storage.store_emission_data(
            user_id="testuser",
            activity_type="electricity",
            input_params={"value": "100", "unit": "kwh"},
            carbon_kg=Decimal("15.25")
        )

        self.assertTrue(result)
        mock_table.put_item.assert_called_once()

    @patch('boto3.resource')  # Mock the entire boto3.resource (no need to patch Key directly)
    def test_get_user_emissions(self, mock_boto):
        """
        Test that get_user_emissions() correctly retrieves and parses a record from DynamoDB.
        """
        # Mock the table and query response
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
        mock_boto.return_value.Table.return_value = mock_table

        # Create instance
        storage = DataStorage(table_name="CarbonFootprint")

        # Fetch data
        items = storage.get_user_emissions("testuser")

        # Assertions
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["carbonKg"], Decimal("15.25"))
        self.assertEqual(items[0]["inputParams"]["unit"], "kwh")
