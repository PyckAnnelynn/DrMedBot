# this file contains the code to use the text analysis from the Comprehend Medical by Amazon
# more info here: https://aws.amazon.com/comprehend/medical/
# getting started here: https://docs.aws.amazon.com/comprehend/latest/dg/get-started-api-med.html#med-examples-python
# categories list here: https://docs.aws.amazon.com/comprehend/latest/dg/extracted-med-info.html#medical-entities-list

import os
# get current directory
package_directory = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level="ERROR", filename=os.path.join(package_directory, '..', '..', 'error.log'), filemode='a', format='%(asctime)s - %(levelname)s - %(message)s in {0}'.format(package_directory), datefmt='%d-%b-%y %H:%M:%S')

def getMedicalEntities(text_to_analyse):
    # import libraries
    import boto3

    try:
        # create a client to make the API calls to Amazon Comprehend Medical
        client = boto3.client(service_name='comprehendmedical')
        # make the call
        result = client.detect_entities(Text= text_to_analyse)
        # catch the result
        entities = result['Entities']

        # return filtered results
        filtered_entities = ""
        for entity in entities:
            if(entity["Category"] == "MEDICAL_CONDITION"):
                text_to_append = ", " + entity["Text"]
                filtered_entities += text_to_append


        # if no entitites were found
        if(filtered_entities == ""):
            return "None"

        # remove first ", "
        return filtered_entities[2:]

    except Exception as e:
        logging.error(e)
        return "None"

# test here
#print(getMedicalEntities("Pt is 40yo mother, highschool teacher HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily,             Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled"))