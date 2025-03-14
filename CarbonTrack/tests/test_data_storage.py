# tests/test_data_storage.py
import pytest
import boto3
from decimal import Decimal
from carbon_footprint_cal.data_storage import DataStorage

@pytest.fixture
def data_storage():
    """Returns DataStorage instance using existing TestTable."""
    return DataStorage(table_name="TestTable")

def test_store_emission_data_success(data_storage):
    result = data_storage.store_emission_data("user123", "electricity", {"location": "us-ca"}, 10.0)
    assert result is True

def test_get_user_emissions_success(data_storage):
    data_storage.store_emission_data("user123", "electricity", {"location": "us-ca"}, 10.0)
    emissions = data_storage.get_user_emissions("user123")
    assert len(emissions) >= 1 # greater than or equal to, as other tests may have added data.
    found = False
    for item in emissions:
        if item.get("carbonKg") == 10.0:
            found = True
            break;
    assert found is True

def test_get_user_emissions_no_data(data_storage):
    emissions = data_storage.get_user_emissions("user456")
    assert len(emissions) == 0