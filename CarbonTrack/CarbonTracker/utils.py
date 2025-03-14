# CarbonTracker/utils.py
import boto3
import os

import boto3

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


'''
def create_sns_topic(topic_name, region_name='us-east-1'):
    """Creates an SNS topic and returns its ARN."""
    sns_client = boto3.client('sns', region_name=region_name)
    response = sns_client.create_topic(Name=topic_name)
    return response['TopicArn']

def subscribe_email_to_sns(topic_arn, email, region_name='us-east-1'):
    """Subscribes an email address to an SNS topic."""
    sns_client = boto3.client('sns', region_name=region_name)
    response = sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email
    )
    print(f"SNS Subscription Response: {response}")

def send_verification_email_sns(topic_arn, verification_link, subject, region_name='us-east-1'):
    """Sends an email verification link via SNS."""
    sns_client = boto3.client('sns', region_name=region_name)
    message = f"Click the following link to verify your email: {verification_link}"
    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject
        )
        print(f"SNS Publish Response: {response}")
    except Exception as e:
        print(f"Error sending verification email via SNS: {e}")'''