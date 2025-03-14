import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1") 
table = dynamodb.Table("supported_countries")

# List of countries to insert
countries = [
    {"country_code": "US", "country": "United States Of America"},
	{"country_code": "CA", "country": "Canada"},
	{"country_code": "AT", "country": "Austria"},
    {"country_code": "BE", "country": "Belgium"},
    {"country_code": "BG", "country": "Bulgaria"},
    {"country_code": "HR", "country": "Croatia"},
    {"country_code": "CY", "country": "Cyprus"},
    {"country_code": "CZ", "country": "Czechia"},
    {"country_code": "DK", "country": "Denmark"},
    {"country_code": "EU-27", "country": "EU-27"},
    {"country_code": "EU-27+1", "country": "EU-27+1"},
    {"country_code": "EE", "country": "Estonia"},
    {"country_code": "FI", "country": "Finland"},
    {"country_code": "FR", "country": "France"},
    {"country_code": "DE", "country": "Germany"},
    {"country_code": "GR", "country": "Greece"},
    {"country_code": "GU", "country": "Hungary"},
    {"country_code": "IE", "country": "Ireland"},
    {"country_code": "IT", "country": "Italy"},
    {"country_code": "LV", "country": "Latvia"},
    {"country_code": "LT", "country": "Lithuania"},
    {"country_code": "LU", "country": "Luxembourg"},
    {"country_code": "MT", "country": "Malta"},
    {"country_code": "NL", "country": "Netherlands"},
    {"country_code": "PL", "country": "Poland"},
    {"country_code": "PT", "country": "Portugal"},
    {"country_code": "RO", "country": "Romania"},
    {"country_code": "SK", "country": "Slovakia"},
    {"country_code": "SI", "country": "Slovenia"},
    {"country_code": "ES", "country": "Spain"},
	{"country_code": "SE", "country": "Sweden"},
    {"country_code": "GB", "country": "United Kingdom"},
]

# Insert countries into the DynamoDB table
for cntry in countries:
    table.put_item(Item=cntry)

print("Countries added successfully!")