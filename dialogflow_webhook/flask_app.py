#!/usr/bin/python3.7
# -*- coding: utf8 -*-

import os
# get current directory
package_directory = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level="INFO", filename=os.path.join(package_directory, '..', 'error.log'), filemode='a', format='%(asctime)s - %(levelname)s - %(message)s in {0}'.format(package_directory), datefmt='%d-%b-%y %H:%M:%S')

# setup flask
from flask import Flask, request
app = Flask(__name__)

# import general methods to reply to DialogFlow
from dialogflow_webhook.dialogflowResponses import rich_response_with_suggestions_and_contexts, simple_response_with_contexts, simple_final_response

# random module to select random sentence from the list
import random
repeat_sentences_eng = ["Let me repeat that for you. ",
                        "",
                        "No problem. ",
                        "I'll repeat that. ",
                        "I am going to repeat what I just said. ",
                        "This is what I just said: ",
                        "Here is what I just said: "]
not_understood_sentences_eng = ["Sorry, I didn't understand you. ",
                                "I did not understand you. ",
                                "I don't understand. ",
                                "Apologies, I didn't understand that. ",
                                "I didn't quite understand that. ",
                                "I didn't catch that. ",
                                "I didn't understand. "]
number_of_not_understood_sentences = len(not_understood_sentences_eng)-1
number_of_repeat_sentences = len(repeat_sentences_eng)-1

# variables to store parameters in
received_text = ""
received_icd_codes = ""

