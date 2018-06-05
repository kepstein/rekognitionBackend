#!/Users/kevin/.virtualenvs/RekognitionBackend/bin/python

import boto3
import sys


def index_faces(imageByteArray, image_id=None, attributes=(), region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    response = rekognition.index_faces(
        Image={
            'Bytes': imageByteArray
        },
        CollectionId='rekognition-collection-id-goes-here',
        ExternalImageId=image_id,
        DetectionAttributes=attributes,
    )
    return response['FaceRecords']


# https://stackoverflow.com/questions/8286352/how-to-save-an-image-locally-using-python-whose-url-address-i-already-know
def image2ByteArray(fileName):
    with open(fileName, "rb") as imageFile:
        f = imageFile.read()
        b = bytearray(f)
    return b

response = index_faces(image2ByteArray(sys.argv[1]),"kevin-epstein",['ALL'])
print response