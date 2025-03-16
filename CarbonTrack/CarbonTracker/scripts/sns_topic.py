import boto3

def create_sns_topic(topic_name, region="us-east-1"):
    """Creates an SNS topic."""

    sns = boto3.client('sns', region_name=region)

    try:
        response = sns.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        print(f"Topic ARN: {topic_arn}")
        return topic_arn

    except Exception as e:
        print(f"Error creating SNS topic: {e}")
        return None

if __name__ == "__main__":
    topic_name = 'carbon_emissions_alerts' 
    topic_arn = create_sns_topic(topic_name)

    if topic_arn:
        print(f"SNS topic '{topic_name}' created successfully.")
    else:
        print("SNS topic creation failed.")