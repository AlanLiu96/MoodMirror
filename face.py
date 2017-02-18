from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()
service = discovery.build('vision', 'v1', credentials=credentials)

service_request = service.images().annotate(body={
    'requests': [{
        'image': {
            'source': {
                'gcsImageUri': 'gs://blahblahy/test'
            }
        },
        'features': [{
            'type': 'FACE_DETECTION'
        }]
    }]
})

response = service_request.execute()
print(response)
labels = response['responses'][0]['faceAnnotations']

print(labels)
