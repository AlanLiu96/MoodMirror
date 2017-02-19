from flask import Flask, jsonify, request, render_template, url_for
from datetime import datetime
import base64
import os
import io
import random

# Imports the Google Cloud client library
from google.cloud import vision

# custom imports
from watson import send_watson
from gDataStore import storeInTable, retrieveFromTable

app = Flask(__name__)



results = {'numEntry':0, 'fear':0.0, 'anger':0.0, 'joy':0.0, 'sadness':0.0, 'disgust':0.0, 'messages':[]}

should_take_photo = (False, "")

def add_error(results, reason):
    results['error'] = reason

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

# views
@app.route('/')
def index():
    return render_template('home.html')
@app.route('/intro1')
def intro1():
    return render_template('intro1.html')

@app.route('/intro2')
def intro2():
    return render_template('intro2.html')

@app.route('/encouragement')
def encouragement():
    return render_template('encouragement.html')

@app.route('/finish')
def finish():
    return render_template('finish.html')

@app.route('/graphs')
def graphs():
    return render_template('graphs.html')

# Android
# Uploads an image and saves it to URL
@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    global should_take_photo
    # should_take_photo = (False, "") # disabled
    file = request.files['photo']
    file.save('images/test.jpg')
    return jsonify({"success": True})

# Alexa
# Signals start taking photos
@app.route('/trigger_photo', methods=['GET'])
def trigger_photo():
    global should_take_photo
    should_take_photo = (True, "")
    print(should_take_photo)
    return str(random.randrange(1, 5))

# Alexa
# Signals start taking photos
@app.route('/trigger_stop', methods=['GET'])
def trigger_stop():
    global should_take_photo
    should_take_photo = (False, "")
    print(should_take_photo)
    # store old results if applicable
    global results
    if results['numEntry']>0:
        for item in results:
            if item != "messages" and item != 'numEntry':
                results[item] = results[item]/results['numEntry']
        results.pop('numEntry')
        storeInTable(results)
        # reset results
        results = {'numEntry':0, 'fear':0, 'anger':0, 'joy':0, 'sadness':0, 'disgust':0, 'messages':[]}
    return str(random.randrange(1, 5))

# Alexa
@app.route('/message', methods=['GET'])
def store_message():
    message = request.args.get('msg') # expect qString of msg
    if message == None:
        return "I couldn't find a message! :(" #error : no qString

    #Send to IBM Watson
    ret = send_watson(message) # ret val is a dict with emotion Ids mapped to emotion scores
    ret['message'] = message
    sessions = addEmotions(ret) # adds to current Session
    return message + " after being parsed: " + str(ret) + sessions

# Image Read
# Finds the first face and finds emotion
# Then returns a dict with those emotions, while saving to a db
@app.route('/image_test')
def read_image():
    # Instantiates a Google Vision client
    print("trying to create client")
    vision_client = vision.Client()
    print("FINISHING CREATING CLIENT")

    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        'images/test.jpg')
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
        image = vision_client.image(
            content=content)
    # look for faces
    faces = image.detect_faces(limit=10)
    print("I found", str(len(faces)), "faces")

    # for face in faces:
    face = faces[0]

    ret = {}
    # anger, joy, sorrow, surprise
    ret['anger'] = likelihoodToNum(face.anger.value)
    ret['joy'] = likelihoodToNum(face.joy.value)
    ret['sadness'] = likelihoodToNum(face.sorrow.value)

    # had to "adjust" b/c need these categories
    ret['fear'] = likelihoodToNum(face.surprise.value) # sketchy stuff
    ret['disgust'] = 0.5* likelihoodToNum(face.surprise.value) + 0.3* likelihoodToNum(face.anger.value) + 0.2* likelihoodToNum(face.sorrow.value)

    ret['message'] = None # empty placeholder
    # Performs label detection on the image file
    labels = image.detect_labels()
    print('Labels:')
    for label in labels:
        print(label.description)
    addEmotions(ret)
    return "Facial Emotions: " + str(ret)

@app.route('/test')
def test():
    start_date = datetime(1990, 1, 1)
    testDictList = retrieveFromTable(start_date)
    for testDict in testDictList:
        for i in range(len(testDict['messages'])):
            testDict['messages'][i] = str(testDict['messages'][i])
        testDict = str(testDict)
    return str(testDictList)

def likelihoodToNum(likelihoodStr):
    if likelihoodStr == "UNKNOWN":
        print("UNKNOWN LIKELIHOOD FOR FACE")
        return -1
    elif likelihoodStr == "VERY_LIKELY":
        return 1.0
    elif likelihoodStr == "LIKELY":
        return 0.75
    elif likelihoodStr == "POSSIBLE":
        return 0.5
    elif likelihoodStr == "UNLIKELY":
        return 0.25
    elif likelihoodStr == "VERY_UNLIKELY":
        return 0.0

def addEmotions(ret):
    results['numEntry']+=1
    for item in ret:
        if item == 'message':
            results['messages'].append(ret[item])
        else:
            results[item]+=ret[item]
    return "added to Session"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
