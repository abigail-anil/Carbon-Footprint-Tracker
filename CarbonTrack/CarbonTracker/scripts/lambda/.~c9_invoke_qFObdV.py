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

notified_users = set()  # Track users who have already received an alert

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
    
    
    for user_settings in response.get('Items',[]):  # Iterate over the items in the scan response.
        user_id = user_settings.get('userId')  
        electricity_threshold = user_settings.get('electricity_threshold', 0)  
        flight_threshold = user_settings.get('flight_threshold', 0)  
        shipping_threshold = user_settings.get('shipping_threshold', 0)  
        fuel_threshold = user_settings.get('fuel_threshold', 0) 
        vehicle_threshold = user_settings.get('vehicle_threshold', 0) 
        subscribed = user_settings.get('subscribed', False)  

        logger.debug(f"Processing user: {user_id}")  # Log the user ID being processed.
        logger.debug(f"User settings: {user_settings}")  # Log the user settings.

        if not subscribed or user_id in notified_users:  # Check if the user is not subscribed or already notified.
            logger.debug(f"User {user_id} is already notified or is not subscribed. Skipping.")  # Log that the user is not subscribed.
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
        total_fuel = 0
        total_vehicle = 0

        for item in query_response.get('Items',):  # Iterating over the items
            if item['activityType'] == 'electricity':  # Checking if the activity type is electricity.
                total_electricity += float(item['carbonKg'])  # Adding the electricity emissions to the total.
            elif item['activityType'] == 'flight':  # Checking if the activity type is flight.
                total_flight += float(item['carbonKg'])  # Adding the flight emissions to the total.
            elif item['activityType'] == 'shipping':  # Checking if the activity type is shipping.
                total_shipping += float(item['carbonKg'])  # Adding the shipping emissions to the total.
            elif item['activityType'] == 'fuel_combustion':  # Checking if the activity type is shipping.
                total_fuel += float(item['carbonKg'])
            elif item['activityType'] == 'vehicle':  # Checking if the activity type is shipping.
                total_vehicle += float(item['carbonKg'])

        logger.debug(f"Total electricity emission for user {user_id}: {total_electricity}")  # Logging the total electricity emissions.
        logger.debug(f"Total flight emission for user {user_id}: {total_flight}")  # Logging the total flight emissions.
        logger.debug(f"Total shipping for user {user_id}: {total_shipping}")  # Logging the total shipping emissions.
        logger.debug(f"Total fuel emission for user {user_id}: {total_fuel}")
        logger.debug(f"Total vehicle emission for user {user_id}: {total_vehicle}")

        ''' Check thresholds and send notifications: Compare total emissions against user-defined thresholds. '''

        if total_electricity > electricity_threshold or total_flight > flight_threshold or total_shipping > shipping_threshold or total_fuel > fuel_threshold or total_vehicle > vehicle_threshold:  # Checking if any threshold is exceeded.
            message = f"Carbon Emission Alert for User {user_id} (Monthly):\n"  # Creating the message for the email notification.
            message += f"Period: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n"  # Adding the period to the message body.

            if total_electricity > electricity_threshold:  # Check if the electricity threshold is exceeded.
                message += f"  Total Carbon emissions for Electricity : {total_electricity:.2f} kg (Threshold: {electricity_threshold:.2f} kg)\n"  # Adding the electricity emissions and threshold to the message.
            if total_flight > flight_threshold:  # Check if the flight threshold is exceeded.
                message += f"  Total Carbon emissions for Flight: {total_flight:.2f} kg (Threshold: {flight_threshold:.2f} kg)\n"  # Adding the flight emissions and threshold to the message.
            if total_shipping > shipping_threshold:  # Check if the shipping threshold is exceeded.
                message += f"  Total Carbon emissions for Shipping: {total_shipping:.2f} kg (Threshold: {shipping_threshold:.2f} kg)\n"  # Adding the shipping emissions and threshold to the message.
            if total_fuel > fuel_threshold:  # Check if the shipping threshold is exceeded.
                message += f"  Total Carbon emissions for Fuel Combustions: {total_fuel:.2f} kg (Threshold: {fuel_threshold:.2f} kg)\n" 
            if total_vehicle > vehicle_threshold:  # Check if the shipping threshold is exceeded.
                message += f"  Total Carbon emissions for Vehicles: {total_vehicle:.2f} kg (Threshold: {vehicle_threshold:.2f} kg)\n" 

            # Adding recommendations
            message += "\nHere are some tips to reduce your emissions:\n"  # Adding a section for recommendations.
            if total_electricity > electricity_threshold:  # Checking if the electricity threshold is exceeded.
                message += "  - Conserve energy by turning off lights and unplugging devices when not in use.\n"
                message += "  - Switch to energy-efficient appliances and lighting.\n"
                message += "  - Consider installing solar panels or switching to a renewable energy provider.\n" # Adding a recommendation for reducing electricity emissions.
                
            if total_flight > flight_threshold:  # Checking if the flight threshold is exceeded.
                message += "  - Consider offsetting your flight emissions or choosing more sustainable travel options.\n"
                message += "  - Opt for direct flights to reduce fuel consumption.\n"
                message += "  - Pack light to reduce the aircraft's weight.\n"
                message += "  - Explore alternative modes of transportation like trains or buses for shorter distances.\n" # Adding a recommendation for reducing flight emissions.
                
            if total_shipping > shipping_threshold:  # Checking if the shipping threshold is exceeded.
                message += "  - Opt for local products or consolidate your online orders to reduce shipping emissions.\n"
                message += "  - Choose slower shipping options when possible, as they are often more fuel-efficient.\n"
                message += "  - Support companies that prioritize sustainable shipping practices.\n"
                message += "  - Reduce packaging waste by opting for minimal or recyclable packaging.\n"

            if total_fuel > fuel_threshold:  # Checking if the shipping threshold is exceeded.
                message += "  - Reduce reliance on fossil fuels by using public transportation, biking, or walking.\n"
                message += "  - Improve home insulation to reduce heating and cooling needs.\n"
                message += "  - Switch to a more fuel-efficient heating system.\n"
                message += "  - Carpool or combine errands to minimize driving.\n"
                
            if total_vehicle > vehicle_threshold:  # Checking if the shipping threshold is exceeded.
                message += "  - Drive less by combining trips, using public transport, biking, or walking.\n"
                message += "  - Maintain your vehicle for optimal fuel efficiency (tire pressure, engine tune-ups).\n"
                message += "  - Consider switching to a hybrid or electric vehicle.\n"
                message += "  - Practice smooth acceleration and braking to conserve fuel.\n"
                message += "  - Avoid idling your engine for extended periods.\n"
                

            logger.info(f"Sending SNS notification for user {user_id}: {message}")
            try:
                '''Publish to SNS topic: Send email notification via SNS if thresholds are exceeded.'''
                sns.publish(
                        TopicArn=TOPIC_ARN,
                        Message=message,
                        Subject='Carbon Emission Alert (Monthly)'
                    )
                notified_users.add(user_id)  # Mark user as notified
                logger.info(f"SNS notification sent successfully for user {user_id}")
            except Exception as e:
                logger.exception(f"Error sending SNS notification for user {user_id}: {str(e)}")

        else:
            logger.info(f"Thresholds not exceeded for user {user_id}. Skipping SNS notification.")

    return {'statusCode': 200, 'body': json.dumps('Monthly emission checks completed')}  # Return a successful HTTP response indicating that the monthly emission checks have been completed.s