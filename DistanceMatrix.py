import requests
import json
import sys

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
    print response.text

def GetMatrix(origins, destinations, key):
    HTTPRequest = BuildRequest(origins, destinations, key)

    response = requests.get(HTTPRequest)
    return ParseResponse(response)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        origins = ["Vancouver, BC, Canada", "Seattle, WA, USA"]
        destinations = ["San Francisco, CA, USA", "Victoria, BC, Canada"]
    else:
        origins = sys.argv[0]
        destinations = sys.argv[1]

    APIKey = "AIzaSyDfNjjRUcKkycQ0vcQ1Vh0vJCCLppimCYQ"
    GetMatrix(origins, destinations, APIKey)
