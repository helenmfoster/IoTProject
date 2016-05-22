### Savings Method

import numpy as np


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
			a = [i for i in self.currentRoutes if i[0] == 0 and i[1] == s[0]][0]
			#find a route ending with (j, 0)
			b = [i for i in self.currentRoutes if i[len(i)-1] == 0 and i[len(i)-2] == s[1]][0]
			#Check Capacity constraint
			if self.tourCap(a) + self.tourCap(b) <= self.truckCapacity:
				self.currentRoutes.remove(a)
				self.currentRoutes.remove(b)
				newRoute = b[:len(b)-1] + a[1:] #remove zeros and concatenate
				self.currentRoutes.append(newRoute)

		return self.currentRoutes

		


		

dm = np.array([[0,2,3], [1,0,1], [2,3,0]])
print dm
inv = [0, 12, 7]
cap = 10
a = SavingsMethod(dm, inv, cap)
print a.parallelSolver()