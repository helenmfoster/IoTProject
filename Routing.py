### Savings Method

import numpy as np
import copy

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
				next = sorted([(i, self.distMat[t[len(t)-1],i]) for i in nl if self.distMat[t[len(t)-1],i] != 0], key=lambda x: x[1])[0]
				nl.remove(next[0])
				t.append(next[0])

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







if __name__ == "__main__":

	br17 = [[9999,3,5,48,48,8,8,5,5,3,3,0,3,5,8,8,5],
			[3,9999,3,48,48,8,8,5,5,0,0,3,0,3,8,8,5],
			[5,3,9999,72,72,48,48,24,24,3,3,5,3,0,48,48,24],
			[48,48,74,9999,0,6,6,12,12,48,48,48,48,74,6,6,12],
			[48,48,74,0,9999,6,6,12,12,48,48,48,48,74,6,6,12],
			[8,8,50,6,6,9999,0,8,8,8,8,8,8,50,0,0,8],
			[8,8,50,6,6,0,9999,8,8,8,8,8,8,50,0,0,8],
			[5,5,26,12,12,8,8,9999,0,5,5,5,5,26,8,8,0],
			[5,5,26,12,12,8,8,0,9999,5,5,5,5,26,8,8,0],
			[3,0,3,48,48,8,8,5,5,9999,0,3,0,3,8,8,5],
			[3,0,3,48,48,8,8,5,5,0,9999,3,0,3,8,8,5],
			[0,3,5,48,48,8,8,5,5,3,3,9999,3,5,8,8,5],
			[3,0,3,48,48,8,8,5,5,0,0,3,9999,3,8,8,5],
			[5,3,0,72,72,48,48,24,24,3,3,5,3,9999,48,48,24],
			[8,8,50,6,6,0,0,8,8,8,8,8,8,50,9999,0,8],
			[8,8,50,6,6,0,0,8,8,8,8,8,8,50,0,9999,8],
			[5,5,26,12,12,8,8,0,0,5,5,5,5,26,8,8,9999]]		


	#dm = np.array([[0,2,3], [1,0,1], [2,3,0]])
	dm = np.array(br17)
	#print dm
	inv = [2, 3, 4, 1, 1, 6, 3, 4, 2, 8, 2, 2, 1, 6, 1, 2, 1]
	cap = 45
	a = SavingsMethod(dm, inv, cap)
	print a.parallelSolver()

	b = TSPSolver(dm, range(17))
	arbSoln = b.arbitraryInsertionSolver(10)
	if arbSoln != []:
		arbSolnImp = b.twoOpt(arbSoln)
		arbSolnImp2 = b.twoOpt(arbSolnImp)
	print 'Arbitrary Insertion:'
	print arbSoln, tourDist(dm, arbSoln) if arbSoln != [] else 'None'
	print arbSolnImp, tourDist(dm, arbSolnImp) if arbSolnImp != [] else 'None'
	print arbSolnImp2, tourDist(dm, arbSolnImp2) if arbSolnImp2 != [] else 'None'
	
	b = TSPSolver(dm, range(17))
	arbSoln = b.arbitraryInsertionSolver(10, opt=True)
	if arbSoln != []:
		arbSolnImp = b.twoOpt(arbSoln)
		arbSolnImp2 = b.twoOpt(arbSolnImp)

	print 'Arbitrary Insertion w/ 2-Opt:'
	print arbSoln, tourDist(dm, arbSoln) if arbSoln != [] else 'None'
	print arbSolnImp, tourDist(dm, arbSolnImp) if arbSolnImp != [] else 'None'
	print arbSolnImp2, tourDist(dm, arbSolnImp2) if arbSolnImp2 != [] else 'None'
	


	b = TSPSolver(dm, range(17))
	neaSoln = b.nearestInsertionSolver(randInit = False, reps = 20)
	neaSolnImp = b.twoOpt(neaSoln)
	neaSolnImp2 = b.twoOpt(neaSolnImp)
	print 'Nearest Insertion'
	print neaSoln, tourDist(dm, neaSoln) if neaSoln != [] else 'None'
	print neaSolnImp, tourDist(dm, neaSolnImp) if neaSolnImp != [] else 'None'
	print neaSolnImp2, tourDist(dm, neaSolnImp2) if neaSolnImp2 != [] else 'None'


