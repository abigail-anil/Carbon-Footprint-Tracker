import boto3
import base64
from io import BytesIO
import logging
from botocore.exceptions import ClientError
import os
from django.conf import settings 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_supported_countries():
    """Retrieves supported countries from DynamoDB."""
    logging.info("Starting retrieval of supported countries from DynamoDB.")

    try:
        dynamodb = boto3.client('dynamodb')
        logging.debug("DynamoDB client created.")

        # Scanning the DynamoDB table 'supported_countries' to retrieve all items.
        response = dynamodb.scan(TableName='supported_countries')
        logging.debug(f"DynamoDB scan response: {response}")

        # Initializing an empty dictionary to store country codes and names.
        countries = {}

        # Iterating through the items returned by the DynamoDB scan.
        for item in response.get('Items', []):
            # Extracting the country code and name from the item.
            country_code = item['country_code']['S']  
            country_name = item['country']['S']
            # Adding the country code and name to the dictionary.
            countries[country_code] = country_name

        logging.info(f"Successfully retrieved {len(countries)} supported countries.")
        return countries

    except Exception as e:
        # Logging any exceptions that occur during the process.
        logging.error(f"Error retrieving supported countries from DynamoDB: {e}")
        return {}  # Returning an empty dictionary in case of an error.

def subscribe_email_to_sns_topic(topic_arn, email_address, region="us-east-1"):
    """Subscribes an email address to an existing SNS topic."""
    logging.info(f"Subscribing email {email_address} to SNS topic {topic_arn}.")

    try:
        
        sns = boto3.client('sns', region_name=region)
        logging.debug(f"SNS client created for region: {region}")

        # Subscribe the email address to the SNS topic.
        response = sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email_address
        )
        # Extract the Subscription ARN from the response.
        subscription_arn = response['SubscriptionArn']
        logging.info(f"Email {email_address} successfully subscribed. Subscription ARN: {subscription_arn}")
        return subscription_arn

    except Exception as e:
        # Log any exceptions that occur during the subscription process.
        logging.error(f"Error subscribing email {email_address} to SNS topic {topic_arn}: {e}")
        return None
        
        
def unsubscribe_email_from_sns_topic(topic_arn, email_address, region="us-east-1"):
    """Unsubscribes an email address from an SNS topic."""
    logging.info(f"Unsubscribing email {email_address} from SNS topic {topic_arn}.")

    try:
        sns = boto3.client('sns', region_name=region)
        logging.debug(f"SNS client created for region: {region}")

        # List subscriptions for the given topic ARN.
        subscriptions_response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        subscriptions = subscriptions_response['Subscriptions']

        # Find the subscription with the matching email address.
        subscription_arn_to_unsubscribe = None
        for subscription in subscriptions:
            if subscription['Endpoint'] == email_address and subscription['Protocol'] == 'email':
                subscription_arn_to_unsubscribe = subscription['SubscriptionArn']
                break

        if subscription_arn_to_unsubscribe:
            # Unsubscribe the email address from the SNS topic.
            response = sns.unsubscribe(SubscriptionArn=subscription_arn_to_unsubscribe)
            logging.info(f"Email {email_address} successfully unsubscribed. Subscription ARN: {subscription_arn_to_unsubscribe}")
            return True
        else:
            logging.warning(f"Email {email_address} not found as a subscriber to SNS topic {topic_arn}.")
            return False

    except Exception as e:
        # Log any exceptions that occur during the unsubscription process.
        logging.error(f"Error unsubscribing email {email_address} from SNS topic {topic_arn}: {e}")
        return False

'''Upload files to s3 bucket'''        
# The S3 bucket name is accessed from Django settings which is loaded from a .env file
S3_BUCKET_NAME = settings.S3_BUCKET_NAME 

# Create an S3 client using boto3
s3_client = boto3.client('s3')

def upload_chart_to_s3(user_id, chart_image_base64, chart_name):
    """Upload a chart image (base64 encoded) to an S3 bucket."""
    
    logging.info(f"Starting upload of {chart_name}.png for user {user_id} to S3.")

    try:
        # Decode the base64 encoded image data.
        image_data = base64.b64decode(chart_image_base64)
        logging.debug(f"Image data decoded for {chart_name}.png.")

        # Construct the S3 object key, including the user's folder.
        object_key = f"{user_id}/{chart_name}.png"
        logging.debug(f"S3 object key: {object_key}")

        # Upload the image data to S3 using upload_fileobj.
        s3_client.upload_fileobj(BytesIO(image_data), S3_BUCKET_NAME, object_key)
        logging.info(f"Successfully uploaded {chart_name}.png to S3.")

        # Construct and return the S3 URL of the uploaded chart.
        s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{object_key}"
        logging.debug(f"S3 URL: {s3_url}")
        return s3_url

    except ClientError as e:
        # Log any S3 ClientError that occurs during the upload.
        logging.error(f"Error uploading {chart_name}.png to S3: {e}")
        return None
    except base64.binascii.Error as e:
        logging.error(f"Error decoding base64 data for {chart_name}.png: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while uploading {chart_name}.png: {e}")
        return None