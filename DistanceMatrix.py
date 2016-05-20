import requests
import json
import sys
import numpy as np

def FormatParameters(parameters):
    NewParameters = ""
    for param in parameters:
        NewParameters += param.replace(", ", "+")
        NewParameters += "|"
    return NewParameters[:-1]

def BuildRequest(origins, destinations, key):
    origins = "origins=" + FormatParameters(origins) + "&"
    destinations = "destinations=" + FormatParameters(destinations) + "&"
    APIkey = "key=" + key
    return "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&" + origins + destinations + APIkey

def ParseResponse(response):
    response = json.loads(response.text)['rows']
    numOrigins = len(response)
    numDestinations = len(response[0]['elements'])

    #columns = destinations = elements
    #rows = origins = rows
    distanceMatrix = np.zeros((numOrigins, numDestinations), dtype='f')
    durationMatrix = np.zeros((numOrigins, numDestinations), dtype="int")

    for o in range(0, numOrigins):
        for d in range(0, numDestinations):

            #duration in seconds
            duration = response[o]['elements'][d]['duration']['value']
            #distance in meters
            distance = response[o]['elements'][d]['distance']['value']

            durationMatrix[o, d] = duration
            distanceMatrix[o, d] = distance
    print "duration matrix: "
    print durationMatrix
    print
    print "distance matrix: "
    print distanceMatrix

def GetMatrix(origins, destinations, key):
    HTTPRequest = BuildRequest(origins, destinations, key)
    response = requests.get(HTTPRequest)
    return ParseResponse(response)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        origins = ["Vancouver, BC, Canada", "Seattle, WA, USA", "Victoria, BC, Canada"]
        destinations = ["San Francisco, CA, USA", "Victoria, BC, Canada"]
    #else:
    #    origins = sys.argv[0]
    #    destinations = sys.argv[1]

    APIKey = ""
    GetMatrix(origins, destinations, APIKey)
