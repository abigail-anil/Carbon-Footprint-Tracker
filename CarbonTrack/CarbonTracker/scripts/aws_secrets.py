import boto3
import json

def create_secret(secret_name, api_key, region_name="us-east-1"):
    """Creates a secret in AWS Secrets Manager and stores the API key."""

    secrets_client = boto3.client('secretsmanager', region_name=region_name)  # Initialize the Secrets Manager client for the specified region

    try:
        # Create the secret with the API key stored as a JSON string
        response = secrets_client.create_secret(
            Name=secret_name,
            SecretString=json.dumps({'api_key': api_key})
        )
        print(f"Secret '{secret_name}' created successfully. ARN: {response['ARN']}")
        return response['ARN']

    except secrets_client.exceptions.ResourceExistsException:
        # If the secret already exists, update its value with the new API key
        print(f"Secret '{secret_name}' already exists. Updating its value.")
        response = secrets_client.put_secret_value(
            SecretId=secret_name,
            SecretString=json.dumps({'api_key': api_key})
        )
        print(f"Secret '{secret_name}' value updated successfully.")
        # Retrieve and return the ARN of the existing secret
        return secrets_client.describe_secret(SecretId=secret_name)['ARN']

    except Exception as e:
        # Handle any other exceptions that might occur
        print(f"Error creating or updating secret: {e}")
        return None

if __name__ == "__main__":
    # Define the name of the secret and the API key to store
    secret_name = "CARBON_INTERFACE_API_KEY"
    api_key = "ly0WhDdNgcDOHFmQK4Fw"  
    region = "us-east-1" 

    create_secret(secret_name, api_key, region) # Call the function to create or update the secret