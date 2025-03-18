import boto3  
import datetime 
import json  
import pytz  # for time zones.
import os  #  for interacting with the operating system.
import logging  #  for logging messages.

# Configuring logging
logger = logging.getLogger()  # Get the root logger.
logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG for detailed logs.

dynamodb = boto3.resource('dynamodb') 
sns = boto3.client('sns')  

CARBON_TABLE = os.environ['CARBON_TABLE']  # Retrieve the name of the CarbonFootprint DynamoDB table from environment variables of lambda function.
SETTINGS_TABLE = os.environ['SETTINGS_TABLE']  # Retrieve the name of the user settings DynamoDB table from environment variables of lambda function.
TOPIC_ARN = 'arn:aws:sns:us-east-1:754789402555:carbon_emissions_alerts'  # Define the ARN of the SNS topic for carbon emission alerts.

def lambda_handler(event, context):
    logger.debug(f"Event: {event}")  # Log the incoming event.
    logger.debug(f"Context: {context}")  # Log the Lambda context.

    now_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)  # Get the current UTC time and set its timezone.
    now_local = now_utc.astimezone(pytz.timezone('UTC'))  # Convert the UTC time to the local time zone (also UTC in this case, but good practice).
    end_time = now_local.replace(hour=23, minute=59, second=59, microsecond=0)  # Set the end time to the last second of the current day.

    '''Monthly check: Calculate start time as the first day of the current month. '''
    start_time = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # Set the start time to the beginning of the current month.
    check_frequency = 'Monthly'  # Set the check frequency to 'Monthly'.

    logger.debug(f"Start Time: {start_time.isoformat()}")  # Log the start time in ISO format.
    logger.debug(f"End Time: {end_time.isoformat()}")  # Log the end time in ISO format.

    ''' Scan user settings for matching frequencies: Retrieve user settings based on the monthly frequency. '''
    settings_table = dynamodb.Table(SETTINGS_TABLE)  # Create a DynamoDB table object for the user settings table.
    response = settings_table.scan(  # Scan the user settings table.
        FilterExpression='emission_check_frequency = :freq',  # Filter the scan results based on the check frequency.
        ExpressionAttributeValues={':freq': check_frequency}  # Set the value of the filter expression.
    )

    logger.debug(f"Scan response: {response}")  # Log the scan response.

    for user_settings in response.get('Items',):  # Iterate over the items in the scan response.
        user_id = user_settings['userId']  
        electricity_threshold = user_settings.get('electricity_threshold', 0)  
        flight_threshold = user_settings.get('flight_threshold', 0)  
        shipping_threshold = user_settings.get('shipping_threshold', 0)  
        subscribed = user_settings.get('subscribed', False)  

        logger.debug(f"Processing user: {user_id}")  # Log the user ID being processed.
        logger.debug(f"User settings: {user_settings}")  # Log the user settings.

        if not subscribed:  # Check if the user is not subscribed.
            logger.debug(f"User {user_id} is not subscribed. Skipping.")  # Log that the user is not subscribed.
            continue  # Skip to the next user

        ''' Query CarbonFootprint for user emissions: Retrieve emission records for previous month.'''
        carbon_table = dynamodb.Table(CARBON_TABLE)  # Creating a DynamoDB table object for the CarbonFootprint table.
        query_response = carbon_table.query(  # Querying the CarbonFootprint table.
            KeyConditionExpression='userId = :user_id AND #ts BETWEEN :start_time AND :end_time',  # Defining the query condition.
            ExpressionAttributeValues={  # Set the values of the query condition.
                ':user_id': user_id,
                ':start_time': start_time.isoformat(),
                ':end_time': end_time.isoformat()
            },
            ExpressionAttributeNames={'#ts': 'timestamp'}  # Setting the expression attribute name for the timestamp.
        )

        logger.debug(f"Query response for user {user_id}: {query_response}")  # Logging the query response.

        '''Initializing emissions'''
        total_electricity = 0  
        total_flight = 0  
        total_shipping = 0  

        for item in query_response.get('Items',):  # Iterating over the items
            if item['activityType'] == 'electricity':  # Checking if the activity type is electricity.
                total_electricity += float(item['carbonKg'])  # Adding the electricity emissions to the total.
            elif item['activityType'] == 'flight':  # Checking if the activity type is flight.
                total_flight += float(item['carbonKg'])  # Adding the flight emissions to the total.
            elif item['activityType'] == 'shipping':  # Checking if the activity type is shipping.
                total_shipping += float(item['carbonKg'])  # Adding the shipping emissions to the total.

        logger.debug(f"Total electricity for user {user_id}: {total_electricity}")  # Logging the total electricity emissions.
        logger.debug(f"Total flight for user {user_id}: {total_flight}")  # Logging the total flight emissions.
        logger.debug(f"Total shipping for user {user_id}: {total_shipping}")  # Logging the total shipping emissions.

        ''' Check thresholds and send notifications: Compare total emissions against user-defined thresholds. '''

        if total_electricity > electricity_threshold or total_flight > flight_threshold or total_shipping > shipping_threshold:  # Checking if any threshold is exceeded.
            message = f"Carbon Emission Alert for User {user_id} (Monthly):\n"  # Creating the message for the email notification.
            message += f"Period: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n"  # Adding the period to the message body.

            if total_electricity > electricity_threshold:  # Check if the electricity threshold is exceeded.
                message += f"  Electricity: {total_electricity:.2f} kg (Threshold: {electricity_threshold:.2f} kg)\n"  # Adding the electricity emissions and threshold to the message.
            if total_flight > flight_threshold:  # Check if the flight threshold is exceeded.
                message += f"  Flight: {total_flight:.2f} kg (Threshold: {flight_threshold:.2f} kg)\n"  # Adding the flight emissions and threshold to the message.
            if total_shipping > shipping_threshold:  # Check if the shipping threshold is exceeded.
                message += f"  Shipping: {total_shipping:.2f} kg (Threshold: {shipping_threshold:.2f} kg)\n"  # Adding the shipping emissions and threshold to the message.

            # Adding recommendations
            message += "\nHere are some tips to reduce your emissions:\n"  # Adding a section for recommendations.
            if total_electricity > electricity_threshold:  # Checking if the electricity threshold is exceeded.
                message += "  - Conserve energy by turning off lights and unplugging devices when not in use.\n"  # Adding a recommendation for reducing electricity emissions.
            if total_flight > flight_threshold:  # Checking if the flight threshold is exceeded.
                message += "  - Consider offsetting your flight emissions or choosing more sustainable travel options.\n"  # Adding a recommendation for reducing flight emissions.
            if total_shipping > shipping_threshold:  # Checking if the shipping threshold is exceeded.
                message += "  - Opt for local products or consolidate your online orders to reduce shipping emissions.\n"

            logger.info(f"Sending SNS notification for user {user_id}: {message}")
            try:
                '''Publish to SNS topic: Send email notification via SNS if thresholds are exceeded.'''
                sns.publish(
                    TopicArn=TOPIC_ARN,
                    Message=message,
                    Subject='Carbon Emission Alert (Monthly)'
                )
                logger.info(f"SNS notification sent successfully for user {user_id}")
            except Exception as e:
                logger.exception(f"Error sending SNS notification for user {user_id}:")

        else:
            logger.info(f"Thresholds not exceeded for user {user_id}. Skipping SNS notification.")

    return {'statusCode': 200, 'body': json.dumps('Monthly emission checks completed')}  # Return a successful HTTP response indicating that the monthly emission checks have been completed.s