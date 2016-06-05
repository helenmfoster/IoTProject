
from Routing import *
from TrashBot import *
import csv

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


#print d.shape

#set distance matrix
evanston.setDistMat(d)


#print sum(evanston.simulate1Week())
#print sum(evanston.simulateWorstWeek())

#each dumpster is 1.6 y^3, with compression ratio 2.5 => .52
#each truck is 30 cubic yards
#heights are given out of 5
#so, sum(height) * .52 / 5 = 30
#capacity on each truck is 288, round to 290
TRUCK_CAPACITY = 290

#Run FJ solver on baseline
#c = FisherJaikumar(evanston.getDistMat(), evanston.simulateWorstWeek(), 12, TRUCK_CAPACITY)
#fjRoutes, fjDist = c.solve('nearest_2')
#print fjRoutes
#print fjDist

#c = SavingsMethod(evanston.getDistMat(), np.append([0], evanston.simulateWorstWeek()), 290)
#soln = c.parallelSolver()
#print len(soln)
#print sum([tourDist(evanston.getDistMat(), i) for i in soln])

#########

def writeSimResults(filename, num_routes, route_dist, worst_routes, worst_dist):
	with open(filename, 'wb') as file:
		writer = csv.writer(file, delimiter = ',')
		writer.writerow(['num_routes', 'route_dist', 'worst_routes', 'worst_dist'])
		for i in range(len(num_routes)):
			writer.writerow([num_routes[i], route_dist[i], worst_routes[i], worst_dist[i]])

########


########
#Savings Method
########


resultsDist = []
resultsNumRoutes = []
baselineDist = []
baselineRoutes = []
for jj in range(30):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = SavingsMethod(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY)
	soln = c.parallelSolver()
	resultsNumRoutes.append(len(soln))
	resultsDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	evanston.reset()
	heights = evanston.simulateWorstWeek()
	c = SavingsMethod(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY)
	soln = c.parallelSolver()
	baselineRoutes.append(len(soln))
	baselineDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	print jj, 'th SAVINGS replication completed'

writeSimResults('savingsMethod.csv', resultsNumRoutes, resultsDist, baselineRoutes, baselineDist)

########
#Tour Paritioning with Arbitrary Insertion
########


resultsDist = []
resultsNumRoutes = []
baselineDist = []
baselineRoutes = []
for jj in range(30):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 50)
	soln = c.solve('arbitrary')
	resultsNumRoutes.append(len(soln))
	resultsDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	evanston.reset()
	heights = evanston.simulateWorstWeek()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 50)
	soln = c.solve('arbitrary')
	baselineRoutes.append(len(soln))
	baselineDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	print jj, 'th ARBITRARY replication completed'

writeSimResults('arbitraryMethod.csv', resultsNumRoutes, resultsDist, baselineRoutes, baselineDist)


########
#Tour Paritioning with Arbitrary Insertion (2-opt)
########


resultsDist = []
resultsNumRoutes = []
baselineDist = []
baselineRoutes = []
for jj in range(30):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 10)
	soln = c.solve('arbitrary_2')
	resultsNumRoutes.append(len(soln))
	resultsDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	evanston.reset()
	heights = evanston.simulateWorstWeek()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 10)
	soln = c.solve('arbitrary_2')
	baselineRoutes.append(len(soln))
	baselineDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	print jj, 'th ARBITRARY-2 replication completed'

writeSimResults('arbitrary2Method.csv', resultsNumRoutes, resultsDist, baselineRoutes, baselineDist)

########
#Tour Paritioning with Nearest Insertion
########


resultsDist = []
resultsNumRoutes = []
baselineDist = []
baselineRoutes = []
for jj in range(30):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 5)
	soln = c.solve('nearest')
	resultsNumRoutes.append(len(soln))
	resultsDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	evanston.reset()
	heights = evanston.simulateWorstWeek()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 5)
	soln = c.solve('nearest')
	baselineRoutes.append(len(soln))
	baselineDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	print jj, 'th NEAREST replication completed'

writeSimResults('nearestMethod.csv', resultsNumRoutes, resultsDist, baselineRoutes, baselineDist)

########
#Tour Paritioning with Nearest Insertion (2-opt)
########


resultsDist = []
resultsNumRoutes = []
baselineDist = []
baselineRoutes = []
for jj in range(30):
	evanston.reset()
	heights = evanston.simulate1Week()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 2)
	soln = c.solve('nearest_2')
	resultsNumRoutes.append(len(soln))
	resultsDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	evanston.reset()
	heights = evanston.simulateWorstWeek()
	c = TourPartitioning(evanston.getDistMat(), np.append([0], heights), TRUCK_CAPACITY, reps = 2)
	soln = c.solve('nearest_2')
	baselineRoutes.append(len(soln))
	baselineDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))

	print jj, 'th NEAREST-2 replication completed'

writeSimResults('nearest2Method.csv', resultsNumRoutes, resultsDist, baselineRoutes, baselineDist)
