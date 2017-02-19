from datetime import datetime
from google.cloud import datastore

def storeInTable(ret):
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Fetch the current date / time and store
    current_datetime = datetime.now()
    ret['datetime']=current_datetime

    # The kind for the new entity.
    kind = 'Emotions'

    # The name/ID for the new entity.
    name = "Mir_" + str(current_datetime)

    # Create the Cloud Datastore key for the new entity.
    key = datastore_client.key(kind, name)

    # Construct the new entity using the key. Set dictionary values for entity
    entity = datastore.Entity(key)

    for item in ret:
        entity[item]=ret[item]

    # Save the new entity to Datastore.
    datastore_client.put(entity)
    return "stored sucessfully"

def retrieveFromTable(startDate):
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about
    # each photo.
    query = datastore_client.query(kind='Emotions')
    query.order = ['datetime']

    query.add_filter(
        'datetime', '>', startDate)

    data = []

    emotionDataRecords = query.fetch()
    for emotionData in emotionDataRecords:
        print str(emotionData)
        sessionData = {}
        for emotion in emotionData:
            print emotion
            sessionData[str(emotion)] = emotionData[emotion]
        data.append(sessionData)
    print data
    return data
