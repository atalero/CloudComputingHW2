import dateutil.parser
import datetime
import time
import os
import logging
import json
import urllib2
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class LexEvent:
    def __init__(self, event):
        self.event = event
        self.slots = event['currentIntent']['slots']
        self.intent = event['currentIntent']['name']
        self.attr = event['sessionAttributes']
        self.src = event['invocationSource']

        self.location = self.slots["Location"]
        self.cuisine = self.slots["Cuisine"]
        self.sz = self.slots["Size"]
        self.dt = self.slots["Date"]
        self.tm = self.slots["Time"]
        self.phone = self.slots["Phone"]


    def delegate(self):
        return {
            'sessionAttributes': self.attr,
            'dialogAction': {
                'type': 'Delegate',
                'slots': self.slots
            }
        }


    def fulfill(self):
        sqs = boto3.resource('sqs')
        try:
            q = sqs.get_queue_by_name(QueueName='DiningBotQueue')
            resp = q.send_message(MessageBody=json.dumps(self.slots))
            print resp

            if resp['ResponseMetadata']['HTTPStatusCode'] == 200:
                return self.close("You are all set. You will receive my recommendations shortly at " + str(self.phone) + ".")
            else:
                return self.close("I'm unable to process this request currently. Please try again later.")
        except:
            return self.close("I'm unable to process this request currently. Please try again later.")



    def close(self, message):
        return {
            'sessionAttributes': self.attr,
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Fulfilled',
                'message': {'contentType': 'PlainText', 'content': message }
            }
        }



    def elicit_slot(self, slot_to_elicit, message):
        return {
            'sessionAttributes': self.attr,
            'dialogAction': {
                'type': 'ElicitSlot',
                'intentName': self.intent,
                'slots': self.slots,
                'slotToElicit': slot_to_elicit,
                'message': {'contentType': 'PlainText', 'content': message }
            }
        }


    def validate_dining(self):

        res = {
            'isValid': True,
            'violatedSlot': 'None',
            'message': {'contentType': 'PlainText', 'content': 'Slots Valid'}
        }
        if self.dt is not None:
            if not isvalid_date(self.dt):
                res['isValid'] = False
                res['violatedSlot'] = 'Date'
                res['message'] = 'I did not understand that. On what date would you like to dine out?'
                return res

            fmt_dt = datetime.datetime.strptime(self.dt, '%Y-%m-%d').date()

            if fmt_dt < datetime.date.today():
                #Can't change the past
                res['isValid'] = False
                res['violatedSlot'] = 'Date'
                res['message'] = "It's too late to plan for the past. What date would you like to dine out?"
                return res

        if self.sz is not None:
            if int(self.sz) <= 0:
                # Not enough people
                res['isValid'] = False
                res['violatedSlot'] = 'Size'
                res['message'] = "That's not enough people to dine out. How many people are there in your party?"
                return res

        return res




""" --- Helper Functions --- """

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False



""" --- Functions that control the bot's behavior --- """

def dining_sugg(lex):
    """
    Performs dialog management and fulfillment.
    """

    # Perform basic validation on the supplied input slots.
    # Use the elicitSlot dialog action to re-prompt for the first violation detected.

    res = lex.validate_dining()
    if not res['isValid']:
        lex.slots[res['violatedSlot']] = None
        return lex.elicit_slot(res['violatedSlot'], res['message'])

    if lex.src == 'DialogCodeHook':
        return lex.delegate()
    else:
        return lex.fulfill()

#   lex.close()
#    return lex.delegate()




def unknown_intent(lex):
    return lex.close("I did not understand that. Please try again.")



""" --- Intents --- """

def dispatch(lex):
    """
    Called when the user specifies an intent for this bot.
    """
    if lex.intent == 'DiningSuggestionsIntent':
        return dining_sugg(lex)

    return unknown_intent(lex)



""" --- Main handler --- """

def lambda_handler(event, context):
    lex = LexEvent(event)
    logger.info(('IN', event))

    try:
        result = dispatch(lex)
        logger.info(('OUT', result))
        return result
    except Exception as e:
        logger.error(e)
