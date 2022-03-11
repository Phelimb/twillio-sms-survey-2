import os
from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import json
import urllib.request
from replit import db

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
from_number = os.environ['FROM_NUMBER']
client = Client(account_sid, auth_token)

# RETURN_URL = "https://frailenchantingparentheses.phelimbradley.repl.co/sms-response"
return_url = os.environ['RETURN_URL'] 

app = Flask('app')



@app.route('/')
def hello_world():
  return '<h1>Hello, World!</h1>'

def get_results_so_far(question):
  try:
    return json.loads(db[question])
  except:
    db[question] = json.dumps({})
    return get_results_so_far(question)
  
def update_results_so_far(question, response):
  data=get_results_so_far(question)
  response_key=str(response)
  if data.get(response_key) is None:
    data[response_key]=0
  data[response_key]=data[response_key]+1
  db[question]=json.dumps(data)
  return data

def results_so_far_to_string(results):
  res=""
  for k,v in results.items():
    res+=k + ": " + str(v)
    res+="\n"
  return res
    
  
@app.route('/recieve-sms', methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()
    number=request.values['From']
    body=request.values['Body']
    

    try:
      response_index=int(body.strip())
      response_string=db[number]["responses"][response_index-1]
      question=db[number]["question"]
    except:
      resp.message("We couldn't find the survey. Have you already responded? ")
    else:
      try: 
        update_results_so_far(question,response_string)
        
        return_value = {"response":response_string,"number":number, "question":question,"results":results_so_far_to_string(get_results_so_far(question))}
        
        req = urllib.request.Request(return_url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(return_value)
        jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
        req.add_header('Content-Length', len(jsondataasbytes))
        post_response = urllib.request.urlopen(req, jsondataasbytes)
        
        del db[number]
        # Add a message
        resp.message("Thank you for answering our survey with: "+response_string +"\n\nResults so far: "+results_so_far_to_string(get_results_so_far(question)))
      except:
        resp.message("Hmm, we couldn't read your reply. Please try with a number 1-"+str(len(db[number]["responses"])))
      else:
                ## New responses
        latest=json.loads(db["latest"]) 
        latest["responses"].append(return_value)
        db["latest"] = json.dumps(latest)


  

    return str(resp)

@app.route('/send-sms/', methods=['GET', 'POST'])
def send_sms():

  '''
  {"question":"What's your fovorite ice cream", responses:["Choc", "Vanilla"], "numbers":[124,1234]}
  '''
  data=request.get_json() 

  body = "This is a very important survey from Prolific. You will be paid £0.00 for it's completion. \n\n"
  body += data["question"]
  for i,response in enumerate(data["responses"]):
    body+="\n"+str(i+1)+". " + response
  body += "\n Please reply with a number only. "
  print(body)
  
  for number in data["numbers"]:
    print(number)
    db[number]=data
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

@app.route('/new-responses', methods=['GET'])
def new_responses():

  latest=json.loads(db["latest"])
  db["latest"]=json.dumps({"responses":[]})
  
  response = app.response_class(
        response=json.dumps(latest),
        status=200,
        mimetype='application/json'
    )
  return response
  
app.run(host='0.0.0.0', port=8080)