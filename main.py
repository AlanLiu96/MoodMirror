import base64
import os

from flask import Flask, jsonify, request

import recommender
import get_props

import random

app = Flask(__name__)

should_take_photo = (False, "")

def add_error(results, reason):
    results['error'] = reason


@app.route('/')
def hello_world():
    return "If a human soul should dream of me, may he still remember me on awaking!"


@app.route('/judge-outfit')
def judge_outfit():
    data = get_props.getProps('images/test.jpg')
    res = ' '.join(recommender.get_comments(data))

    print(res)
    return res


@app.route('/take-photo', methods=['GET'])
def take_photo():
    global should_take_photo
    print(should_take_photo)
    return jsonify({"ready": should_take_photo[0]})

@app.route('/should-take-photo', methods=['GET'])
def set_should_take_photo():
    global should_take_photo
    should_take_photo = (True, "")
    print(should_take_photo)
    return str(random.randrange(1, 5))


@app.route('/test-vision', methods=['GET'])
def test_vision():
    return jsonify(get_props.getProps('images/summer.jpg'))

@app.route('/upload-image', methods=['POST'])
def upload_image():
    global should_take_photo
    should_take_photo = (False, "")
    file = request.files['photo']
    file.save('images/test.jpg')
    return 'Done'

if __name__ == "__main__":
    debug = os.environ.get("FLASK_APP_DEBUG", "")
    if debug == "":
        app.run(host="0.0.0.0", port=8042)
    else:
        app.run(port=8042, debug=True)
