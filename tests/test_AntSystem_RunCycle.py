import sys
import copy
import pytest
import random

sys.path.insert(0, "./src")
sys.path.insert(0, "../src")
from supportingDS import TSPInstance
from AntSystem import AntSystem, Ant


class Test_AntSystem_RunCycle:
	def test_AntCycleTourAttributes(self):
		AS = AntSystem()
		arg = {
			"maxIterations": 10,
			"numberOfAnts": 15,
		}

		numberOfCities = 20
		## NOTE: This provides an Assymetric TSP distance matrix
		distanceMatrix = [[random.randint(0, 100) for _ in range(numberOfCities)] for _ in range(numberOfCities)]
		
		AS._setHyperparameters(arg)
		AS._initializeDataStructures(distanceMatrix, numberOfCities)

		for ant in AS.ants:
			AS._runAntCycle(ant)
			assert len(ant.tour) == AS.TSPInstance.numberOfCities - 1
			startCity = next(iter(ant.tour))
			assert startCity == ant.startCity

	## TODO: We still need to test whether the probabilitisicSelection is correct

	## BUG: We need to ensure that the ZeroDivision doens't occur

