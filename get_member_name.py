#!/Users/kevin/.virtualenvs/RekognitionBackend/bin/python

import boto3
import os


def search_by_id(id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('your_dynamodb_table_name_goes_here')  # Change the DynamoDB table name
    response = table.get_item(
        Key={
            "memberId": id,
            "meetupId": "0000000000"  # Insert your own meetup.com meetup ID here
        }
    )
    print response
    item = response['Item']
    print(item["name"])
    return item["name"]

def handler(event, context):
    if 'AWS_LAMBDA_FUNCTION_VERSION' in os.environ:
        print(event)
        id = str(event['queryStringParameters']['id'])
    else:
        id = "000000000"  # Hard-coded id goes here for local testing.
    result = search_by_id(id)
    print {"statusCode": 200,
           "headers": {"Content-Type": "application/json"},
           "body": "{\"name\": \"" + result + "\"}"}

    return {"statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "{\"name\": \"" + result + "\"}"}

if __name__ == '__main__':
    handler("event", "context")  # Allows for local execution / testing. This gets ignored by AWS Lambda.