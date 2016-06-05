### Savings Method

import numpy as np
import copy
import Gap

def tourDist(distMat, tour):
	d = 0
	if tour[0] != 0 or tour[len(tour)-1] != 0:
		raise Exception('Invalid Tour')
	else:
		for i in range(1, len(tour)):
			d += distMat[tour[i-1],tour[i]]
	return d

class SavingsMethod:
	"""
	This class implements the Clark and Wright SAVINGS ALGORITHM (1964). 

	It provides heuristic solutions to the VRP, works well when the number of vechiles is not known ahead of time, and can handle both directed and undirected graphs.

	Args:
		distMat: a 2d numpy array representing the graph's distance matrix (note, node 0 should be the depot)
		inventory: a list-like structure, holding the current inventory of the i-th node
		truckCapacity: a float designating the maximum capacity of each truck

	Attributes:
		distMat: a 2d numpy array representing the graph's distance matrix
		inventory: a list-like structure, holding the current inventory of the i-th node
		truckCapacity: a float designating the maximum capacity of each truck
		currentRoutes: the current routes, list of lists
		savings: a list of tuples containing the savings for node pairs (i,j)
	"""

	#Constants
	DEBUG = False

	def __init__(self, distMat, inventory, truckCapacity):
		self.distMat = distMat
		self.inventory = inventory
		self.truckCapacity = truckCapacity
		
		#Calculate Savings
		savingsMat = np.zeros(distMat.shape)
		for i in range(len(inventory)):
			for j in range(len(inventory)):
				if i != j:
					savingsMat[i,j] = self.distMat[i,0] + self.distMat[0,j] - self.distMat[i,j]
		savingsList = [(x, y, savingsMat[x,y]) for x in range(1, len(inventory)) for y in range(1, len(inventory)) if x != y]
		self.savings = sorted(savingsList, key=lambda x: x[2], reverse=True)
		
		self.currentRoutes = [[0, i, 0] for i in range(len(inventory)) if i != 0]

	def tourCap(self, tour):
		return sum([self.inventory[i] for i in tour])


	def parallelSolver(self):
		"""
		Solve the VRP with the Savings Method using the parallel Strategy

		Args:
			None

		Return:
			Routes: List of lists, each inner list is a node id tour
		"""

		#TODO: Make this travesty more efficient and less ugly
		for s in self.savings:
			#find a route starting with (0,j)
			try:

				a = [i for i in self.currentRoutes if i[0] == 0 and i[1] == s[0]][0]
				#find a route ending with (i, 0)
				b = [i for i in self.currentRoutes if i[len(i)-1] == 0 and i[len(i)-2] == s[1] and i != a][0]
				#Check Capacity constraint
				if self.tourCap(a) + self.tourCap(b) <= self.truckCapacity:
					self.currentRoutes.remove(a)
					if b in self.currentRoutes: self.currentRoutes.remove(b)
					newRoute = b[:len(b)-1] + a[1:] #remove zeros and concatenate
					self.currentRoutes.append(newRoute)
			except IndexError:
				if self.DEBUG:
					print 'Cannot merge for ', s, ', skipping...'

		return self.currentRoutes

class VRPSolver:

	def __init__(self, distMat, inventory, truckCapacity):
		self.distMat = distMat
		self.inventory = inventory
		self.truckCapacity = truckCapacity
	def savingsMethod(self):
		a = SavingsMethod(self.distMat, self.inventory,self.truckCapacity)
		return a.parallelSolver()
	def improve(self, routes):
		newRoutes = []
		a = TSPSolver(self.distMat, [0])
		for r in routes:
			newRoutes.append(a.twoOpt(r))
		return newRoutes
	def solve(self):
		initial = self.savingsMethod()
		return self.improve(initial)

		
