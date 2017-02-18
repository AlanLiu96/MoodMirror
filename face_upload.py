import base64
import os

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()
service = discovery.build('vision', 'v1', credentials=credentials)


def detect_face(face_file):
    image_content = face_file.read()
    batch_request = [{
        'image': {
            'content': base64.b64encode(image_content).decode('utf-8')
        },
        'features': [{
            'type': 'FACE_DETECTION',
        }]
    }]

    request = service.images().annotate(body={
        'requests': batch_request,
    })
    response = request.execute()

    return response['responses'][0]['faceAnnotations']


curPath = os.path.dirname(os.path.realpath(__file__))
input_filename = os.path.join(curPath, 'ngan.jpg')

with open(input_filename, 'rb') as image:
    faces = detect_face(image)

    print(faces)
