#!/Users/kevin/.virtualenvs/RekognitionBackend/bin/python

import json
import requests
import boto3
from base64 import b64decode
import urllib
import os


def decrypt_kms_data(encrypted_data):
    kms = boto3.client('kms')
    decrypted = kms.decrypt(CiphertextBlob=b64decode(encrypted_data))['Plaintext']
    return str(decrypted)


def log(msg, console):
    logfile = open("/tmp/rekognition.log", "a")
    if console:
        print msg
    logfile.write(msg + "\n")
    logfile.close()


def get_rsvps(event_id):
    url = 'https://api.meetup.com/2/rsvps'

    params = dict(
        key=decrypt_kms_data(os.environ['meetupApiKey']),
        event_id=event_id,
        order='name'
    )

    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)
    print json.dumps(data['results'], indent=4, sort_keys=True)
    return data['results']


# https://gist.github.com/alexcasalboni/0f21a1889f09760f8981b643326730ff
def index_faces(imageByteArray, image_id=None, attributes=(), region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    response = rekognition.index_faces(
        Image={
            'Bytes': imageByteArray
        },
        CollectionId='rekognition-collection-id-goes-here',  # Insert your own collection ID here
        ExternalImageId=image_id,
        DetectionAttributes=attributes,
    )
    return response['FaceRecords']


# https://stackoverflow.com/questions/8286352/how-to-save-an-image-locally-using-python-whose-url-address-i-already-know
def image2ByteArray(ImageUrl, MemberId):
    file_name = "/tmp/" + MemberId + ".jpg"
    urllib.urlretrieve(ImageUrl, file_name)
    with open(file_name, "rb") as imageFile:
        f = imageFile.read()
        b = bytearray(f)
    try:
        os.remove(file_name)
    except:
        pass
    return b


def processRsvp(rsvps, event_id):
    totalCount = 0
    successfulCount = 0
    for rsvp in rsvps:
        totalCount = totalCount + 1
        try:
            member_id = str(rsvp["member"]["member_id"])
        except:
            log("Error: Unable to set Member ID", True)
            continue

        try:
            member_name = rsvp["member"]["name"]
        except:
            log("Error: " + member_id + " no member name found", True)
            continue

        try:
            highres_url = rsvp["member_photo"]["highres_link"]
        except:
            log("Error: " + member_id + " (" + member_name + ")" + " No high res photo found", True)
            continue

        try:
            converted_image = image2ByteArray(highres_url, member_id)
        except Exception, e:
            log("Error: " + member_id + " (" + member_name + ")" + " Unable to convert image to byte array (" + str(
                e) + ")", True)
            continue

        try:
            IndexedFace = index_faces(image2ByteArray(highres_url, member_id), member_id, ['ALL'])
            update_dynamodb(str(event_id), member_id, member_name, 'false')
        except Exception, e:
            log("Error: " + member_id + " (" + member_name + ")" + " Unable to index face (" + str(e) + ")", True)
            continue

        successfulCount = successfulCount + 1
        log("Success: " + member_id + " (" + member_name + ")" + " indexed.", True)

    log("Total RSVP's process: " + str(totalCount), True)
    log("Total successfully indexed faces: " + str(successfulCount), True)


def create_image_byte_Array():
    pass


def add_image_to_collection():
    pass


def update_dynamodb(meetup_id, member_id, member_name, checked_in):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="https://dynamodb.us-east-1.amazonaws.com")
    table = dynamodb.Table('your-dynamodb-table-name-goes-here')  # Add your DynamoDB table name here
    try:
        table.put_item(
            Item={
                'meetupId': meetup_id,
                'memberId': member_id,
                'name': member_name.title().replace(".",""),
                'checkedIn': checked_in
            }
        )
    except Exception, e:
        print str(e)


def handler(event, context):
    global rsvps
    event_id = 123456789  # Add your Meetup.com Event ID over here
    rsvps = get_rsvps(event_id)
    try:
        os.remove("/tmp/rekognition.log")
    except Exception, e:
        print(str(e))
    log("There are " + str(len(rsvps)) + " to process", True)
    processRsvp(rsvps, event_id)
    return event


if __name__ == '__main__':
    handler("event", "context")  # Allows for local execution / testing. This gets ignored by AWS Lambda.
