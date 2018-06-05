#!/Users/kevin/.virtualenvs/RekognitionBackend/bin/python

import boto3
import os


def search_by_face(photo):
    match_info = {}
    rekognition = boto3.client("rekognition", "us-east-1")
    response = rekognition.search_faces_by_image(
        CollectionId='rekognition-demo',
        FaceMatchThreshold=95,
        Image={
            'S3Object': {
                'Bucket': 'la-aws-rekognition-demo',
                'Name': photo,
            },
        },
        MaxFaces=1,
    )
    # print response
    if len(response["FaceMatches"]) != 1:
        match_info.update({'matched': False})
        match_info.update({'ExternalImageId': ''})
        return match_info
    else:
        match_info.update({'matched': True})
        match_info.update({'ExternalImageId': response["FaceMatches"][0]["Face"]["ExternalImageId"]})
        match_info.update({'Confidence': response['FaceMatches'][0]['Face']['Confidence']})
        return match_info


def handler(event, context):
    if 'AWS_LAMBDA_FUNCTION_VERSION' in os.environ:
        photo = str(event['queryStringParameters']['photo'])
    else:
        photo = "ke-1.JPG"
    result = search_by_face(photo)
    if result['matched']:
        print "not matched"
        return {"statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": "{\"matched\": " + "true," +
                "\"confidence\": " + str(result["Confidence"]) + ","
                "\"externalid\": \"" + str(result["ExternalImageId"]) + "\"}"}
    else:
        print "matched!"
        return {"statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": "{\"matched\": " + "false}"}


if __name__ == '__main__':
    handler("event", "context")  # Allows for local execution / testing. This gets ignored by AWS Lambda.