class TSPSolver:

	def __init__(self, distMat, nodeList):
		self.distMat = distMat
		if 0 not in nodeList:
			raise Exception('Input Error: Depot not present')
		self.nodeList = nodeList
		self.tour = []

	def arbitraryInsertionSolver(self, reps, opt=False):
		
		def arbitraryInstance():
			#pick random starting node other than 0
			nl = copy.deepcopy(self.nodeList)
			nl.remove(0)
			
			#build tour
			t = []
			t.append(0)

			#print [i for i in nl if self.distMat[nl[len(nl)-1],i] != 0], nl
			start = np.random.choice([i for i in nl if self.distMat[t[len(t)-1],i] != 0])

			nl.remove(start)
			t.append(start)

			#choose next to insert at random
			while len(nl) > 0:
				try:
					next = np.random.choice([i for i in nl if self.distMat[t[len(t)-1],i] != 0])
				except ValueError:
					#Bad Solution, skip
					return [], 0
				nl.remove(next)
				t.append(next)

			#tour completed, append depot, get distance
			t.append(0)

			if opt:
				t = self.twoOpt(t)

			dist = tourDist(self.distMat, t)
			return t, dist

		bestTour, bestDist = arbitraryInstance()
		for i in range(reps - 1):
			t, d = arbitraryInstance()
			if d < bestDist and t != []:
				bestTour = t
				bestDist = d

		self.tour = bestTour
		if bestTour == []:
			print 'ArbitraryInsertionError: No Solution Found'
		return bestTour

	def nearestInsertionSolver(self, randInit=False, reps=1):
		
		bestTour = []
		bestDist = -1

		for r in range(reps):

			nl = copy.deepcopy(self.nodeList)
			nl.remove(0)
			t = []
			t.append(0)

			if randInit:
				start = np.random.choice([i for i in nl if self.distMat[t[len(t)-1],i] != 0])
				nl.remove(start)
				t.append(start)

			while len(nl) > 0:
				#this feels hella inefficient, but then again, list comps are fast... time later
				
				
				next = sorted([(i, self.distMat[t[len(t)-1],i]) for i in nl if self.distMat[t[len(t)-1],i] != 0], key=lambda x: x[1])
				
				if next == []:
					print 'NearestInsertionError: No Solution Found'
					continue
				else:
					nl.remove(next[0][0])
					t.append(next[0][0])

			t.append(0)
			
			d = tourDist(self.distMat, t)

			if bestDist == -1 or d < bestDist:
				bestTour = t
				bestDist = d

		self.tour = bestTour
		if bestTour == []:
			print 'NearestInsertionError: No Solution Found'
		return bestTour



	def twoOpt(self, route):
		"""
		Removes 2 edges and reconnects to complete tour, if shorter

		Args:
			None

		Return:
			tour (list): a list of node ids, possibly improved
		"""
		def twoSwap(route, i, k):
			if i==0 or k==(len(route)-1):
				return route
			elif k <= i:
				return route
			else:
				start = route[:i]
				mid = route[i:k][::-1]
				end = route[k:]
				return start + mid + end
		
		bestTour = route
		bestDist = tourDist(self.distMat, route)
		for i in range(1, len(self.tour)-4):
			for k in range(i + 2, len(self.tour)-2):
				tmpTour = twoSwap(bestTour, i, k)
				tmpDist = tourDist(self.distMat, tmpTour)
				if tmpDist < bestDist:
					bestTour = tmpTour
					bestDist = tmpDist

		return bestTour


