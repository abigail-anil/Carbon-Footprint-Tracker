import unittest
from decimal import Decimal
from unittest.mock import patch
from carbon_footprint_cal.data_validation.validation import Validation

class TestValidation(unittest.TestCase):
    """
    Unit tests for the Validation class.
    These tests verify that the input validation methods handle
    valid and invalid cases correctly across different activities.
    """

    def setUp(self):
        """Setup method to create a fresh instance of Validation before each test."""
        self.validator = Validation()

    # ELECTRICITY TESTS
    @patch('carbon_footprint_cal.data_validation.validation.get_supported_countries', return_value={'IE': 'Ireland', 'US': 'United States'})
    def test_validate_electricity_params_valid(self, mock_countries):
        """Test electricity parameters with a valid country, value, and unit."""
        self.assertTrue(self.validator.validate_electricity_params("IE", 100, "kwh"))

    @patch('carbon_footprint_cal.data_validation.validation.get_supported_countries', return_value={'IE': 'Ireland'})
    def test_validate_electricity_invalid_location(self, mock_countries):
        """Test electricity input with an unsupported location."""
        with self.assertRaises(ValueError):
            self.validator.validate_electricity_params("XX", 100, "kwh")

    @patch('carbon_footprint_cal.data_validation.validation.get_supported_countries', return_value={'IE': 'Ireland'})
    def test_validate_electricity_invalid_unit(self, mock_countries):
        """Test electricity input with an invalid unit (not 'kwh' or 'mwh')."""
        with self.assertRaises(ValueError):
            self.validator.validate_electricity_params("IE", 100, "litre")

    # FLIGHT TESTS
    def test_validate_flight_params_valid(self):
        """Test flight input with 2 passengers and valid legs."""
        legs = [{"departure_airport": "DUB", "destination_airport": "LHR"}]
        self.assertTrue(self.validator.validate_flight_params(2, legs))

    def test_validate_flight_invalid_passengers(self):
        """Test flight input with zero passengers (invalid)."""
        with self.assertRaises(ValueError):
            self.validator.validate_flight_params(0, [])

    def test_validate_flight_invalid_leg_structure(self):
        """Test flight input with malformed legs missing required keys."""
        with self.assertRaises(ValueError):
            self.validator.validate_flight_params(2, [{"departure": "DUB"}])

    # SHIPPING TESTS
    def test_validate_shipping_params_valid(self):
        """Test valid shipping parameters with correct units and transport."""
        self.assertTrue(self.validator.validate_shipping_params(100, "kg", 300, "km", "truck"))

    def test_validate_shipping_invalid_weight_unit(self):
        """Test invalid weight unit for shipping."""
        with self.assertRaises(ValueError):
            self.validator.validate_shipping_params(100, "litre", 300, "km", "truck")

    def test_validate_shipping_invalid_transport_method(self):
        """Test shipping input with unsupported transport method (e.g., 'bike')."""
        with self.assertRaises(ValueError):
            self.validator.validate_shipping_params(100, "kg", 300, "km", "bike")

    # FUEL COMBUSTION TESTS
    def test_validate_fuel_combustion_params_valid(self):
        """Test valid fuel combustion value."""
        self.assertTrue(self.validator.validate_fuel_combustion_params(10))

    def test_validate_fuel_combustion_invalid_value(self):
        """Test invalid fuel combustion value (negative or zero)."""
        with self.assertRaises(ValueError):
            self.validator.validate_fuel_combustion_params(-5)

    # VEHICLE TESTS
    def test_validate_vehicle_params_valid(self):
        """Test valid vehicle emission input."""
        self.assertTrue(self.validator.validate_vehicle_params(100, "km", "model123"))

    def test_validate_vehicle_params_invalid_distance_unit(self):
        """Test vehicle emission with an invalid distance unit."""
        with self.assertRaises(ValueError):
            self.validator.validate_vehicle_params(100, "litres", "model123")

    def test_validate_vehicle_params_missing_model_id(self):
        """Test vehicle emission with missing vehicle model ID."""
        with self.assertRaises(ValueError):
            self.validator.validate_vehicle_params(100, "km", "")
