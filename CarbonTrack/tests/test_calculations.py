import unittest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from carbon_footprint_cal.emissions.calculations import Calculations

class TestCalculations(unittest.TestCase):
    def setUp(self):
        self.api_key = "dummy_key"
        self.calc = Calculations(self.api_key)

    @patch("carbon_footprint_cal.emissions.calculations.requests.post")
    def test_calculate_electricity_emission(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"attributes": {"carbon_kg": "20.5"}}
        }

        data = {"value": 100, "unit": "kwh", "location": "IE"}
        result = self.calc.calculate_electricity_emission(data)
        self.assertEqual(result, Decimal("20.5"))

    @patch("carbon_footprint_cal.emissions.calculations.requests.post")
    def test_calculate_flight_emission(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"attributes": {"carbon_kg": "1000.0"}}
        }

        legs = [{"departure_airport": "DUB", "destination_airport": "LHR"}]
        result = self.calc.calculate_flight_emission(2, legs)
        self.assertEqual(result, Decimal("1000.0"))

    @patch("carbon_footprint_cal.emissions.calculations.requests.post")
    def test_calculate_shipping_emission(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"attributes": {"carbon_kg": "150.0"}}
        }

        result = self.calc.calculate_shipping_emission(100, "kg", 300, "km", "truck")
        self.assertEqual(result, Decimal("150.0"))

    @patch("carbon_footprint_cal.emissions.calculations.Calculations.get_api_name_by_fuel_type")
    @patch("carbon_footprint_cal.emissions.calculations.requests.post")
    def test_calculate_fuel_combustion_emission(self, mock_post, mock_get_name):
        mock_get_name.return_value = "home_heating_oil"
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"attributes": {"carbon_kg": "80.0"}}
        }

        result = self.calc.calculate_fuel_combustion_emission("Heating Oil", "gallon", 50)
        self.assertEqual(result, Decimal("80.0"))

    @patch("carbon_footprint_cal.emissions.calculations.requests.post")
    def test_calculate_vehicle_emission(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"attributes": {"carbon_kg": "12.2"}}
        }

        result = self.calc.calculate_vehicle_emission(100, "km", "model123")
        self.assertEqual(result, Decimal("12.2"))

if __name__ == '__main__':
    unittest.main()
