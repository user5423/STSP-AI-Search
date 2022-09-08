import sys
import copy
import random
import pprint
import pytest
sys.path.insert(0, "./src")
sys.path.insert(0, "../src")
from supportingDS import TSPInstance
from AntSystem import AntSystem, Ant			

##BUG: ZeroByDivision Is possible !!! Review cases in AlgAbasic.py and fix accordingly

class Test_AntSystem_AdvanceAntCycle:
	def test_advancePheremoneCycle(self):
		AS = AntSystem()

		numberOfCities = 4
		## NOTE: This provides an Assymetric TSP distance matrix
		distanceMatrix = [[None for _ in range(numberOfCities)] for _ in range(numberOfCities)]
		for i in range(numberOfCities):
			for j in range(i, numberOfCities):
				distance = random.randint(1, 100)
				distanceMatrix[i][j] = distance
				distanceMatrix[j][i] = distance

		AS._initializeDataStructures(distanceMatrix, numberOfCities)
		oldPheremoneMatrix = copy.deepcopy(AS.pheremoneMatrix)

		citySelection = [i for i in range(numberOfCities)]
		for ant in AS.ants:
			cityTour = copy.deepcopy(citySelection)
			random.shuffle(cityTour)
			ant.tour.update(dict.fromkeys(cityTour, None))
			ant.tourDistance = random.randint(1,100)

		AS._advancePheremoneCycle()

		assert AS.pheremoneMatrix != oldPheremoneMatrix
		pprint.pprint(AS.pheremoneMatrix)
		for row in range(numberOfCities):
			for column in range(numberOfCities):
				assert AS.pheremoneMatrix[row][column] == AS.pheremoneMatrix[column][row]

		pprint.pprint(AS.pheremoneMatrix)
		return None

	def test_resetAntCycle(self):
		AS = AntSystem()

		numberOfCities = 20
		## NOTE: This provides an Assymetric TSP distance matrix
		distanceMatrix = [[random.randint(0, 100) for _ in range(numberOfCities)] for _ in range(numberOfCities)]

		AS._initializeDataStructures(distanceMatrix, numberOfCities)

		citySelection = [i for i in range(numberOfCities)]
		for ant in AS.ants:
			cityTour = copy.deepcopy(citySelection)
			random.shuffle(cityTour)
			ant.tour = dict.fromkeys(cityTour, None)
			ant.tourDistance = random.randint(0,100)

		AS._resetAntCycle()

		for ant in AS.ants:
			assert ant.tour == {ant.startCity: None}
			assert ant.tourDistance == 0

		return None