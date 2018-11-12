from bot_request import BotRequest  
from bot_response import BotResponse 
from error import Error
from message import Message
import boto3

def produce_reply_string(user_text, id):
    """ Return a reply string basedo on the response from Lex """
    client = boto3.client('lex-runtime')
    
    response = client.post_text(
            botName = "GetDiningSuggestions",
            botAlias = "DiningChatbot",
            userId = id,
            inputText = user_text
        )

    return (response["message"])

def send_message(message, context):  # noqa: E501
    """The endpoint for the Natural Language Understanding API.

    This API takes in one or more messages from the client and returns one or more messages as a response. The API leverages the NLP backend functionality, paired with state and profile information and returns a context-aware reply.  # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: BotResponse
    """
    bot_reply = BotResponse()
    
    for element in message["messages"]:
        #params to pass to Lex
        text = element["unstructured"]["text"]
        id = element["unstructured"]["id"]
        
        #test
        response = produce_reply_string(text, id)
        
        new_message = Message("type1", response)
        
        bot_reply.add_message(new_message)
        
        return bot_reply.asdict()


