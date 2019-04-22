from google.oauth2 import service_account
import googleapiclient.discovery
# import general methods to reply to DialogFlow
from dialogflow_webhook.dialogflowResponses import rich_response_with_suggestions_and_contexts, simple_final_response

from flask import Flask, request, jsonify, render_template
app = Flask(__name__)

import os
# get current directory
package_directory = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level="ERROR", filename=os.path.join(package_directory, '..', 'error.log'), filemode='a', format='%(asctime)s - %(levelname)s - %(message)s in {0}'.format(package_directory), datefmt='%d-%b-%y %H:%M:%S')


# method to safely retrieve project id
def getProjectId():
    import csv

    try:
        # open file
        with open(os.path.join(package_directory, '..', 'dialogflow_webhook', 'NNModels', 'config.csv'), 'r') as csvfile:
            keyreader = csv.reader(csvfile, delimiter=';')
            for row in keyreader:
                if(row[0] == "Dialogflow Project ID"):
                    return row[1]

    except FileNotFoundError:
        logging.error("Couldn't open config file because it was not found.")

# Google OAUTH2 Credentials
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
SERVICE_ACCOUNT_FILE = os.path.join(package_directory, "..", "dialogflow_webhook", "medbot-b9f16-9d80b50b78b2.json")

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = googleapiclient.discovery.build('dialogflow', 'v2beta1', credentials=credentials)

# set variables
path = service.projects().agent().sessions()

# receive responses from dialogflow
def detect_intent_texts(session_id, text, language_code):
    try:

        # send right answer
        body = {"queryInput": {"text": {"text": text, "languageCode": language_code}}}
        # make request, make sure the .execute() method gets called
        req = path.detectIntent(session=session_id, body=body).execute()

        return req

    except Exception as e:
        logging.error(e)
        # send something to trigger a fallback intent
        body = {"queryInput": {"text": {"text": "something wrong", "languageCode": language_code}}}
        # make request
        req = path.detectIntent(session=session_id, body=body).execute()
        return req

# sends message to dialogflow
@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        # get the user typed message from the form
        message = request.form['message']
        # set the project id
        project_id = getProjectId()
        # set the session id
        current_session = f"projects/{project_id}/agent/sessions/1"
        # receive JSON as response
        req = detect_intent_texts(current_session, message, 'en-gb')

        # return response to dialogFlow
        return jsonify(req)

    except Exception as e:
        logging.error(e)
        return simple_final_response("Sorry, something went wrong.")

@app.route('/')
def index():
    return render_template('index.html')

# run Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=80)