from flask import Flask, jsonify, request, render_template, url_for
from datetime import datetime
import base64
import os
import io
import random
import pytz


# Imports the Google Cloud client library
from google.cloud import vision

# custom imports
from watson import send_watson
from gDataStore import storeInTable, retrieveFromTable

app = Flask(__name__)

results = {'numEntry':0, 'fear':0.0, 'anger':0.0, 'joy':0.0, 'sadness':0.0, 'disgust':0.0, 'messages':[]}

should_take_photo = (False, "")
next_trig = (False, "")
hist_trig = (False, "")

pacific_tz = pytz.timezone('America/Los_Angeles') # desired time zone

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
    current_datetime = local_to_desiredTZ()
    am_pm = "AM" if current_datetime.hour <= 12 else "PM"
    hour = current_datetime.hour % 12 if current_datetime.hour % 12  != 0 else 12
    return render_template('home.html', hour=('%02d' % hour), minute=('%02d' % current_datetime.minute), am_pm=am_pm)

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
    # json = '{"mydate":new Date("%s")}' % date.ctime()
    # json = getRecordedData()
    return render_template('graphs.html')

# Android
# Checks if photo has been uploaded
@app.route('/check_trigger', methods=['GET'])
def check_trigger():
    global should_take_photo
    print(should_take_photo)
    return jsonify({"ready": should_take_photo[0]})

# Android
# Checks if photo has been uploaded
@app.route('/check_next', methods=['GET'])
def check_next():
    global next_trig
    print(next_trig)
    ready = True if next_trig[0] else False
    if next_trig[0]:
        next_trig = (False, "")
    return jsonify({"ready": ready})


# Android
# Checks if photo has been uploaded
@app.route('/check_history', methods=['GET'])
def check_history():
    global hist_trig
    print(hist_trig)
    ready = True if hist_trig[0] else False
    if hist_trig[0]:
        hist_trig = (False, "")
    return jsonify({"ready": ready})

# Android
# Uploads an image and saves it to URL
@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    global should_take_photo
    file = request.files['photo']
    read_image(file)
    # file.save('images/test.jpg')
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
    retVal = max(ret, key=lambda key: ret[key])
    print str(ret)
    ret['message'] = message
    sessions = addEmotions(ret) # adds to current Session
    return retVal

# Alexa
# Signals move to next
@app.route('/trigger_next', methods=['GET'])
def trigger_next():
    global next_trig
    next_trig = (True, "")
    print(next_trig, "is trigger_next")
    return "next triggered"

# Alexa
# Signals start history
@app.route('/trigger_history', methods=['GET'])
def trigger_history():
    global hist_trig
    hist_trig = (True, "")
    print(hist_trig, "is trigger_history")
    return "history triggered"


# Image Read
# Finds the first face and finds emotion
# Then returns a dict with those emotions, while saving to a db
# @app.route('/image_test')
def read_image(image_file):
    # Instantiates a Google Vision client
    print("trying to create client")
    vision_client = vision.Client()
    # print("FINISHING CREATING CLIENT")

    # # The name of the image file to annotate
    # file_name = os.path.join(
    #     os.path.dirname(__file__),
    #     'images/test.jpg')

    # Loads the image into memory
    # with io.open(file_name, 'rb') as image_file:
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
    print str(ret)
    ret['message'] = None # empty placeholder

    # Performs label detection on the image file
    # labels = image.detect_labels()
    # print('Labels:')
    # for label in labels:
    #     print(label.description)
    addEmotions(ret)
    return "Facial Emotions: " + str(ret)

# @app.route('/test')
def getRecordedData():
    start_date = datetime(1990, 1, 1)
    testDictList = retrieveFromTable(start_date)
    newList = []
    for j in range(len(testDictList)):
        testDict = testDictList[j]
        for i in range(len(testDict['messages'])):
            testDict['messages'][i] = str(testDict['messages'][i])
            # json = '{"mydate":new Date("%s")}' % date.ctime()
        # testDict1 = "{\'joy\': %f, \'datetime\': new Date(%s)}, \'sadness\': %f, \'disgust\': %f, \'anger\': %f, \'fear\': %f" % (testDict['joy'], testDict['datetime'].ctime(), testDict['sadness'], testDict['disgust'], testDict['anger'], testDict['fear'])
        # testDict2 =  ",\'messages\': " + str(testDict['messages']) +  "}"
        # testDict = testDict1 + testDict2
        newList.append(testDict)
        print newList
    return str(newList)

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

def local_to_desiredTZ():
    local_dt = datetime.now(pytz.utc).replace(tzinfo=pytz.utc).astimezone(pacific_tz)
    return local_dt

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=3000, debug=True)
    app.run(host='0.0.0.0', port=3000)
