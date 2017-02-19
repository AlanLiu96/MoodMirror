# MoodMirror

### Setup

Install the requirements from the directory. (use a virtualenv if needed)

` pip install -r requirements.txt `

Then run using main.py

`python main.py`

It will run on localhost:3000

### Routes

Static server URL at 104.196.44.38:3000

##Android

#GET

- /check_trigger - Checks if photo has been uploaded

#POST

- /upload_photo -  Uploads a photo and saves it to URL
##Alexa

#GET

- /trigger_photo - Signals to start taking photos
- /trigger_stop - Signals to stop taking photos
- /message - Sends a journal entry/message
  - Query string parameter: {msg: [MESSAGE] }
