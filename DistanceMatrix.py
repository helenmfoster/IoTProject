import requests
import json
import sys
import numpy as np
import os
import math
import time
import csv
import re

def FormatParameters(parameters):
    formatted_params = ""
    for param in parameters:
        split_string = param.split(',')
        split_string.reverse()
        param = ','.join(split_string)
        formatted_params += param + "|"
    return formatted_params[:-1]

    # pipe = "|"
    # return pipe.join(parameters);

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
    max_request_params = 10;
    num_requests_sqrt = int(math.ceil(len(origins)/float(max_request_params)))
    for d in range(0, num_requests_sqrt):
        current_destination = max_request_params * d
        destinations_subset = destinations[current_destination:(current_destination + max_request_params)]
        for o in range(0, num_requests_sqrt):
            current_origin = max_request_params * o
            origins_subset = origins[current_origin:(current_origin + max_request_params)]

            HTTPRequest = BuildRequest(origins_subset, destinations_subset, key)
            response = requests.get(HTTPRequest)
            time.sleep(1)
            print ParseResponse(response)
            print
    return ParseResponse(response)
    # Concatenate number matrices

def GetData():
    building_data = [];
    with open('Buildings.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            #find text with number of stories
            p = re.compile('STORIES<\/td><td>([\ \/0-9a-zA-Z]*)')
            match = p.search(row[1]).group(1)
            #check if number of stories data exists
            if match:
                if match == 'No Stories':
                    num_stories = 0.0
                elif match == '1/2 Stories':
                    num_stories = 0.5
                elif '/' in match:
                    num_stories = float(match[0:2]) + 0.5
                else:
                    num_stories = float(match[0:2])

                #get latitude and longitude data
                lon = float(row[2].split(',')[0])
                lat = float(row[2].split(',')[1])

                #check if lat and lon are in evanston range
                if lat < 42.062057 and lat > 42.048164 and lon < -87.678947 and lon > -87.710688:
                    building_data.append({'lat': lat, 'lon': lon, 'stories': num_stories})
    print building_data
    print

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        # origins = ["Vancouver, BC, Canada", "Seattle, WA, USA", "Victoria, BC, Canada"]
        # destinations = ["San Francisco, CA, USA", "Victoria, BC, Canada"]

        GetData();

    #else:
    #    origins = sys.argv[0]
    #    destinations = sys.argv[1]

    # APIKey = os.environ['GMAP_KEY']
    # GetMatrix(origins, destinations, 'AIzaSyDfNjjRUcKkycQ0vcQ1Vh0vJCCLppimCYQ')
