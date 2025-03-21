# Carbon Emissions Library

**Description:**

This library provides tools for calculating and tracking carbon emissions, integrating with the Carbon Interface API for up-to-date emission factors, and utilizing AWS DynamoDB for data storage. It's designed to be used both in general Python environments and seamlessly within AWS Lambda functions.

## Features

* **Carbon Emission Calculation:** Calculates carbon emissions for various activity types (electricity, flight, shipping, fuel combustion and vehicles) using the Carbon Interface API.
* **AWS Integration:** Integrates with AWS DynamoDB for persistent data storage.
* **Data Storage:** Stores carbon emission data in a DynamoDB table.
* **Data Validation:** Ensures data integrity through validation of required fields and data types.
* **Modular Design:** Organized into reusable modules for calculations, data storage, and validation.
* **Environment Variable Configuration:** Designed to be configured via environment variables.

## Installation

```bash
pip install carbon_footprint_cal
```

## Usage
This library uses carbon interface API to fetch the emissions factor. An API key (CARBON_INTERFACE_API_KEY)is required to fetch the emission factor which can be set as an environment variable.

### Calculations


```python

from carbon_footprint_cal.emissions.calculations import Calculations
import os

carbon_interface_api_key = os.environ.get("CARBON_INTERFACE_API_KEY")
carbon_calculator = Calculations(carbon_interface_api_key)

# Electricity Calculation
electricity_value = 100  # kWh or mwh
location = "US-CA"  # Example: "country-state"
electricity_emission = carbon_calculator.calculate_electricity_emission({"value": electricity_value, "location": location, "unit": "kwh"})
print(f"Calculated electricity emission: {electricity_emission} kg CO2e")

# Flight Calculation
passengers = 2
legs = [{"departure_airport": "sfo", "destination_airport": "yyz"}, {"departure_airport": "yyz", "destination_airport": "sfo"}]
flight_emission = carbon_calculator.calculate_flight_emission(passengers, legs)
print(f"Calculated flight emission: {flight_emission} kg CO2e")

# Shipping Calculation
weight_value = 200
weight_unit = "g"
distance_value = 2000
distance_unit = "km"
transport_method = "truck"
shipping_emission = carbon_calculator.calculate_shipping_emission(weight_value, weight_unit, distance_value, distance_unit, transport_method)
print(f"Calculated shipping emission: {shipping_emission} kg CO2e")

# Fuel Combustion Calculation
fuel_source_type = "natural_gas" #Example
fuel_source_unit = "mwh" #Example
fuel_source_value = 100 #Example
fuel_emission = carbon_calculator.calculate_fuel_combustion_emission(fuel_source_type, fuel_source_unit, fuel_source_value)
print(f"Calculated fuel combustion emission: {fuel_emission} kg CO2e")

# Vehicle Calculation
distance_value = 100 #Example
distance_unit = "km" #Example
vehicle_model_id = "72c68172-aa91-4221-a084-5731efc79c68" #Example
vehicle_emission = carbon_calculator.calculate_vehicle_emission(distance_value, distance_unit, vehicle_model_id)
print(f"Calculated vehicle emission: {vehicle_emission} kg CO2e")
```


### Data Storage
```python

from carbon_footprint_cal.data_storage import DataStorage
import os
from decimal import Decimal

data_storage = DataStorage(table_name="TestTable") #Ensure to create the table beforehand.

user_id = "user123"
activity_type = "electricity"
input_params = {"location": "US-CA", "value": Decimal("100"), "unit": "kwh"}
carbon_kg = Decimal("50")

data_storage.store_emission_data(user_id, activity_type, input_params, carbon_kg)
user_data = data_storage.get_user_emissions(user_id)
print(user_data)
```

### Data Validation
```python

from carbon_footprint_cal.validation import Validation

validation = Validation()

# Example: Electricity validation
try:
    validation.validate_electricity_params("US-CA", 100, "kwh")
    print("Electricity data is valid")
except ValueError as e:
    print(f"Electricity data is invalid: {e}")

# Example: Flight validation
try:
    legs = [{"departure_airport": "sfo", "destination_airport": "yyz"}]
    validation.validate_flight_params(2, legs)
    print("Flight data is valid")
except ValueError as e:
    print(f"Flight data is invalid: {e}")

# Example: Shipping validation
try:
    validation.validate_shipping_params(200, "g", 2000, "km", "truck")
    print("Shipping data is valid")
except ValueError as e:
    print(f"Shipping data is invalid: {e}")
    
# Example: Fuel Combustion validation
try:
    validation.validate_fuel_combustion_params("natural_gas", "mwh", 100)
    print("Fuel Combustion data is valid")
except ValueError as e:
    print(f"Fuel Combustion data is invalid: {e}")

# Example: Vehicle validation
try:
    validation.validate_vehicle_params(100, "km", "72c68172-aa91-4221-a084-5731efc79c68")
    print("Vehicle data is valid")
except ValueError as e:
    print(f"Vehicle data is invalid: {e}")
```
    
### Data Storage

The library uses AWS DynamoDB for persistent storage.

Table Name: The DynamoDB table name is configurable via the DYNAMODB_TABLE_NAME environment variable or defaults to "CarbonFootprint".
Usage: The data_storage module provides methods to store and retrieve data.

### Data Validation
The library includes data validation to ensure data integrity.

Validation Rules: Checks for required fields (e.g., location, departure_airport, destination_airport, etc) and ensures that values are of the correct type (e.g., non-negative numbers).
Refer https://docs.carboninterface.com/ for the rules to pass data to Carbon Interface API.
Error Handling: Returns an error message if validation fails.
Usage: The validation module provides a method to validate data.

## Dependencies
* requests
* boto3
* os
* logging


## DynamoDB Data

The fuel combustion and vehicle calculations rely on data stored in DynamoDB tables. Ensure that you have the following tables set up:

* `fuel_sources`: Contains fuel source types and their corresponding API names.
* `VehicleModels`: Contains vehicle makes and models.

## License
This project is licensed under the MIT License. See the LICENSE file for details.