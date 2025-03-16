import boto3
import datetime
import json
import pytz
import os

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

CARBON_TABLE = os.environ['CARBON_TABLE']
SETTINGS_TABLE = os.environ['SETTINGS_TABLE']
TOPIC_ARN = 'arn:aws:sns:us-east-1:754789402555:carbon_emissions_alerts'

def lambda_handler(event, context):
    now_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    now_local = now_utc.astimezone(pytz.timezone('UTC'))
    end_time = now_local.replace(hour=23, minute=59, second=59, microsecond=0)

    # Monthly check (entire previous month)
    start_time = (now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0) # start of last month.
    check_frequency = 'Monthly'

    # 2. Scan user settings for matching frequencies
    settings_table = dynamodb.Table(SETTINGS_TABLE)
    response = settings_table.scan(
        FilterExpression='emission_check_frequency = :freq',
        ExpressionAttributeValues={':freq': check_frequency}
    )

    for user_settings in response['Items']:
        user_id = user_settings['userId']
        electricity_threshold = user_settings.get('electricity_threshold', 0)
        flight_threshold = user_settings.get('flight_threshold', 0)
        shipping_threshold = user_settings.get('shipping_threshold', 0)
        subscribed = user_settings.get('subscribed', False)

        if not subscribed:
            continue

        # 3. Query CarbonFootprint for user emissions
        carbon_table = dynamodb.Table(CARBON_TABLE)
        query_response = carbon_table.query(
            KeyConditionExpression='userId = :user_id AND #ts BETWEEN :start_time AND :end_time',
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':start_time': start_time.isoformat(),
                ':end_time': end_time.isoformat()
            },
            ExpressionAttributeNames={'#ts': 'timestamp'}
        )

        total_electricity = 0
        total_flight = 0
        total_shipping = 0

        for item in query_response.get('Items', []):
            if item['activityType'] == 'electricity':
                total_electricity += float(item['carbonKg'])
            elif item['activityType'] == 'flight':
                total_flight += float(item['carbonKg'])
            elif item['activityType'] == 'shipping':
                total_shipping += float(item['carbonKg'])

        # 4. Check thresholds and send notifications
        if total_electricity > electricity_threshold or total_flight > flight_threshold or total_shipping > shipping_threshold:
            message = f"Carbon emission alert for user {user_id}:\n"
            if total_electricity > electricity_threshold:
                message += f"  Electricity: {total_electricity} kg (Threshold: {electricity_threshold} kg)\n"
            if total_flight > flight_threshold:
                message += f"  Flight: {total_flight} kg (Threshold: {flight_threshold} kg)\n"
            if total_shipping > shipping_threshold:
                message += f"  Shipping: {total_shipping} kg (Threshold: {shipping_threshold} kg)\n"

            sns.publish(
                TopicArn=TOPIC_ARN,
                Message=message,
                Subject='Carbon Emission Alert'
            )

    return {'statusCode': 200, 'body': json.dumps('Monthly emission checks completed')}