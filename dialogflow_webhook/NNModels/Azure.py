# this file contains the code to use the text analysis from the cognitive services by Azure
# more info here: https://azure.microsoft.com/en-gb/services/cognitive-services/text-analytics/
# getting started here: https://docs.microsoft.com/en-gb/azure/cognitive-services/text-analytics/quickstarts/python
# specific for medicine here: https://azure.microsoft.com/en-us/industries/healthcare/
import os
# get current directory
package_directory = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level="ERROR", filename=os.path.join(package_directory, '..', '..', 'error.log'), filemode='a', format='%(asctime)s - %(levelname)s - %(message)s in {0}'.format(package_directory), datefmt='%d-%b-%y %H:%M:%S')

def getAzureKey():
    import csv

    try:
        # open file
        with open(os.path.join(package_directory,'config.csv'), 'r') as csvfile:
            keyreader = csv.reader(csvfile, delimiter=';')
            for row in keyreader:
                if(row[0] == "AZURE_KEY"):
                    return row[1]

    except FileNotFoundError:
        logging.error("Couldn't open config file because it was not found.")

def getLinks(text_to_analyse):
    # import libraries
    import requests
    import json

    try:
        # necessary data to make request
        url = 'https://westeurope.api.cognitive.microsoft.com/text/analytics/v2.0/entities'
        AzureKey = getAzureKey()
        headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": AzureKey}
        body = {
          "documents": [
            {
              "language": "en",
              "id": "1",
              "text": text_to_analyse
            }
          ]
        }

        # make API call
        response = requests.post(url, headers=headers, data=json.dumps(body))
        # convert string to json
        json = json.loads(response.text)
        # clean up JSON
        filtered_entities = ""
        for entity in json["documents"][0]["entities"]:
            text_to_append = ", " + entity["wikipediaUrl"]
            filtered_entities += text_to_append

        if (filtered_entities == ""):
            return "None"

        # remove first ", "
        return filtered_entities[2:]

    except Exception as e:
        logging.error(e)
        return "None"

# Test here
#print(getLinks("Test 123 test. Windows 10 should be an entity and so should Apple."))