
import boto3

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