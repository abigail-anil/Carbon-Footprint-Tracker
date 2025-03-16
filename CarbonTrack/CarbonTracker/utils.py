# CarbonTracker/utils.py
import boto3
import os



def get_supported_countries():
    # Create a DynamoDB client
    dynamodb = boto3.client('dynamodb')

    # Get items from DynamoDB table (replace with your actual table name)
    response = dynamodb.scan(TableName='supported_countries')

    countries = {}
    for item in response.get('Items', []):
        country_code = item['country_code']['S']
        country_name = item['country']['S']
        countries[country_code] = country_name

    return countries


def subscribe_email_to_sns_topic(topic_arn, email_address, region="us-east-1"):
    """Subscribes an email address to an existing SNS topic."""

    sns = boto3.client('sns', region_name=region)

    try:
        response = sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email_address
        )
        print(f"Subscription ARN: {response['SubscriptionArn']}")
        return response['SubscriptionArn']

    except Exception as e:
        print(f"Error subscribing email to SNS topic: {e}")
        return None