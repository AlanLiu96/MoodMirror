from flask import Flask, jsonify, request
import base64
import os
import random

# custom imports
import recommender
import get_props
from watson import send_watson

app = Flask(__name__)

should_take_photo = (False, "")

def add_error(results, reason):
    results['error'] = reason

@app.route('/')
def hello_world():
    return "Hello World! What a beautiful day :) "

@app.route('/judge-outfit')
def judge_outfit():
    data = get_props.getProps('images/test.jpg')
    res = ' '.join(recommender.get_comments(data))
    print(res)
    return res

# Android
@app.route('/check_photo', methods=['GET'])
def take_photo():
    global should_take_photo
    print(should_take_photo)
    return jsonify({"ready": should_take_photo[0]})

# Alexa
@app.route('/trigger_photo', methods=['GET'])
def set_should_take_photo():
    global should_take_photo
    should_take_photo = (True, "")
    print(should_take_photo)
    return str(random.randrange(1, 5))

# Alexa
@app.route('/message', methods=['GET'])
def store_message():
    message = request.args.get('msg') # expect qString of msg
    if message == None:
        return 1 #error : no qString
    # TODOs
    # OPT: STORE MESSAGE?

    #Send to IBM Watson
    ret = send_watson(message) # ret val is a dict with emotion Ids mapped to emotion scores
    return message + " after being parsed " + str(ret)
    #STORE SENTIMENT

@app.route('/upload-image', methods=['POST'])
def upload_image():
    global should_take_photo
    should_take_photo = (False, "")
    file = request.files['photo']
    file.save('images/test.jpg')
    return 'Done'

if __name__ == "__main__":
    # debug = os.environ.get("FLASK_APP_DEBUG", "")
    # if debug == "":
        # app.run(host="0.0.0.0", port=3000)
    # else:
    app.run(port=3000, debug=True)
