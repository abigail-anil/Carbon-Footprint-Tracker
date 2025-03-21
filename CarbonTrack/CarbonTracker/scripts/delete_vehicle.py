import boto3

# Initialize the DynamoDB resource
dynamodb = boto3.resource("dynamodb")
table_name = "VehicleModels"
table = dynamodb.Table(table_name)

def delete_all_items():
    scan = table.scan()
    with table.batch_writer() as batch:
        for item in scan["Items"]:
            batch.delete_item(Key={"model_id": item["model_id"]})  # Add sort key if applicable
    
    print("All items deleted successfully.")

delete_all_items()