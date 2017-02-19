'use strict';

const Alexa = require('alexa-sdk');

const APP_ID = undefined; // TODO replace with your app ID (OPTIONAL).

// Make endpoint requests
const http = require('http');
const util = require('util');

/**
 * The AlexaSkill prototype and helper functions
 */
// var AlexaSkill = require('./AlexaSkill');

var Moody = function () {
    AlexaSkill.call(this, APP_ID);
};

function createConnection(callback) {

  return http.get({
    host: '104.196.44.38',
    port: 3000,
    path: '/trigger_photo'
  }, function(response) {

    var body = '';
    response.on('data', function(c) {
     body += c;
    });
    response.on('end', function() {
     console.log(body);
     var message = body;
     callback(message);
    });
  }).on('socket', (socket) => {
    socket.emit('agentRemove');
  });

}

function endConnection(callback) {

  return http.get({
    host: '104.196.44.38',
    port: 3000,
    path: '/trigger_stop'
  }, function(response) {

    var body = '';
    response.on('data', function(c) {
     body += c;
    });
    response.on('end', function() {
     console.log(body);
     var message = body;
     callback(message);
    });
  }).on('socket', (socket) => {
    socket.emit('agentRemove');
  });

}


function sendentry(callback) {

  return http.get({
    host: '104.196.44.38',
    port: 3000,
    path: '/message'
  }, function(response) {

    var body = '';
    response.on('data', function(c) {
     body += c;
    });
    response.on('end', function() {
     console.log(body);
     var message = body;
     callback(message);
    });
  }).on('socket', (socket) => {
    socket.emit('agentRemove');
  });

}



function returnResponse() {
  this.emit(':responseReady');
  // response <http.IncomingMessage>
}


const handlers = {
    'NewSession': function () {
        var speechOutput = this.t('WELCOME_MESSAGE', this.t('SKILL_NAME'));
        console.log('hello welcome message');
        console.log(speechOutput);
        // If the user either does not reply to the welcome message or says something that is not
        // understood, they will be prompted again with this text.
        var repromptSpeech = this.t('WELCOME_REPROMPT');
        this.emit(':ask', speechOutput, repromptSpeech);

        console.log('About to create connection');

        this.emit('MoodIntent');

    },
    'MoodIntent': function () {
        console.log('beginning MoodIntent');
        // const input = this.event.request.intent.slots.response;
        var input = util.inspect(this.event.request.type, false, null)

        // let inputPhrase;

        // console.log(inputPhrase);


        // console.log(input);

        console.log(util.inspect(this.event.request.type, false, null))
        console.log('hello hello bye');

        // if (input && input.value) {
        //     inputPhrase = input.value.toLowerCase();
        // }

        // if (input && input) {
        //     input = input.value.toLowerCase();
        // }

        console.log('hello hello 2');


        const cardTitle = this.t('DISPLAY_CARD_TITLE', this.t('SKILL_NAME'), input);

        if (input) {
            console.log('hello hello hello');
            var speechOutput = input;
            var repromptSpeech = this.t('SPEECH_REPEAT_MESSAGE');
            this.emit(':ask', speechOutput, repromptSpeech);

            console.log("about to create the connection to the server");
            createConnection(function(rec) {
              console.log('Creating connection rn');
              var response = "Aside: Connection established";
              this.emit(':tell', response);
              console.log(response);
            })

            sendentry(function(rec) {
              console.log('startig to send entry to server');
              var message = input;
              this.emit(':tell', message);
              console.log(message);
            })

        } else {
            let speechOutput = this.t('SPEECH_NOT_UNDERSTOOD_MESSAGE');
            const repromptSpeech = this.t('COMMAND_NOT_FOUND_REPROMPT');
            if (input) {
                console.log('hello command not found message');
                speechOutput += this.t('COMMAND_NOT_FOUND', input);
            } else {
                speechOutput = this.t('SPEECH_NOT_UNDERSTOOD_MESSAGE');
            }
            speechOutput += repromptSpeech;
          }

            // this.attributes.speechOutput = speechOutput;
            // this.attributes.repromptSpeech = repromptSpeech;

          // this.emit(':ask', speechOutput, repromptSpeech);
    },
    'AMAZON.HelpIntent': function () {
        var speechOutput = '';
        speechOutput += "You can talk to me about anything: the weather, your day, how you feel... don\'t be shy!";
        speechOutput += "Or, you can say exit. Now, what\'s up?",
        this.emit(':ask', speechOutput, speechOutput);
    },
    'AMAZON.RepeatIntent': function () {
        var speechOutput = '';
        speechOutput += "I\'m sorry, I didn\'t get what you said, could you please repeat it?"
        this.emit(":tell", speechOutput, speechOutput);
    },
    'AMAZON.StopIntent': function () {
        endConnection(function(rec) {
          console.log('Ending connection rn');
          var response = "Aside: Connection cut"
          this.emit(':tell', response);
          console.log(response);
        })
        this.emit('SessionEndedRequest');
    },
    'AMAZON.CancelIntent': function () {
        this.emit('SessionEndedRequest');
    },
    'SessionEndedRequest': function () {
        this.emit(':tell', this.t('STOP_MESSAGE'));
    },
};

