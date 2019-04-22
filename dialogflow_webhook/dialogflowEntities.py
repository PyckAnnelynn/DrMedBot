# this file can be used to upload entities to dialogflow
# do not execute without any reason
import os
# get current directory
package_directory = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level="ERROR", filename=os.path.join(package_directory, '..', 'error.log'), filemode='a', format='%(asctime)s - %(levelname)s - %(message)s in {0}'.format(package_directory), datefmt='%d-%b-%y %H:%M:%S')

# method to safely retrieve project id
def getProjectId():
    import csv

    try:
        with open(os.path.join(package_directory, 'NNModels', 'config.csv'), 'r') as csvfile:
            keyreader = csv.reader(csvfile, delimiter=';')
            for row in keyreader:
                if(row[0] == "Dialogflow Project ID"):
                    return row[1]

    except FileNotFoundError:
        logging.ERROR("Couldn't open config file because it was not found.")


# method to get ICD codes from file
def getICDcodes():
    import numpy as np
    icd_codes = np.load('../model_training/icd_diagnosis.npy').item()
    return list(icd_codes)[:9999] # entities in dialogflow are limited to 10000

# convert dictionary to list of entities
def convertListToEntities(icd_list):
    entities = []
    # loop over all ICdD codes
    for icdCode in icd_list:
        # if icdCode happens to be an int (there is one code that's just 0 which means none)
        if type(icdCode) == int:
            # convert to string
            icdCode = str(icdCode)
        # convert to entity
        entity = {"value": icdCode, "synonyms": [icdCode]}
        # add to list
        entities.append(entity)

    return entities

# gives an error but still works :)
from google.oauth2 import service_account
import googleapiclient.discovery

# set credentials
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
SERVICE_ACCOUNT_FILE = 'medbot-b9f16-9d80b50b78b2.json'

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = googleapiclient.discovery.build('dialogflow', 'v2beta1', credentials=credentials)

# set variables
project_id = getProjectId()
entities = convertListToEntities(getICDcodes())

def create_entities(project_id, entities):
    try:

        # send entities to dialogflow
        body = {
                  "displayName": "ICD9",
                  "kind": "KIND_LIST",
                  "autoExpansionMode": "AUTO_EXPANSION_MODE_UNSPECIFIED",
                  "entities": entities
                }

        # more paths can be found here:
        # https://developers.google.com/resources/api-libraries/documentation/dialogflow/v2beta1/python/latest/dialogflow_v2beta1.projects.html
        path = service.projects().agent().entityTypes()

        # make request, make sure the .execute() method gets called
        req = path.create(parent=f'projects/{project_id}/agent', body=body).execute()
        return req


    except Exception as e:
        logging.error(e)

# call the function to create entities, won't work if the enities exist already!
create_entities(project_id, entities)