import boto3
import json
import os

def create_iam_role_for_lambda(role_name, region="us-east-1"):
    """Creates an IAM role for Lambda functions."""
    iam = boto3.client("iam", region_name=region)

    # Trust relationship policy (allows Lambda to assume the role)
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    try:
        # Create the role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Lambda functions",
        )
        role_arn = response["Role"]["Arn"]

        # Attach policies
        attach_lambda_policy(role_name, region)

        print(f"IAM role '{role_name}' created successfully. ARN: {role_arn}")
        return role_arn

    except Exception as e:
        print(f"Error creating IAM role: {e}")
        return None

def attach_lambda_policy(role_name, region="us-east-1"):
    iam = boto3.client("iam", region_name=region)
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Action": ["dynamodb:PutItem", "dynamodb:Scan"], "Resource": "arn:aws:dynamodb:us-east-1:754789402555:table/CarbonFootprint"},
            {"Effect": "Allow", "Action": ["s3:PutObject"], "Resource": "arn:aws:s3:::carbon-tracker-reports"},
            {"Effect": "Allow", "Action": ["sns:Publish"], "Resource": "arn:aws:sns:us-east-1:754789402555:carbon-tracker-notifications"},
            {"Effect": "Allow", "Action": ["secretsmanager:GetSecretValue"], "Resource": "arn:aws:secretsmanager:*:*:secret:carbon_interface_api_key"},
        ],
    }

    policy_name = f"{role_name}-policy"

    try:
        policy_response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        policy_arn = policy_response['Policy']['Arn']

        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        print (f"Policy {policy_name} attached to role {role_name}")

    except Exception as e:
        print(f"Error attaching policy to role: {e}")

if __name__ == "__main__":
    role_name = os.environ.get("LAMBDA_ROLE_NAME")
    region = os.environ.get("AWS_REGION", "us-east-1")

    if not role_name:
        print("Please set LAMBDA_ROLE_NAME environment variable.")
    else:
        create_iam_role_for_lambda(role_name, region)