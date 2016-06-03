from __future__ import print_function
from ortools.linear_solver import pywraplp
import numpy as np
class GeneralizedAssignment:


	def __init__(self, costMat, loadArr, capArr, seeds):
		self.seeds = seeds
		self.num_routes = len(seeds)
		
		self.loads = loadArr
		self.capacities = capArr

		#calculate costs and then remove 0 from distance matrix
		self.cost_mat = np.zeros((costMat.shape[0]-1, self.num_routes))
		for i in range(1, costMat.shape[0]):
			for j in range(self.num_routes):
				if i == seeds[j]:
					self.cost_mat[i-1,j] = 0
				else:
					self.cost_mat[i-1,j] = min(costMat[0,i] + costMat[i,seeds[j]] + costMat[seeds[j],0],
					costMat[0,seeds[j]] + costMat[seeds[j],i] + costMat[i,0]) -costMat[0,seeds[j]] + costMat[seeds[j],0] 

		#print(self.cost_mat)

		#Initialize solver (using Google's OR tools to solve MILP)
		self.solver = pywraplp.Solver('SolveIntegerProblem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

		#Initialize sets
		self.N = range(len(self.loads))
		self.K = range(self.num_routes)


		# For the output: the assignment as task number.
		self.assigned = [self.solver.IntVar(0, 10000, 'assigned[%i]' % j) for j in self.N]
		#self.costs = [self.solver.IntVar(0, 10000, 'costs[%i]' % i) for i in self.N]
		

		#Initialize decision variables
		self.x = {}
		for i in range(len(self.N)):
			for j in range(len(self.K)):
				self.x[i, j] = self.solver.IntVar(0, 1, 'x[%i,%i]' % (i, j))

		
		# total cost, to be minimized
		self.z = self.solver.Sum([self.cost_mat[i,j] * self.x[i, j] 
			for i in self.N for j in self.K])

  		#
		# constraints
		#
		# each node is on 1 route
		for i in self.N:
			self.solver.Add(self.solver.Sum([self.x[i, j] for j in self.K]) == 1)

		# each route must remain below capacity
		for j in self.K:
			self.solver.Add(self.solver.Sum([self.loads[i] * self.x[i, j] for i in self.N]) <= self.capacities[j])

		# to which task and what cost is person i assigned (for output in MiniZinc)
		for i in self.N:
			self.solver.Add(self.assigned[i] == self.solver.Sum([j * self.x[i, j] for j in self.K]))
			#self.solver.Add(self.costs[i] == self.solver.Sum([self.cost_mat[i,j] * self.x[i, j] for j in self.K]))

	def solve(self):	
		# objective
		objective = self.solver.Minimize(self.z)

		#
		# solution and search
		#
		result_status = self.solver.Solve()

		if result_status != self.solver.OPTIMAL:
			return 'INFEASIBLE'
		
		#print()
		#print('z: ', int(self.solver.Objective().Value()))

		print('Assigned')
		for j in self.N:
			print(int(self.assigned[j].SolutionValue()), end=' ')
		print()

		return [int(i.SolutionValue()) for i in self.assigned]

		#print('Matrix:')
		#for i in self.N:
		#	for j in self.K:
		#  		print(int(self.x[i, j].SolutionValue()), end=' ')
		#	print()
		#print()

		#print()
		#print('walltime  :', self.solver.WallTime(), 'ms')


if __name__ == '__main__':
	#test using given example from google
	c = [[9999,3,5,48,48,8,8,5,5,3,3,0,3,5,8,8,5],
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


	
	c = np.array(c)
	
	inv = [3, 4, 1, 1, 6, 3, 4, 2, 8, 2, 2, 1, 6, 1, 2, 1]
	#print(c)
	seeds = [4, 10]
	caps = [3, 25]
	a = GeneralizedAssignment(c, inv, caps, seeds)
	assignments = a.solve()
	print(assignments)
