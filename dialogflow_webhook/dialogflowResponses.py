#!/usr/bin/python3.7
# -*- coding: utf8 -*-

# This file contains all possible ways to response to dialogflow
from flask import  make_response, jsonify

def simple_response(fullfilment):
    # return a simple text response
    return make_response(jsonify({'fulfillmentText': fullfilment}))

def simple_final_response(fullfilment):
    # return a simple text response and make the chatbot leave the conversation
    return make_response(jsonify({"fulfillmentText": fullfilment,
                                  "payload": {"google": {"expectUserResponse": False}}}))

def simple_response_with_contexts(fullfilment, contextNames, projectId, sessionId):
    # create empty list to add contexts to
    contexts = []
    # loop over all provided contexts in a contextNames list
    for contextName in contextNames:
        # set pathname
        pathName = "projects/" + projectId + "/agent/sessions/" + sessionId + "/contexts/" + contextName
        # add the paths to the context list
        if "followup" in contextName:
            # a followup should have a lifespan of 2
            contexts.append({"name": pathName, "lifespanCount": 2, "parameters": {}})
        else:
            # a normal context should have a lifespan of 1
            contexts.append({"name": pathName, "lifespanCount": 1, "parameters": {}})
    # return simple text response with contexts
    return make_response(jsonify({"fulfillmentText": fullfilment,
                                  "outputContexts": contexts}))

# the following method only works for the google assistant and web chat bot
def rich_response(fullfilment):
    return make_response(jsonify({"fulfillmentText": fullfilment,
                                  "payload":
                                        {"google":
                                            {"expectUserResponse": True,
                                               "richResponse":
                                                   {"items":
                                                       [{"simpleResponse":
                                                               {"textToSpeech": fullfilment}
                                                            }]
                                                    }
                                            }
                                        }
                                    }
                                )
                        )

# the following method only works for the google assistant and web chat bot
def rich_response_with_suggestions(fullfilment, suggestionsList):
    # create empty list to add suggestions to
    suggestions = []
    # loop over all provided suggestions in a suggestionList
    for suggestion in suggestionsList:
        # create empty dictionary
        suggestionDict = {}
        # set title property with the suggestion as value
        suggestionDict["title"] = suggestion
        # add dictionary to the suggestionlist
        suggestions.append(suggestionDict)

    return make_response(jsonify({"fulfillmentText": fullfilment,
                                  "payload":
                                    {"google":
                                        {"expectUserResponse": True,
                                         "richResponse":
                                            {"items":
                                                [{"simpleResponse":
                                                    {"textToSpeech": fullfilment}
                                                }],
                                                "suggestions": suggestions
                                            }
                                        }
                                    }
                                })
                        )

# the following method only works for the google assistant and web chat bot
def rich_response_with_suggestions_and_contexts(fullfilment, suggestionsList, contextNames, projectId, sessionId):
    # suggestions
    # create empty list to add suggestions to
    suggestions = []
    # loop over all provided suggestions in a suggestionList
    for suggestion in suggestionsList:
        # create empty dictionary
        suggestionDict = {}
        # set title property with the suggestion as value
        suggestionDict["title"] = suggestion
        # add dictionary to the suggestionlist
        suggestions.append(suggestionDict)

    # contexts
    # create empty list to add contexts to
    contexts = []
    # loop over all provided contexts in a contextNames list
    for contextName in contextNames:
        # set pathname
        pathName = "projects/" + projectId + "/agent/sessions/" + sessionId + "/contexts/" + contextName
        # add the paths to the context list
        contexts.append({"name": pathName, "lifespanCount": 1, "parameters": {}})

    return make_response(jsonify({"fulfillmentText": fullfilment,
                                  "outputContexts": contexts,
                                  "payload":
                                    {"google":
                                        {"expectUserResponse": True,
                                         "richResponse":
                                            {"items":
                                                [{"simpleResponse":
                                                    {"textToSpeech": fullfilment}
                                                }],
                                                "suggestions": suggestions
                                            }
                                        }
                                    }
                                })
                        )