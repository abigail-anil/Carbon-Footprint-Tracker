import boto3
import json

def create_secret(secret_name, api_key, region_name="us-east-1"):
    """Creates a secret in AWS Secrets Manager and stores the API key."""

    secrets_client = boto3.client('secretsmanager', region_name=region_name)

    try:
        # Create the secret with the API key stored as a JSON string
        response = secrets_client.create_secret(
            Name=secret_name,
            SecretString=json.dumps({'api_key': api_key})
        )
        print(f"Secret '{secret_name}' created successfully. ARN: {response['ARN']}")
        return response['ARN']

    except secrets_client.exceptions.ResourceExistsException:
        print(f"Secret '{secret_name}' already exists. Updating its value.")
        response = secrets_client.put_secret_value(
            SecretId=secret_name,
            SecretString=json.dumps({'api_key': api_key})
        )
        print(f"Secret '{secret_name}' value updated successfully.")
        return secrets_client.describe_secret(SecretId=secret_name)['ARN']

    except Exception as e:
        print(f"Error creating or updating secret: {e}")
        return None

if __name__ == "__main__":
    secret_name = "CARBON_INTERFACE_API_KEY"
    api_key = "ly0WhDdNgcDOHFmQK4Fw"  # Replace with your actual API key
    region = "us-east-1"  # Change if needed

    create_secret(secret_name, api_key, region)