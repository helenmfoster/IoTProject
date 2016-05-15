### Params for trashbot

"""
1. Number of floors (proxy for num. people): Int

"""

#Imports
import numpy as np
import time

#Constants
CENTER = (1.13 / 3) / 4 #1.13 mean, divided by 3 floors, over 4 samples/day
FLR_MULT = 1


class TrashBot:
    def __init__(self, sensor_id, num_floors):
		self.id = sensor_id
		self.scale_factor = num_floors

		self.mean = max(0.01, np.random.normal(CENTER * FLR_MULT * self.scale_factor, 0.01)) #currently arbitrary stdev
		print self.mean

		self.current_fill = 0

    #def __str__(self):
	#	return str(self.trash_average) 

    def grow(self):
        self.current_fill += np.random.exponential(self.mean)

    def emitStatus(self):
        self.grow()
        print "id: "+ str(self.id) + ", ht: " + str(self.current_fill)

class City:
	def __init__(self):
		self.sensors = []

	def addSensor(self, bot):
		self.sensors.append(bot)

	def getStatuses(self):
		order = np.arange(len(self.sensors))
		np.random.shuffle(order) #emit in random order
		
		#Should we introduce noise? (sensors that don't emit/die)

		for i in order:
			self.sensors[i].emitStatus()

	def simulate(self):
		while True:
			self.getStatuses()
			time.sleep(0.25) #.25 seconds/reading -> 1 second /day




network = City() #make new coll. of sensors
for i in range(30): #add 30 dummy sensors
	#for now, random building height params, change after meeting CoE guy
	network.addSensor(TrashBot(i, np.random.randint(1, high=5, size=1)))


#Test simulation
network.simulate()

