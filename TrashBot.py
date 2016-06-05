### Params for trashbot

"""
1. Number of floors (proxy for num. people): Int

"""

#Imports
import numpy as np
import time



class TrashBot:
	#Constants
	CENTER = (1.45/3) #1.4/5 mean, divided by 3 floors
	CENTER = CENTER / 2.5 #1.16 cubic feet, compression ratio of 2.5
	FLR_MULT = 1
	def __init__(self, sensor_id, num_floors, num_buildings):
		self.id = sensor_id
		self.scale_factor = num_floors
		self.buildings = num_buildings

		self.mean = max(0.2, np.random.normal(self.CENTER * self.FLR_MULT * self.scale_factor, 0.2))
		#print self.mean

		self.current_fill = 0

	def grow(self):
	    self.current_fill += np.random.exponential(self.mean)

	def simWeek(self):
		for i in range(7):
			self.grow()
		return self.current_fill

	def worstWeek(self):
		return 5  * self.buildings / 2.5 #compression ratio

	def reset(self):
		self.current_fill = 0

	def emitStatus(self):
	    self.grow()
	    print "id: "+ str(self.id) + ", ht: " + str(self.current_fill)

	def getId(self):
		return str(self.id)

class City:
	def __init__(self):
		self.sensors = []

	def addSensor(self, bot):
		self.sensors.append(bot)

	def simulate1Week(self):
		week_heights = [] #intialize with depot
		for i in self.sensors:
			week_heights.append(i.simWeek())
		return week_heights

	def simulateWorstWeek(self):
		week_heights = [] #intialize with depot
		for i in self.sensors:
			week_heights.append(i.worstWeek())
		return week_heights

	def reset(self):
		for i in self.sensors:
			i.reset()

	def setDistMat(self, distMat):
		self.dist_mat = distMat

	def getDistMat(self):
		return self.dist_mat


			




#network = City() #make new coll. of sensors
#for i in range(30): #add 30 dummy sensors
	#for now, random building height params, change after meeting CoE guy
#	network.addSensor(TrashBot(i, np.random.randint(1, high=5, size=1)))


#Test simulation
#network.simulate()

