"""

This file contains the stuff we need to do at run time and some quick notes on how to use

"""


from Routing import *
from TrashBot import *
import csv


#each dumpster is 1.6 y^3, with compression ratio 2.5 => .52
#each truck is 30 cubic yards
#heights are given out of 5
#so, sum(height) * .52 / 5 = 30
#capacity on each truck is 288, round to 290
TRUCK_CAPACITY = 290



def loadData():
	#initialize City
	evanston = City()

	lat_lons = []

	def manhattanDist(pt1, pt2):
		return abs(pt1[0] - pt2[0]) + abs(pt1[1] - pt2[1])


	with open('aggregate.csv', 'rb') as csvfile:
		rdr = csv.reader(csvfile, delimiter = ',')
		hdrFlg = 1
		depotFlg = 1
		for r in rdr:
			if hdrFlg == 1:
				hdrFlg = 0
			else:
				#add lat, lon
				lat_lons.append((float(r[1]), float(r[2])))
				if depotFlg == 1:
					depotFlg = 0
				else:
					#print r[0], r[3]
					evanston.addSensor(TrashBot(r[0], float(r[3]), float(r[4])))

	#calculate distance matrix
	d = np.zeros((len(lat_lons), len(lat_lons)))
	for i in range(len(lat_lons)):
		for j in range(len(lat_lons)):
			if i == j:
				d[i,j] = 99
			else:
				d[i,j] = manhattanDist(lat_lons[i], lat_lons[j])

	#set distance matrix
	evanston.setDistMat(d)

	#return the container class that we run the simulations/generate the data from
	return evanston, lat_lons


def savingsMethod(evanston):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = SavingsMethod(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY)
	soln = c.parallelSolver()
	return soln #this is a list of routes, each route is alist of node ids in the order they are traversed

def arbitraryMethod(evanston):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 50)
	soln = c.solve('arbitrary')
	return soln #this is a list of routes, each route is alist of node ids in the order they are traversed

def arbitrary2Method(evanston):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 50)
	soln = c.solve('arbitrary_2')
	return soln #this is a list of routes, each route is alist of node ids in the order they are traversed

def nearestMethod(evanston):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 5)
	soln = c.solve('nearest')
	return soln #this is a list of routes, each route is alist of node ids in the order they are traversed

def nearest2Method(evanston):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 2)
	soln = c.solve('nearest_2')
	return soln #this is a list of routes, each route is alist of node ids in the order they are traversed


def get_routes():
	"""Function to be called by app"""
	city, coords = loadData()
	return nearestMethod(city)

def main():
	#this function happens when we execute the simulation at runtime
	city, coords = loadData()
	routes = nearestMethod(city) #this gives us the routes
	#we can then use the routes and the lat/lon coordinates to draw the routes, probably


if __name__ == '__main__':
	main()