class FisherJaikumar:


	def __init__(self, distMat, loads, numRoutes, capacity, reps = 10):
		self.dm = distMat
		self.inv = loads
		self.num_routes = numRoutes
		self.cap = capacity
		self.replications = reps

	def stageOne(self, seeds):
		gapInst = Gap.GeneralizedAssignment(self.dm, self.inv, [self.cap for i in range(len(self.inv))],seeds)
		return gapInst.solve()


	def stageTwo(self, assignments, tsp_solver = 'nearest_2'):

		print len(assignments)

		#move nodes to sub-routes
		sub_routes = {}
		for i in range(self.num_routes):
			sub_routes[str(i)] = []
		for i in range(len(assignments)):
			sub_routes[str(assignments[i])].append(i+1)

		sub_tours = {}
		sub_distances = []

		if tsp_solver == 'nearest_2':
			for i in range(self.num_routes):
				sub_routes[str(i)].append(0) #add depot
				
				tsp = TSPSolver(self.dm, sub_routes[str(i)])
				t = tsp.nearestInsertionSolver(randInit=True, reps = self.replications)
				sub_tours[str(i)] = tsp.twoOpt(t)
				if sub_tours[str(i)] != []:
					sub_distances.append(tourDist(self.dm, sub_tours[str(i)]))
				else:
					print 'Invalid Tour'
					return 'TSP Failed', 'TSP Failed'
		elif tsp_solver == 'nearest':
			for i in range(self.num_routes):
				sub_routes[str(i)].append(0) #add depot
				tsp = TSPSolver(self.dm, sub_routes[str(i)])
				t = tsp.nearestInsertionSolver(randInit=True, reps = self.replications)
				sub_tours[str(i)] = t
				if sub_tours[str(i)] != []:
					sub_distances.append(tourDist(self.dm, sub_tours[str(i)]))
				else:
					print 'Invalid Tour'
					return 'TSP Failed', 'TSP Failed'

		elif tsp_solver == 'arbitrary_2':
			for i in range(self.num_routes):
				sub_routes[str(i)].append(0) #add depot
				tsp = TSPSolver(self.dm, sub_routes[str(i)])
				sub_tours[str(i)] = tsp.arbitraryInsertionSolver(self.replications, opt=True)
				if sub_tours[str(i)] != []:
					sub_distances.append(tourDist(self.dm, sub_tours[str(i)]))
				else:
					print 'Invalid Tour'
					return 'TSP Failed', 'TSP Failed'

		else: #arbitrary w/o 2-opt improvement
			for i in range(self.num_routes):
				sub_routes[str(i)].append(0) #add depot
				tsp = TSPSolver(self.dm, sub_routes[str(i)])
				sub_tours[str(i)] = tsp.arbitraryInsertionSolver(self.replications, opt=False)
				if sub_tours[str(i)] != []:
					sub_distances.append(tourDist(self.dm, sub_tours[str(i)]))
				else:
					print 'Invalid Tour'
					return 'TSP Failed', 'TSP Failed'

		return sub_tours, sub_distances

	def solve(self, solver='nearest_2'):
		bestDist = 10000000000
		bestTours = {}
		for i in range(self.replications):
			#first, get random seeds
			idList = range(1,len(self.inv)+1)
			np.random.shuffle(idList)
			assignments = self.stageOne(idList[:self.num_routes])
			while assignments == 'INFEASIBLE':
				print 'too few routes, incrementing'
				self.num_routes += 1
				idList = range(1,len(self.inv)+1)
				np.random.shuffle(idList)
				assignments = self.stageOne(idList[:self.num_routes])
			t, d = self.stageTwo(assignments, solver)
			tries = 0
			while t == 'TSP Failed' and tries < 100:
				t, d = self.stageTwo(assignments, solver)
				tries += 1
			if d != 'TSP Failed' and sum(d) < bestDist:
				bestDist = sum(d)
				bestTours = t
		return bestTours, bestDist


class TourPartitioning:
	def __init__(self, distMat, loads, capacity, reps = 10):
		self.dm = distMat
		self.inv = loads
		
		self.cap = capacity
		self.replications = reps
	def solve(self, method = 'nearest_2'):
		#first solve TSP
		a = TSPSolver(self.dm, range(len(self.inv)))
		
		if method == 'arbitrary':
			improvedSoln = a.arbitraryInsertionSolver(self.replications, opt=False)
		elif method == 'nearest':
			improvedSoln = a.nearestInsertionSolver(randInit=True, reps=1)
		elif method == 'arbitrary_2':
			improvedSoln = a.arbitraryInsertionSolver(self.replications, opt=True)
		else: #nearest_2
			prelimSoln = a.nearestInsertionSolver(randInit=True, reps=1)
			improvedSoln = a.twoOpt(prelimSoln)

		#remove zeros for partitioning
		improvedSoln.remove(0)
		improvedSoln.remove(0)

		#now do partitioning
		finalRoutes = []
		currCap = 0
		currRoute = []
		for i in range(len(improvedSoln)):
			if (currCap + self.inv[improvedSoln[i]] < self.cap):
				currCap += self.inv[improvedSoln[i]]
				currRoute.append(improvedSoln[i])
			else:
				#route complete
				finalRoutes.append([0] + currRoute + [0])
				currRoute = []
				currCap = 0
		return finalRoutes






