import pytest
import boto3
from carbon_footprint_cal.emissions.calculations import Calculations
from carbon_footprint_cal.data_storage import DataStorage
from carbon_footprint_cal.validation import Validation
import requests_mock

API_KEY = "ly0WhDdNgcDOHFmQK4Fw"

@pytest.fixture
def data_storage():
    """Returns DataStorage instance using existing TestTable."""
    return DataStorage(table_name="TestTable")
 
@pytest.fixture
def calculator():
    return Calculations(API_KEY)

@pytest.fixture
def validator():
    return Validation()

def test_integration_electricity(calculator, data_storage, validator):
    with requests_mock.Mocker() as m:
        m.post(
            "https://www.carboninterface.com/api/v1/estimates",
            json={"data": {"attributes": {"carbon_kg": 10.0}}},
        )
        location = "us-ca"
        value = 100
        unit = "kwh"
        try:
            validator.validate_electricity_params(location, value, unit)
            emission = calculator.calculate_electricity_emission(value, location, unit)
            if emission is not None:
                user_id = "user123"
                input_params = {"location": location, "value": value, "unit": unit}
                data_storage.store_emission_data(user_id, "electricity", input_params, emission)
                emissions = data_storage.get_user_emissions(user_id)
                assert len(emissions) == 1
                assert emissions[0]["carbonKg"] == 10.0
                assert emissions[0]["activityType"] == "electricity"
        except ValueError as e:
            pytest.fail(f"Validation failed: {e}")

def test_integration_flight(calculator, data_storage, validator):
    with requests_mock.Mocker() as m:
        m.post(
            "https://www.carboninterface.com/api/v1/estimates",
            json={"data": {"attributes": {"carbon_kg": 20.0}}},
        )
        passengers = 2
        legs = [{"departure_airport": "sfo", "destination_airport": "yyz"}]
        try:
            validator.validate_flight_params(passengers, legs)
            emission = calculator.calculate_flight_emission(passengers, legs)
            if emission is not None:
                user_id = "user456"
                input_params = {"passengers": passengers, "legs": legs}
                data_storage.store_emission_data(user_id, "flight", input_params, emission)
                emissions = data_storage.get_user_emissions(user_id)
                assert len(emissions) == 1
                assert emissions[0]["carbonKg"] == 20.0
                assert emissions[0]["activityType"] == "flight"
        except ValueError as e:
            pytest.fail(f"Validation failed: {e}")

def test_integration_shipping(calculator, data_storage, validator):
    with requests_mock.Mocker() as m:
        m.post(
            "https://www.carboninterface.com/api/v1/estimates",
            json={"data": {"attributes": {"carbon_kg": 30.0}}},
        )
        weight_value = 100
        weight_unit = "kg"
        distance_value = 1000
        distance_unit = "km"
        transport_method = "truck"
        try:
            validator.validate_shipping_params(weight_value, weight_unit, distance_value, distance_unit, transport_method)
            emission = calculator.calculate_shipping_emission(weight_value, weight_unit, distance_value, distance_unit, transport_method)
            if emission is not None:
                user_id = "user789"
                input_params = {"weight_value": weight_value, "weight_unit": weight_unit, "distance_value": distance_value, "distance_unit": distance_unit, "transport_method": transport_method}
                data_storage.store_emission_data(user_id, "shipping", input_params, emission)
                emissions = data_storage.get_user_emissions(user_id)
                assert len(emissions) == 1
                assert emissions[0]["carbonKg"] == 30.0
                assert emissions[0]["activityType"] == "shipping"
        except ValueError as e:
            pytest.fail(f"Validation failed: {e}")   