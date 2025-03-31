import boto3
import os

# ---------------------- S3 BUCKET CREATION ----------------------
def create_s3_bucket(bucket_name, region="us-east-1"):
    """Creates an S3 bucket."""
    s3 = boto3.client("s3", region_name=region)
    try:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": region})
        print(f"S3 bucket '{bucket_name}' created successfully in {region}.")
    except Exception as e:
        print(f"Error creating S3 bucket: {e}")

# ---------------------- DYNAMODB TABLE 1: CarbonFootprint ----------------------
def create_dynamodb_table1(table_name, region_name="us-east-1"):
    """Creates the DynamoDB table."""
    dynamodb = boto3.resource("dynamodb", region_name=region_name)
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "userId", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "timestamp", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")

# ---------------------- SNS TOPIC CREATION ----------------------
def create_sns_topic(topic_name, region="us-east-1"):
    """Creates an SNS topic."""
    sns = boto3.client("sns", region_name=region)
    try:
        response = sns.create_topic(Name=topic_name)
        topic_arn = response["TopicArn"]
        print(f"SNS topic '{topic_name}' created successfully in {region}. ARN: {topic_arn}")
        return topic_arn
    except Exception as e:
        print(f"Error creating SNS topic: {e}")
        return None

# ---------------------- DYNAMODB TABLE 2: supported_countries ----------------------
def create_dynamodb_table2(table_name, region_name="us-east-1"):
    """Creates the DynamoDB table."""
    dynamodb = boto3.resource("dynamodb", region_name=region_name)
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "country_code", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "country", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "country_code", "AttributeType": "S"},
                {"AttributeName": "country", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
        
# ---------------------- DYNAMODB TABLE 3: fuel_sources ----------------------
def create_dynamodb_table3(table_name, region_name="us-east-1"):
    """Creates the DynamoDB table for fuel sources and their corresponding units."""
    dynamodb = boto3.resource("dynamodb", region_name=region_name)
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "fuel_source_id", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "unit", "KeyType": "RANGE"},  # Sort key (unit for each fuel source)
            ],
            AttributeDefinitions=[
                {"AttributeName": "fuel_source_id", "AttributeType": "S"},  # String type for fuel source ID
                {"AttributeName": "unit", "AttributeType": "S"},  # String type for unit
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
        
# ---------------------- DYNAMODB TABLE 4: user_settings ----------------------
def create_dynamodb_table4(table_name, region_name="us-east-1"):
    """Creates the DynamoDB table."""
    dynamodb = boto3.resource("dynamodb", region_name=region_name)
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "userId", "KeyType": "HASH"},  # Partition key
                #{"AttributeName": "timestamp", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "userId", "AttributeType": "S"},
                #{"AttributeName": "timestamp", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")

# ---------------------- DYNAMODB TABLE 5: VehicleModels ----------------------
def create_dynamodb_table5(table_name, region_name="us-east-1"):
    """Creates the DynamoDB table."""
    dynamodb = boto3.resource("dynamodb", region_name=region_name)
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'model_id',
                    'KeyType': 'HASH'  # Partition key
            },],
            AttributeDefinitions=[
                {'AttributeName': 'model_id',
                    'AttributeType': 'S'  # String
                    },
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")


# ---------------------- MAIN EXECUTION ----------------------
if __name__ == "__main__":
    create_s3_bucket("carbon-tracker-reports", "us-east-1")
    create_dynamodb_table1("CarbonFootprint", "us-east-1")
    create_sns_topic("carbon-tracker-sns", "us-east-1")
    create_dynamodb_table2("supported_countries", "us-east-1")
    create_dynamodb_table3("fuel_sources", "us-east-1")
    create_dynamodb_table4("user_settings", "us-east-1")
    create_dynamodb_table5("VehicleModels", "us-east-1")
    
    ''' bucket_name = os.environ.get("S3_BUCKET_NAME")
    table_name = os.environ.get("DYNAMODB_TABLE_NAME")
    topic_name = os.environ.get("SNS_TOPIC_NAME")
    region = os.environ.get("AWS_REGION", "us-east-1") #use us-east-1 if no region is given.

    if not bucket_name or not table_name:
        print("Please set S3_BUCKET_NAME, SNS_TOPIC_NAME and DYNAMODB_TABLE_NAME environment variables.")
    else:
        create_s3_bucket(bucket_name, region)
        create_dynamodb_table(table_name, region)
        create_sns_topic(topic_name, region)'''
        
        
# ----------------------  TABLE MODIFICATION LOGIC ----------------------
dynamodb = boto3.client('dynamodb')

try:
    # Get the current table description
    table_description = dynamodb.describe_table(TableName='user_settings')
    table_details = table_description['Table']

    # Extract ProvisionedThroughput or BillingMode
    if 'ProvisionedThroughput' in table_details:
        throughput = table_details['ProvisionedThroughput']
        update_params = {
            'TableName': 'user_settings',
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'electricity_threshold', 'AttributeType': 'N'},
                {'AttributeName': 'flight_threshold', 'AttributeType': 'N'},
                {'AttributeName': 'shipping_threshold', 'AttributeType': 'N'},
                {'AttributeName': 'emission_check_frequency', 'AttributeType': 'S'}
            ],
            'ProvisionedThroughput': throughput,
        }
    print("Table updated successfully")
except Exception as e:
    print(f"Error updating table: {e}")