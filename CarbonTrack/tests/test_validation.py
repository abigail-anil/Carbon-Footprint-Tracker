import unittest
from decimal import Decimal
import boto3
boto3.setup_default_session(region_name='us-east-1')
from carbon_footprint_cal.data_validation.validation import Validation

class TestValidation(unittest.TestCase):
    def setUp(self):
        self.validator = Validation()

    def test_validate_electricity_params_valid(self):
        self.assertTrue(self.validator.validate_electricity_params("IE", 100, "kwh"))

    def test_validate_electricity_invalid_location(self):
        with self.assertRaises(ValueError):
            self.validator.validate_electricity_params("XX", 100, "kwh")

    def test_validate_electricity_invalid_unit(self):
        with self.assertRaises(ValueError):
            self.validator.validate_electricity_params("IE", 100, "litre")

    def test_validate_flight_params_valid(self):
        legs = [{"departure_airport": "DUB", "destination_airport": "LHR"}]
        self.assertTrue(self.validator.validate_flight_params(2, legs))

    def test_validate_flight_invalid_passengers(self):
        with self.assertRaises(ValueError):
            self.validator.validate_flight_params(0, [])

    def test_validate_shipping_params_valid(self):
        self.assertTrue(self.validator.validate_shipping_params(100, "kg", 300, "km", "truck"))

    def test_validate_fuel_combustion_params_valid(self):
        self.assertTrue(self.validator.validate_fuel_combustion_params(10))

    def test_validate_vehicle_params_valid(self):
        self.assertTrue(self.validator.validate_vehicle_params(100, "km", "model123"))
