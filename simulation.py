
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
#print len(evanston.simulateWorstWeek())

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

#Run savings method experiment:
# resultsDist = []
# resultsNumRoutes = []
# for jj in range(50):
# 	evanston.reset()
# 	heights = evanston.simulate1Week()
# 	c = SavingsMethod(evanston.getDistMat(), np.append([0], heights), 290)
# 	soln = c.parallelSolver()
# 	resultsNumRoutes.append(len(soln))
# 	resultsDist.append(sum([tourDist(evanston.getDistMat(), i) for i in soln]))
# 	print jj, 'th replication completed'


# print resultsDist
# print resultsNumRoutes

#########
heights = evanston.simulate1Week()
#a = TSPSolver(evanston.getDistMat(), range(len(heights)))
#prelimRes =  a.nearestInsertionSolver(randInit=True, reps=1)
#print tourDist(evanston.getDistMat(), prelimRes)
#improvedRes = a.twoOpt(prelimRes)
#print tourDist(evanston.getDistMat(), improvedRes)

a = TourPartitioning(evanston.getDistMat(), heights, TRUCK_CAPACITY, reps = 1)
s = a.solve()
print s
print sum([tourDist(evanston.getDistMat(), i) for i in s])


