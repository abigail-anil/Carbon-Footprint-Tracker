import pytest
import os
from carbon_footprint_cal.emissions.calculations import Calculations
import requests_mock

API_KEY = "ly0WhDdNgcDOHFmQK4Fw"  # Use a test API key

@pytest.fixture
def calculator():
    return Calculations(API_KEY)

def test_calculate_electricity_emission_success(calculator):
    with requests_mock.Mocker() as m:
        m.post(
            "https://www.carboninterface.com/api/v1/estimates",
            json={"data": {"attributes": {"carbon_kg": 10.0}}},
        )
        emission = calculator.calculate_electricity_emission(100, "us-ca", "kwh")
        assert emission == 10.0

def test_calculate_electricity_emission_api_error(calculator):
    with requests_mock.Mocker() as m:
        m.post(
            "https://www.carboninterface.com/api/v1/estimates",
            status_code=500,
        )
        emission = calculator.calculate_electricity_emission(100, "us-ca", "kwh")
        assert emission is None

def test_calculate_flight_emission_success(calculator):
    with requests_mock.Mocker() as m:
        m.post(
            "https://www.carboninterface.com/api/v1/estimates",
            json={"data": {"attributes": {"carbon_kg": 20.0}}},
        )
        legs = [{"departure_airport": "sfo", "destination_airport": "yyz"}]
        emission = calculator.calculate_flight_emission(1, legs)
        assert emission == 20.0

def test_calculate_shipping_emission_success(calculator):
    with requests_mock.Mocker() as m:
        m.post(
            "https://www.carboninterface.com/api/v1/estimates",
            json={"data": {"attributes": {"carbon_kg": 30.0}}},
        )
        emission = calculator.calculate_shipping_emission(100, "kg", 1000, "km", "truck")
        assert emission == 30.0