const languageStrings = {
    'en-US': {
        translation: {
            SKILL_NAME: 'Moody',
            WELCOME_MESSAGE: "Good morning! I\'m %s. How did you sleep last night?",
            WELCOME_REPROMPT: 'For instructions on what you can say, please say help me.',
            DISPLAY_CARD_TITLE: '%s  - %s.',
            STOP_MESSAGE: 'Goodbye! Hope you have a terrific day!',
            SPEECH_REPEAT_MESSAGE: 'Try saying repeat.',
            SPEECH_NOT_UNDERSTOOD_MESSAGE: "I\'m sorry, I currently do not know ",
            COMMAND_NOT_FOUND: 'the recipe for %s. ',
            COMMAND_NOT_FOUND_REPROMPT: 'What else can I help with?',
        },
    },
    'en-GB': {
        translation: {
            SKILL_NAME: 'Moody',
            WELCOME_MESSAGE: "Good morning! I\'m %s. How did you sleep last night?",
            WELCOME_REPROMPT: 'For instructions on what you can say, please say help me.',
            DISPLAY_CARD_TITLE: '%s  - %s.',
            STOP_MESSAGE: 'Goodbye! Hope you have a terrific day!',
            SPEECH_REPEAT_MESSAGE: 'Try saying repeat.',
            SPEECH_NOT_UNDERSTOOD_MESSAGE: "I\'m sorry, I currently do not know ",
            COMMAND_NOT_FOUND: 'the recipe for %s. ',
            COMMAND_NOT_FOUND_REPROMPT: 'What else can I help with?',
        },
    },
    'en-DE': {
        translation: {
            SKILL_NAME: 'Moody',
            WELCOME_MESSAGE: "Good morning! I\'m %s. How did you sleep last night?",
            WELCOME_REPROMPT: 'For instructions on what you can say, please say help me.',
            DISPLAY_CARD_TITLE: '%s  - %s.',
            STOP_MESSAGE: 'Goodbye! Hope you have a terrific day!',
            SPEECH_REPEAT_MESSAGE: 'Try saying repeat.',
            SPEECH_NOT_UNDERSTOOD_MESSAGE: "I\'m sorry, I currently do not know ",
            COMMAND_NOT_FOUND: 'the recipe for %s. ',
            COMMAND_NOT_FOUND_REPROMPT: 'What else can I help with?',
        },
    },
};

exports.handler = function(event, context, callback) {
    var alexa = Alexa.handler(event, context);
    alexa.APP_ID = APP_ID; //optional
    // To enable string internationalization (i18n) features, set a resources object.
    alexa.resources = languageStrings;
    alexa.registerHandlers(handlers);
    alexa.execute();
};
