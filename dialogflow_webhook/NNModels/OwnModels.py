# this file contains the code to use self-trained models
import keras
import os
# get current directory
package_directory = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level="ERROR", filename=os.path.join(package_directory, '..', '..', 'error.log'), filemode='a', format='%(asctime)s - %(levelname)s - %(message)s in {0}'.format(package_directory), datefmt='%d-%b-%y %H:%M:%S')

# method to get ICD codes from file
def getICDcodes():
    import numpy as np

    try:
        icd_codes = np.load(os.path.join(package_directory, '..', '..', 'model_training','icd_diagnosis.npy')).item()

        return dict(icd_codes)

    except Exception as e:
        logging.error(e)

# convert to integer value
def convertICDtoInt(icd):
    icd9codes_dict = getICDcodes()

    for key, value in icd9codes_dict.items():
        # convert number to ICD code
        if (key == icd):
            return value

    return 0

# convert back to ICD code
def convertIntToICD(int):
    icd9codes_dict = getICDcodes()

    for key, value in icd9codes_dict.items():
        # convert number to ICD code
        if (value == int):
            return key

    return 0

# add padding so the list is the same size as the lists the model was trained on
def addPadding(received_diagnosis, padding_length):
    padded_diagnosis = list(received_diagnosis)

    if (len(received_diagnosis) < padding_length):
        for i in range(len(received_diagnosis), padding_length):
            padded_diagnosis.append(0)
    elif(len(received_diagnosis) > padding_length):
        padded_diagnosis=received_diagnosis[0:padding_length]

    return padded_diagnosis

# convert padded diagnosis to numpy array so model understands
def convertDiagnosisToX(diagnosis):
    import numpy as np

    # convert diagnosis to integers as in the model
    icd9_dict = getICDcodes()
    for i in range(0, len(diagnosis)):
        diagnosis[i] = convertICDtoInt(diagnosis[i])

    # convert list to numpy array + reshape so the model won't nag
    X = np.asarray(diagnosis)
    X = X.reshape([1, 20])

    return X

def getDurationFromDiagnosis(diagnosis):
    import numpy as np
    try:
        # add padding to diagnosis
        diagnosis = addPadding(diagnosis, 20)

        # convert padded diagnosis to numpy array so model understands
        X = convertDiagnosisToX(diagnosis)

        # load the model from disk
        modelname = os.path.join(package_directory, '..', '..', 'model_training', 'model_diagnosis_stay.h5') #edit this before handing in your code
        model = keras.models.load_model(modelname)

        # make a prediction
        daysInHospital = model.predict(X)

        # round to zero decimals
        return np.round(daysInHospital[0][0])

    except Exception as e:
        logging.error(e)
        return 0

def getEcodeFromDiagnosis(diagnosis):
    try:
        # add padding to diagnosis
        diagnosis = addPadding(diagnosis, 20)

        # convert padded diagnosis to numpy array so model understands
        X = convertDiagnosisToX(diagnosis)

        # load the model from disk
        modelname = os.path.join(package_directory, '..', '..', 'model_training', 'model_diagnosis_ecode.h5')
        model = keras.models.load_model(modelname)

        # make a prediction
        prediction = model.predict(X)

        # get prediction where model is most certain
        ecode_int = prediction[0].argmax(axis=0)

        # convert ecode to ICD
        ecode_icd = convertIntToICD(ecode_int)

        if (ecode_icd == 0):
            return "None"

        return ecode_icd

    except Exception as e:
        logging.error(e)
        return "None"

def getNextProcedure(procedure):
    import numpy as np

    try:
        # get the last diagnosis
        procedure = list(procedure)
        procedure = procedure[0]
        if(len(procedure) > 1):
            procedure = procedure[-1]

        # convert procedure to something the model understands
        X = convertICDtoInt(procedure)
        X = np.asarray(X)
        X = X.reshape(1)

        # load the model from disk
        modelname = os.path.join(package_directory, '..', '..', 'model_training', 'model_procedure_next.h5')
        model = keras.models.load_model(modelname)

        # make a prediction
        prediction = model.predict(X)

        # get prediction where model is most certain
        procedure_int = prediction[0].argmax(axis=0)

        # convert ecode to ICD
        procedure_icd = convertIntToICD(procedure_int)

        # if no procedure was found
        if(procedure_icd == 0):
            return "None"

        return procedure_icd

    except Exception as e:
        logging.error(e)
        return "None"

# Test
#print(getDurationFromDiagnosis(["L600", "J45909"]))
#print(getEcodeFromDiagnosis(["L600", "J45909"]))
#print(getNextProcedure(["L600", "J45909"]))