# webhook to handle POST request by DialogFlow
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # make variables usable across calls
        global received_text
        global received_icd_codes
        logging.info(f"received text from user: {received_text}")
        logging.info(f"received icd codes from user: {received_icd_codes}")

        # get JSON
        req = request.get_json(silent=True, force=True)
        logging.info(f"received from dialoglow {req.get('queryResult')}")
        session = req.get('session').split('/')
        projectId = session[1]
        sessionId = session[4]
        parameters = req.get('queryResult').get('parameters')
        queryText = req.get('queryResult').get('queryText')
        intentName = req.get('queryResult').get("intent").get("displayName")
        language = req.get('queryResult').get('languageCode')

        # if-structure for when more languages get added
        if("en" in language):
            # set response for the intent called "0_topic"
            if intentName == "0_topic":
                fulfillment = "Hello, how can I help you today?"
                suggestions = ["Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_topic - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "What do you want me to do?"
                suggestions = ["Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_topic - repeat":
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "What can I do for you today?"
                suggestions = ["Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)

            #region analyse text branch
            elif intentName == "0_1_text":
                fulfillment = "Please provide the text you want to get analysed. Start your answer with the word 'text' please."
                return simple_response_with_contexts(fulfillment, ["0_1_text", "0_1_text-followup"], projectId, sessionId)
            elif intentName == "0_1_text - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "Please provide the text you want to get analysed. Start your answer with the word 'text' and do not exceed the character limit of 256, please."
                return simple_response_with_contexts(fulfillment, ["0_1_text", "0_1_text-followup"], projectId, sessionId)
            elif intentName == "0_1_text - repeat":
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "Please provide the text you want to get analysed. Start your answer with the word 'text' please."
                return simple_response_with_contexts(fulfillment, ["0_1_text", "0_1_text-followup"], projectId, sessionId)

            ## options to analyse the text
            elif intentName == "0_1_0_analyse":
                received_text = queryText
                import re
                received_text = re.sub('text[^A-Za-z0-9]+', '', received_text) # remove the "text" word from the beginning of the text
                fulfillment = "Thank you, what do you want to know?"
                suggestions = ["Get relevant medical data", "Search key words", "Translate"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions,["0_1_text", "0_1_0_analyse", "0_1_0_analyse-followup"], projectId, sessionId)
            elif intentName == "0_1_0_analyse - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "What do you want to know?"
                suggestions = ["Get relevant medical data", "Search key words", "Translate"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_1_text", "0_1_0_analyse", "0_1_0_analyse-followup"], projectId, sessionId)
            elif intentName == "0_1_0_analyse - repeat":
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "What do you want to know?"
                suggestions = ["Get relevant medical data", "Search words", "Translate"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_1_text", "0_1_0_analyse", "0_1_0_analyse-followup"], projectId, sessionId)

            ## relevant medical data branch
            elif intentName == "0_1_0_0_relevant":
                from dialogflow_webhook.NNModels import AWS
                relevant = AWS.getMedicalEntities(received_text)
                fulfillment = "These are the medical conditions I found: {0}. Is there anything else I can do for you?".format(relevant)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_1_0_0_relevant - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "Is there anything else I can do for you?"
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_1_0_0_relevant - repeat":
                from dialogflow_webhook.NNModels import AWS
                relevant = AWS.getMedicalEntities(received_text)
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "These are the medical conditions I found: {0}. Is there anything else I can do for you?".format(relevant)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)

            ## key words branch
            elif intentName == "0_1_0_1_keywords":
                from dialogflow_webhook.NNModels import Azure
                keywords = Azure.getLinks(received_text)
                fulfillment = "These are the links I found: {0}. Is there anything else I can do for you?".format(keywords)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_1_0_1_keywords - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "Is there anything else I can do for you?"
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_1_0_1_keywords - repeat":
                from dialogflow_webhook.NNModels import Azure
                keywords = Azure.getLinks(received_text)
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "These are the links I found: {0}. Is there anything else I can do for you?".format(keywords)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)

            ## translate branch
            elif intentName == "0_1_0_2_translate":
                fulfillment = "Sorry, this feature has not been implemented yet. Is there anything else I can do for you?"
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_1_0_2_translate - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "Sorry, this feature has not been implemented yet. Is there anything else I can do for you?."
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_1_0_2_translate - repeat":
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "Sorry, this feature has not been implemented yet. Is there anything else I can do for you?"
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            #endregion

            #region analyse ICD codes branch
            elif intentName == "0_0_icd":
                fulfillment = "Please provide the ICD code(s) in ICD-9 format."
                return simple_response_with_contexts(fulfillment, ["0_0_icd", "0_0_icd-followup"], projectId, sessionId)
            elif intentName == "0_0_icd - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "Please provide the ICD code(s) in ICD-9 format. Do not provide more than 100 ICD codes or more than 256 characters, please."
                return simple_response_with_contexts(fulfillment, ["0_0_icd", "0_0_icd-followup"], projectId, sessionId)
            elif intentName == "0_0_icd - repeat":
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "Please provide the ICD code(s) in ICD-9 format."
                return simple_response_with_contexts(fulfillment, ["0_0_icd", "0_0_icd-followup"], projectId, sessionId)

            ## receive ICD codes
            elif intentName == "0_0_0_kind":
                received_icd_codes = parameters
                fulfillment = "What kind of ICD codes did you just give me?"
                suggestions = ["Diagnosis", "Procedure"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_0_icd", "0_0_0_kind", "0_0_0_kind-followup"], projectId,sessionId)
            elif intentName == "0_0_0_kind - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "What kind of ICD codes did you just give me?"
                suggestions = ["Diagnosis", "Procedure"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_0_icd", "0_0_0_kind", "0_0_0_kind-followup"], projectId, sessionId)
            elif intentName == "0_0_0_kind - repeat":
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "What kind of ICD codes did you just give me?"
                suggestions = ["Diagnosis", "Procedure"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_0_icd", "0_0_0_kind", "0_0_0_kind-followup"], projectId, sessionId)

            ## diagnosis codes
            elif intentName == "0_0_0_0_diagnosis":
                fulfillment = "Thank you, what do you want to know?"
                suggestions = ["Duration hospital stay", "Predict E-codes"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_0_icd", "0_0_0_0_diagnosis", "0_0_0_0_diagnosis-followup"], projectId, sessionId)
            elif intentName == "0_0_0_0_diagnosis - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "What do you want to know?"
                suggestions = ["Duration hospital stay", "Predict E-codes"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_0_icd", "0_0_0_0_diagnosis", "0_0_0_0_diagnosis-followup"], projectId, sessionId)
            elif intentName == "0_0_0_0_diagnosis - repeat":
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "What do you want to know?"
                suggestions = ["Duration hospital stay", "Predict E-codes"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_0_icd", "0_0_0_0_diagnosis", "0_0_0_0_diagnosis-followup"], projectId, sessionId)

            ## procedure codes
            elif intentName == "0_0_0_1_procedure":
                fulfillment = "Thank you, what do you want to know?"
                suggestions = ["Next Procedure"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_0_icd", "0_0_0_1_procedure", "0_0_0_1_procedure-followup"], projectId, sessionId)
            elif intentName == "0_0_0_1_procedure - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "What do you want to know?"
                suggestions = ["Next Procedure"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_0_icd", "0_0_0_1_procedure", "0_0_0_1_procedure-followup"], projectId, sessionId)
            elif intentName == "0_0_0_1_procedure - repeat":
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "What do you want to know?"
                suggestions = ["Next Procedure"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_0_icd", "0_0_0_1_procedure", "0_0_0_1_procedure-followup"], projectId, sessionId)

            ## duration
            elif intentName == "0_0_0_0_0_duration":
                from dialogflow_webhook.NNModels import OwnModels
                duration = OwnModels.getDurationFromDiagnosis(received_icd_codes)
                fulfillment = "I estimate the patient will have to stay {0} days in the hospital. Is there anything else I can do for you?".format(duration)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_0_0_0_0_duration - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "Is there anything else I can do for you?"
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_0_0_0_0_duration - repeat":
                from dialogflow_webhook.NNModels import OwnModels
                duration = OwnModels.getDurationFromDiagnosis(received_icd_codes)
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "I estimate the patient will have to stay {0} days in the hospital. Is there anything else I can do for you?".format(duration)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)

            ## e-codes
            elif intentName == "0_0_0_0_1_ecode":
                from dialogflow_webhook.NNModels import OwnModels
                ecode = OwnModels.getEcodeFromDiagnosis(received_icd_codes)
                fulfillment = "This is the e-code I think fits best: {0}. Is there anything else I can do for you?".format(ecode)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_0_0_0_1_ecode - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "Is there anything else I can do for you?"
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            elif intentName == "0_0_0_0_1_ecode - repeat":
                from dialogflow_webhook.NNModels import OwnModels
                ecode = OwnModels.getEcodeFromDiagnosis(received_icd_codes)
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "This is the e-code I think fits best: {0}. Is there anything else I can do for you?".format(ecode)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)

            ## next procedure
            elif intentName == "0_0_0_1_0_next":
                from dialogflow_webhook.NNModels import OwnModels
                procedure = OwnModels.getNextProcedure(received_icd_codes)
                fulfillment = "This is the next procedure I think fits best: {0}. Is there anything else I can do for you?".format(procedure)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)

            elif intentName == "0_0_0_1_0_next - fallback":
                fulfillment = not_understood_sentences_eng[random.randint(0, number_of_not_understood_sentences)]
                fulfillment += "Is there anything else I can do for you?"
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)

            elif intentName == "0_0_0_1_0_next - repeat":
                from dialogflow_webhook.NNModels import OwnModels
                procedure = OwnModels.getNextProcedure(received_icd_codes)
                fulfillment = repeat_sentences_eng[random.randint(0, number_of_repeat_sentences)]
                fulfillment += "This is the next procedure I think fits best: {0}. Is there anything else I can do for you?".format(procedure)
                suggestions = ["No", "Analyse some ICD codes", "Analyse some text"]
                return rich_response_with_suggestions_and_contexts(fulfillment, suggestions, ["0_topic", "0_topic-followup"], projectId, sessionId)
            #endregion

            # closing intent
            elif "no" in intentName:
                received_text = ""
                received_icd_codes = ""
                fulfillment = "Okay, I hope I was able to help you. Goodbye."
                return simple_final_response(fulfillment)

            # something wrong intent
            elif intentName == "Default Fallback":
                received_text = ""
                received_icd_codes = ""
                fulfillment = "Sorry, something went wrong. Please start over."
                return  simple_final_response(fulfillment)

    except Exception as e:
        logging.error(e)
        received_text = ""
        received_icd_codes = ""
        return simple_final_response("Sorry, something went wrong.")


# run Flask app
if __name__ == "__main__":
    app.run(debug=True)