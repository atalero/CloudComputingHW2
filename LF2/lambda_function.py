from __future__ import print_function
import json, urllib, requests, datetime, boto3, re, logging

API_KEY = "AIzaSyCzojnMKr_DT4tXG3VuDMNo8HeUvYoByuY"
#url for the text search Google API
TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

#details URL from Google place details API
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
DETAILS_PARAMS = {"fields": "opening_hours,website,formatted_phone_number", "key": API_KEY, "place_id": ""}

MAX_SUGGESTIONS = 10

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Suggestions')
sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/677041989318/DiningBotQueue'

# Initialize logger and set log level
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SNS client for N.Virginia region
session = boto3.Session(
    region_name="us-east-1"
)
sns_client = session.client('sns')


#edits the format of a phone number so that it is understood by SNS
def check_number(number):
	
	#if no country code is provided, assume US number (add +1)
	if not bool(re.search("^[+]{1}", number)):
	    number = "+1" + number
	
	new_number = ""
	for letter in number:
	    if bool(re.search("[0-9+]", letter)):
	        new_number += letter
	return new_number

def send_sms(final_suggestions_dict, customer_phone_number):
	text_string = "Here are your suggestions: \n\n"
	
	#produce text string to send via SMS to customer
	for suggestion in final_suggestions_dict:
		name = suggestion
		address = final_suggestions_dict[suggestion]["formatted_address"]
		phone_number = final_suggestions_dict[suggestion]["formatted_phone_number"]
		
		text_string += name + " address: " + address + " phone_number: " + phone_number + "\n\n"
	
	#format the phone number correctly
	customer_phone_number = check_number(customer_phone_number)
	
	if len(final_suggestions_dict) == 0:
		text_string = "Sorry, we could not find any suggestions with your preferences"
	
	#deliver text message
	response = sns_client.publish(
	    PhoneNumber = customer_phone_number,
	    Message = text_string,
	    MessageAttributes={
	        'AWS.SNS.SMS.SenderID': {
	            'DataType': 'String',
	            'StringValue': 'SENDERID'
	        },
	        'AWS.SNS.SMS.SMSType': {
	            'DataType': 'String',
	            'StringValue': 'Promotional'
	        }
	    }
	)

	logger.info(response)
    
	print('Text Sent to ' + customer_phone_number)
	
def add_to_dynamo(data):
    response = table.put_item(
       Item= data
    )

#returns true if the restaurant is open at the time of reservation
#TRIED AND TESTED (see notebook)
def check_if_open(periods, weekday, int_time):
	for period in periods:
		open_day = period["close"]["day"]
		close_day = period["open"]["day"]
		open_time = int(period["open"]["time"])
		close_time = int(period["close"]["time"])

		open_days = [open_day]
		i = open_day
		while i != close_day:
		    i = (i+1)%7
		    open_days.append(i)

		if (weekday in open_days):
			if weekday == open_day and int_time <= open_time:
				return False
			if weekday == close_day and int_time >= close_time:
				return False

	return True

def lambda_handler(event, context):
	suggestions_dict = {}
	final_suggestions_dict = {}
	
	#{"Cuisine": "Thai", "Phone": "111", "Location": "New York", "Time": "23:00", "Date": "2018-11-30", "Size": 5}
	
	
	# Receive message from SQS queue
	response = sqs.receive_message(
	    QueueUrl=queue_url,
	    AttributeNames=[
        	'SentTimestamp'
	    ],
	    MaxNumberOfMessages=1,
	    MessageAttributeNames=[
        	'All'
	    ],
	    VisibilityTimeout=0,
	    WaitTimeSeconds=0
	)
	
	try:
		message = response['Messages'][0]
		receipt_handle = message['ReceiptHandle']
	except:
		print("No message in queue")
		return
	
	# Delete received message from queue
	sqs.delete_message(
		QueueUrl=queue_url,
		ReceiptHandle=receipt_handle
	)
	
	decode = json.loads(message["Body"])
	
	#print(message_json["Cuisine"])
	#print(message["Body"])
	
	#save all parameters in variables
	user_number = decode["Phone"]
	cuisine_type = decode["Cuisine"]
	location = decode["Location"]
	time = decode["Time"]
	date = decode["Date"]
	num_people = decode["Size"]
	
	#print(decode["Location"]) TRIED AND TESTED

	#format date
	year, month, day = (int(x) for x in date.split('-'))    
	weekday = datetime.date(year, month, day).weekday()
	weekday = (weekday + 1)%7 #match the indecing for weekdays from Google API's
	time = time.split(":")
	int_time = int("".join(time))
	
	#build the text search request and make the request
	query_string = cuisine_type +" restaurants in " + location
	PARAMS = {"key":API_KEY, "query": query_string, "type" :"restaurant"}
	r = requests.get(url = TEXT_SEARCH_URL, params = PARAMS)
	data = r.json()
	
	count = 0
	for result in data["results"]:
		if count == MAX_SUGGESTIONS:
			break
		name = result["name"]
		suggestions_dict[name] = {}
		suggestions_dict[name]["name"] = name
		suggestions_dict[name]["place_id"] = result["place_id"] 
		suggestions_dict[name]["formatted_address"] = result["formatted_address"] 
		count += 1
	
	#susggestions dict format
	#{"Wasana's Thai Restaurant": {'place_id': 'ChIJaekGKHW93YkRurVMHxugaT4', 'formatted_address': '1425, 336 Main St, Catskill, NY 12414, United States'}, 'New York Restaurant': {'place_id': 'ChIJaY-jygq93YkRVFCSDZs_2do', 'formatted_address': '353 Main St, Catskill, NY 12414, USA'}
	
	#get contact details
	for suggestion in suggestions_dict:
		if len(suggestions_dict) == 0:
			print("No suggestions available")
			return
		
		DETAILS_PARAMS["place_id"] = suggestions_dict[suggestion]["place_id"]
		details_request = requests.get(url = DETAILS_URL, params = DETAILS_PARAMS)
		details_data = details_request.json()
		
		#opening_hours, website,formatted_phone_number
		
		try:
			suggestions_dict[suggestion]["opening_hours"] = details_data["result"]["opening_hours"]["periods"]
		except:
			suggestions_dict[suggestion]["opening_hours"] = None
		
		try:
			suggestions_dict[suggestion]["formatted_phone_number"] = details_data["result"]["formatted_phone_number"]
		except:
			suggestions_dict[suggestion]["formatted_phone_number"] = "Unknown"
		
		#delete places that are NOT open at the requested time
		if suggestions_dict[suggestion]["opening_hours"] == None:
			continue
		
		try:
			if check_if_open(suggestions_dict[suggestion]["opening_hours"], weekday, int_time):
				final_suggestions_dict[suggestion] =  suggestions_dict[suggestion]
				add_to_dynamo(suggestions_dict[suggestion])
		except:
			final_suggestions_dict[suggestion] =  suggestions_dict[suggestion]
			add_to_dynamo(suggestions_dict[suggestion])
	
	#Return via SNS
	send_sms(final_suggestions_dict, user_number)

