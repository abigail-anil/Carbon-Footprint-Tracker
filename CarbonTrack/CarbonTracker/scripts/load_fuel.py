import boto3

def insert_fuel_source_data(table_name, fuel_source_id, unit, fuel_source_type, api_name):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    
    # Insert the data
    table.put_item(
        Item={
            'fuel_source_id': fuel_source_id,  # Partition key
            'unit': unit,                      # Sort key
            'fuel_source_type': fuel_source_type,  # Additional attribute
            'api_name': api_name,                # Additional attribute
        }
    )
    print("Item inserted successfully.")

#inserting records
insert_fuel_source_data("fuel_sources", "1", "short_ton", "Bituminous Coal", "bit")
insert_fuel_source_data("fuel_sources", "1", "btu", "Bituminous Coal", "bit")
insert_fuel_source_data("fuel_sources", "2", "gallon", "Home Heating and Diesel Fuel(Distillate)", "dfo")
insert_fuel_source_data("fuel_sources", "2", "btu", "Home Heating and Diesel Fuel(Distillate)", "dfo")
insert_fuel_source_data("fuel_sources", "3", "gallon", "Kerosene", "ker")
insert_fuel_source_data("fuel_sources", "3", "btu", "Kerosene", "ker")
insert_fuel_source_data("fuel_sources", "4", "short_ton", "Municipal Solid Waste", "msw")
insert_fuel_source_data("fuel_sources", "4", "btu", "Municipal Solid Waste", "msw")
insert_fuel_source_data("fuel_sources", "5", "thousand_cubic_feet", "Natural Gas", "ng")
insert_fuel_source_data("fuel_sources", "5", "btu", "Natural Gas", "ng")