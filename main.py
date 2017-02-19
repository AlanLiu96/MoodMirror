from flask import Flask, jsonify, request
import base64
import os
import io
import random

# Imports the Google Cloud client library
from google.cloud import vision

# custom imports
from watson import send_watson
from gDataStore import storeInTable

app = Flask(__name__)

should_take_photo = (False, "")

def add_error(results, reason):
    results['error'] = reason

@app.route('/')
def hello_world():
    return "Hello World! What a beautiful day :) "

# Android
# Checks if photo has been uploaded
@app.route('/check_trigger', methods=['GET'])
def check_trigger():
    global should_take_photo
    print(should_take_photo)
    return jsonify({"ready": should_take_photo[0]})

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
    return str(random.randrange(1, 5))

# Alexa
@app.route('/message', methods=['GET'])
def store_message():
    message = request.args.get('msg') # expect qString of msg
    if message == None:
        return 1 #error : no qString

    #Send to IBM Watson
    ret = send_watson(message) # ret val is a dict with emotion Ids mapped to emotion scores
    ret['message'] = message
    stored = storeInTable(ret)
    return message + " after being parsed: " + str(ret) + stored

# Image Read
# Finds the first face and finds emotion
# Then returns a dict with those emotions, while saving to a db
@app.route('/image_test')
def read_image():
    # Instantiates a Google Vision client
    print "trying to create client"
    vision_client = vision.Client()
    print "FINISHING CREATING CLIENT"

    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        'images/test2.jpg')
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
        image = vision_client.image(
            content=content)
    # look for faces
    faces = image.detect_faces(limit=10)
    print "I found", str(len(faces)), "faces"

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
    storeInTable(ret)
    return "Facial Emotions: " + str(ret)

def likelihoodToNum(likelihoodStr):
    if likelihoodStr == "UNKNOWN":
        print "UNKNOWN LIKELIHOOD FOR FACE"
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
