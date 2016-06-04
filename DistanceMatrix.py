import sys
import numpy as np
import os
import csv
import re

def ClusterData(building_data, minlat, maxlat, minlon, maxlon):
    num_clusters = 22
    lat_range = np.linspace(minlat, maxlat, num_clusters + 1)
    lon_range = np.linspace(minlon, maxlon, num_clusters + 1)
    aggregate_building_data = [{'id': 0, 'lat': 42.056732, 'lon': -87.687349, 'height': 0}];
    node_id = 1

    for ii in range(0,num_clusters):
        for jj in range(0,num_clusters):
            clusterdata = [x for x in building_data if lat_range[ii] <= x['lat'] <= lat_range[ii+1] \
            and lon_range[jj] <= x['lon'] <= lon_range[jj+1]]

            if clusterdata:
                avg_lat = np.mean(map(lambda x: x['lat'], clusterdata))
                avg_lon = np.mean(map(lambda x: x['lon'], clusterdata))
                total_height = sum(map(lambda x: x['stories'], clusterdata))

                aggregate_building_data.append({'id': node_id, 'lat': avg_lat, 'lon': avg_lon, 'height': total_height})
                node_id += 1

    with open('aggregate.csv', 'wb') as file:
       writer = csv.DictWriter(file, fieldnames = ['id', 'lat', 'lon', 'height'])
       writer.writeheader()
       for row in aggregate_building_data:
           writer.writerow(row)

def GetData():
    minlat = 42.048164
    maxlat = 42.062057
    minlon = -87.710688
    maxlon = -87.678947
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
                if lat < maxlat and lat > minlat and lon < maxlon and lon > minlon:
                    building_data.append({'lat': lat, 'lon': lon, 'stories': num_stories})

    ClusterData(building_data, minlat, maxlat, minlon, maxlon)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        # origins = ["Vancouver, BC, Canada", "Seattle, WA, USA", "Victoria, BC, Canada"]
        # destinations = ["San Francisco, CA, USA", "Victoria, BC, Canada"]

        GetData()

    #else:
    #    origins = sys.argv[0]
    #    destinations = sys.argv[1]

    # APIKey = os.environ['GMAP_KEY']
    # GetMatrix(origins, destinations, 'AIzaSyDfNjjRUcKkycQ0vcQ1Vh0vJCCLppimCYQ')
