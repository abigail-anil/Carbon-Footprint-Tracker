import pytest
from carbon_footprint_cal.validation import Validation

@pytest.fixture
def validator():
    return Validation()

def test_validate_electricity_params_success(validator):
    assert validator.validate_electricity_params("us-ca", 100, "kwh") is True

def test_validate_electricity_params_invalid_location(validator):
    with pytest.raises(ValueError):
        validator.validate_electricity_params("invalid", 100, "kwh")

def test_validate_flight_params_success(validator):
    legs = [{"departure_airport": "sfo", "destination_airport": "yyz"}]
    assert validator.validate_flight_params(1, legs) is True

def test_validate_flight_params_invalid_legs(validator):
    with pytest.raises(ValueError):
        validator.validate_flight_params(1, "invalid")

def test_validate_shipping_params_success(validator):
    assert validator.validate_shipping_params(100, "kg", 1000, "km", "truck") is True

def test_validate_shipping_params_invalid_weight_unit(validator):
    with pytest.raises(ValueError):
        validator.validate_shipping_params(100, "invalid", 1000, "km", "truck")