import os
from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import json
import urllib.request

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
from_number = os.environ['FROM_NUMBER']
client = Client(account_sid, auth_token)

# RETURN_URL = "https://frailenchantingparentheses.phelimbradley.repl.co/sms-response"
RETURN_URL = "https://hooks.zapier.com/hooks/catch/5919068/bs3iuuf/"


app = Flask('app')



@app.route('/')
def hello_world():
  return '<h1>Hello, World!</h1>'

@app.route('/recieve-sms', methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()
    try: 
      response=int(request.values['Body'].strip())
  
      return_value = {"response":request.values['Body'],"number":request.values['From']}
  
      req = urllib.request.Request(RETURN_URL)
      req.add_header('Content-Type', 'application/json; charset=utf-8')
      jsondata = json.dumps(return_value)
      jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
      req.add_header('Content-Length', len(jsondataasbytes))
      post_response = urllib.request.urlopen(req, jsondataasbytes)
      # Add a message
      resp.message("Thank you for answering our survey with: "+str(response))
    except:
      resp.message("Hmm, we couldn't read your reply. Please try with a number 1-10.")

    return str(resp)

@app.route('/send-sms/', methods=['GET', 'POST'])
def send_sms():

  '''
  {"question":"What's your fovorite ice cream", responses:["Choc", "Vanilla"], "numbers":[124,1234]}
  '''
  data=request.get_json() 

  body = data["question"]
  for i,response in enumerate(data["responses"]):
    body+="\n"+str(i+1)+". " + response
  body += "\n Please reply with a number only. "
  print(body)
  
  for number in data["numbers"]:
    print(number)
    message = client.messages \
                .create(
                     body=body,
                     from_=from_number,
                     to=number
                 )
  
  return ""

@app.route('/sms-response', methods=['GET', 'POST'])
def sms_response():

  print(request.get_json() )
  
  return ""
  
app.run(host='0.0.0.0', port=8080)