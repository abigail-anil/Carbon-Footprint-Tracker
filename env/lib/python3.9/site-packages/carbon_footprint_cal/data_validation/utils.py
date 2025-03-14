import os
import boto3

def get_supported_countries(table_name=None):
    # Use environment variable or default table name
    table_name = table_name or os.getenv('DYNAMODB_COUNTRIES', 'supported_countries')

    dynamodb = boto3.client('dynamodb')
    response = dynamodb.scan(TableName=table_name)

    countries = {}
    for item in response.get('Items', []):
        country_code = item['country_code']['S']
        country_name = item['country']['S']
        countries[country_code] = country_name

    return countries