if __name__ == "__main__":

	# br17 = [[9999,3,5,48,48,8,8,5,5,3,3,1,3,5,8,8,5],
	# 		[3,9999,3,48,48,8,8,5,5,1,1,3,1,3,8,8,5],
	# 		[5,3,9999,72,72,48,48,24,24,3,3,5,3,1,48,48,24],
	# 		[48,48,74,9999,1,6,6,12,12,48,48,48,48,74,6,6,12],
	# 		[48,48,74,1,9999,6,6,12,12,48,48,48,48,74,6,6,12],
	# 		[8,8,50,6,6,9999,1,8,8,8,8,8,8,50,1,1,8],
	# 		[8,8,50,6,6,1,9999,8,8,8,8,8,8,50,1,1,8],
	# 		[5,5,26,12,12,8,8,9999,1,5,5,5,5,26,8,8,1],
	# 		[5,5,26,12,12,8,8,1,9999,5,5,5,5,26,8,8,1],
	# 		[3,1,3,48,48,8,8,5,5,9999,1,3,1,3,8,8,5],
	# 		[3,1,3,48,48,8,8,5,5,1,9999,3,1,3,8,8,5],
	# 		[1,3,5,48,48,8,8,5,5,3,3,9999,3,5,8,8,5],
	# 		[3,1,3,48,48,8,8,5,5,1,1,3,9999,3,8,8,5],
	# 		[5,3,1,72,72,48,48,24,24,3,3,5,3,9999,48,48,24],
	# 		[8,8,50,6,6,1,1,8,8,8,8,8,8,50,9999,1,8],
	# 		[8,8,50,6,6,1,1,8,8,8,8,8,8,50,1,9999,8],
	# 		[5,5,26,12,12,8,8,1,1,5,5,5,5,26,8,8,9999]]


	# #dm = np.array([[0,2,3], [1,0,1], [2,3,0]])
	# dm = np.array(br17)
	# #print dm
	# inv = [2, 3, 4, 1, 1, 6, 3, 4, 2, 8, 2, 2, 1, 6, 1, 2, 1]
	# cap = 45
	# a = SavingsMethod(dm, inv, cap)
	# print a.parallelSolver()

	# b = TSPSolver(dm, range(17))
	# arbSoln = b.arbitraryInsertionSolver(10)
	# if arbSoln != []:
	# 	arbSolnImp = b.twoOpt(arbSoln)
	# 	arbSolnImp2 = b.twoOpt(arbSolnImp)
	# print 'Arbitrary Insertion:'
	# print arbSoln, tourDist(dm, arbSoln) if arbSoln != [] else 'None'
	# print arbSolnImp, tourDist(dm, arbSolnImp) if arbSolnImp != [] else 'None'
	# print arbSolnImp2, tourDist(dm, arbSolnImp2) if arbSolnImp2 != [] else 'None'
	
	# b = TSPSolver(dm, range(17))
	# arbSoln = b.arbitraryInsertionSolver(10, opt=True)
	# if arbSoln != []:
	# 	arbSolnImp = b.twoOpt(arbSoln)
	# 	arbSolnImp2 = b.twoOpt(arbSolnImp)

	# print 'Arbitrary Insertion w/ 2-Opt:'
	# print arbSoln, tourDist(dm, arbSoln) if arbSoln != [] else 'None'
	# print arbSolnImp, tourDist(dm, arbSolnImp) if arbSolnImp != [] else 'None'
	# print arbSolnImp2, tourDist(dm, arbSolnImp2) if arbSolnImp2 != [] else 'None'
	


	# b = TSPSolver(dm, range(17))
	# neaSoln = b.nearestInsertionSolver(randInit = False, reps = 20)
	# neaSolnImp = b.twoOpt(neaSoln)
	# neaSolnImp2 = b.twoOpt(neaSolnImp)
	# print 'Nearest Insertion'
	# print neaSoln, tourDist(dm, neaSoln) if neaSoln != [] else 'None'
	# print neaSolnImp, tourDist(dm, neaSolnImp) if neaSolnImp != [] else 'None'
	# print neaSolnImp2, tourDist(dm, neaSolnImp2) if neaSolnImp2 != [] else 'None'

	size = 1000

	dm = np.random.rand(size,size)
	for i in range(dm.shape[0]):
		dm[i,i] = 9999

	inv = np.random.rand(size)


	c = FisherJaikumar(dm, inv[1:], 10, 75)
	fjRoutes, fjDist = c.solve('nearest_2')
	print fjRoutes
	print fjDist

