from flask import Flask, jsonify, request
import base64
import os
import io
import random

# Imports the Google Cloud client library
from google.cloud import vision

# custom imports
from watson import send_watson

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
# Uploads an image snd saves it to URL
@app.route('/upload_image', methods=['POST'])
def upload_image():
    global should_take_photo
    # should_take_photo = (False, "") # disabled
    file = request.files['photo']
    file.save('images/test.jpg')
    return 'Done'

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
    # TODO: STORE SENTIMENT IN DB

    #Send to IBM Watson
    ret = send_watson(message) # ret val is a dict with emotion Ids mapped to emotion scores
    ret[message] = message
    return message + " after being parsed: " + str(ret)

# Image Read
@app.route('/image_test')
def read_image():
    # Instantiates a Google Vision client
    print "trying to create client"
    vision_client = vision.Client()
    print "FINISHING CREATING CLIENT"

    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        'images/test.jpg')
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
        image = vision_client.image(
            content=content)
    # Performs label detection on the image file
    labels = image.detect_labels()
    print('Labels:')
    for label in labels:
        print(label.description)
    return " ".join(labels)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
