import unittest
from decimal import Decimal
from carbon_footprint_cal.data_validation.validation import Validation

class TestValidation(unittest.TestCase):
    """
    Unit tests for the Validation class.
    Each test ensures that input validation logic behaves as expected.
    """

    def setUp(self):
        """Initialize the Validation instance before each test."""
        self.validator = Validation()

    def test_validate_electricity_params_valid(self):
        """Test valid electricity input (country code, value, unit)."""
        self.assertTrue(self.validator.validate_electricity_params("IE", 100, "kwh"))

    def test_validate_electricity_invalid_location(self):
        """Test electricity input with unsupported location."""
        with self.assertRaises(ValueError):
            self.validator.validate_electricity_params("XX", 100, "kwh")

    def test_validate_electricity_invalid_unit(self):
        """Test electricity input with invalid unit."""
        with self.assertRaises(ValueError):
            self.validator.validate_electricity_params("IE", 100, "litre")

    def test_validate_flight_params_valid(self):
        """Test valid flight parameters."""
        legs = [{"departure_airport": "DUB", "destination_airport": "LHR"}]
        self.assertTrue(self.validator.validate_flight_params(2, legs))

    def test_validate_flight_invalid_passengers(self):
        """Test flight validation with 0 passengers."""
        with self.assertRaises(ValueError):
            self.validator.validate_flight_params(0, [])

    def test_validate_shipping_params_valid(self):
        """Test valid shipping parameters."""
        self.assertTrue(self.validator.validate_shipping_params(100, "kg", 300, "km", "truck"))

    def test_validate_shipping_invalid_weight_unit(self):
        """Test shipping validation with invalid weight unit."""
        with self.assertRaises(ValueError):
            self.validator.validate_shipping_params(100, "litre", 300, "km", "truck")

    def test_validate_fuel_combustion_params_valid(self):
        """Test valid fuel combustion parameters."""
        self.assertTrue(self.validator.validate_fuel_combustion_params(10))

    def test_validate_fuel_combustion_invalid_value(self):
        """Test fuel combustion validation with non-positive value."""
        with self.assertRaises(ValueError):
            self.validator.validate_fuel_combustion_params(-5)

    def test_validate_vehicle_params_valid(self):
        """Test valid vehicle parameters."""
        self.assertTrue(self.validator.validate_vehicle_params(100, "km", "model123"))

    def test_validate_vehicle_params_invalid_distance_unit(self):
        """Test vehicle validation with invalid distance unit."""
        with self.assertRaises(ValueError):
            self.validator.validate_vehicle_params(100, "litres", "model123")

    def test_validate_vehicle_params_missing_model_id(self):
        """Test vehicle validation with missing model ID."""
        with self.assertRaises(ValueError):
            self.validator.validate_vehicle_params(100, "km", "")
