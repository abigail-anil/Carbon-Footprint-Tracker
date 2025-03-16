import boto3
import time

lambda_client = boto3.client('lambda')
sns_client = boto3.client('sns')
events_client = boto3.client('events') # Add this line


rule_name = 'carbon-emissions-schedule'
schedule_expression = 'cron(0 0 1 * ? *)'

function_name = 'lambda-carbon-emissions'
topic_arn = 'arn:aws:sns:us-east-1:754789402555:carbon_emissions_alerts'

try:
    lambda_client.get_function(FunctionName=function_name)
    print(f"Function '{function_name}' already exists.")
    response = lambda_client.get_function(FunctionName=function_name)
except lambda_client.exceptions.ResourceNotFoundException:
    response = lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.9',
        Role='arn:aws:iam::754789402555:role/LabRole',
        Handler='lambda_function.lambda_handler',
        Code={'ZipFile': open('lambda_package.zip', 'rb').read()},
        Environment={'Variables': {'CARBON_TABLE': 'CarbonFootprint', 'SETTINGS_TABLE': 'user_settings'}}
    )
    print(f"Function '{function_name}' created.")
    print(response)

    # Wait for the function to become active
    while True:
        try:
            function_info = lambda_client.get_function(FunctionName=function_name)
            if function_info['Configuration']['State'] == 'Active':
                break
            else:
                print("Function state:", function_info['Configuration']['State'])
                time.sleep(5)  # Wait for 5 seconds
        except Exception as e:
            print(f'Error getting function state: {e}')
            time.sleep(5)

lambda_arn = function_info['Configuration']['FunctionArn'] #use the function_info variable here.

try:
    subscription_response = sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='lambda',
        Endpoint=lambda_arn
    )
    print("Subscription added")
except Exception as e:
    print(f"Subscription already exists or error: {e}")

try:
    lambda_client.add_permission(
        FunctionName=function_name,
        StatementId='sns-permission',
        Action='lambda:InvokeFunction',
        Principal='sns.amazonaws.com',
        SourceArn=topic_arn
    )
    print("Permission added")
except Exception as e:
    print(f"Permission already exists or error: {e}")
    
    
# CloudWatch events trigger.
# Create CloudWatch Events Rule
rule_response = events_client.put_rule(
    Name=rule_name,
    ScheduleExpression=schedule_expression,
    State='ENABLED',
    Description='Triggers lambda-carbon-emissions on the first of every month at midnight UTC.'
)

print(f"CloudWatch Events rule created: {rule_response}")

# Add Target to the Rule
lambda_arn = lambda_client.get_function(FunctionName=function_name)['Configuration']['FunctionArn']

target_response = events_client.put_targets(
    Rule=rule_name,
    Targets=[
        {
            'Id': '1',
            'Arn': lambda_arn,
        },
    ]
)

print(f"CloudWatch Events target added: {target_response}")

# Grant CloudWatch Events Permission to Invoke Lambda Function
permission_response = lambda_client.add_permission(
    FunctionName=function_name,
    StatementId='CloudWatchEventsInvoke',
    Action='lambda:InvokeFunction',
    Principal='events.amazonaws.com',
    SourceArn=rule_response['RuleArn']
)

print(f"Lambda permission added: {permission_response}")