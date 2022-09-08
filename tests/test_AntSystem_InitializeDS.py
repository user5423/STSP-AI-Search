import sys
import copy
import pytest
import random

sys.path.insert(0, "./src")
sys.path.insert(0, "../src")
from supportingDS import TSPInstance
from AntSystem import AntSystem, Ant

class Test_AntSystem_InitializeDataStructures:
	## The ant system requires the following data structures and attributes

    ## 1. self.TSPInstance -- this is a class that should be tested separately
    ## 2. self.PheremoneMatrix -- List[List]
    ## 3. self.visitedEdges -- Counter[tuple[city, city]]
    ## 4. self.ants -- set()

	def test_visitedEdgesInitialization(self):
		## NOTE: There's no test here since it is a simple creation operation
		...

	def test_TSPInitialization(self):
		## TODO: This should be handled by the TSPInstance classes
		...

	def test_PheremoneMatrixInitialization(self):
		AS = AntSystem()
		arg = {
			"maxIterations": 10,
			"numberOfAnts": 15,
		}

		numberOfCities = 20
		## NOTE: This provides an Assymetric TSP distance matrix
		distanceMatrix = [[random.randint(0, 100) for _ in range(numberOfCities)] for _ in range(numberOfCities)]
		AS._setHyperparameters(arg)
		AS.TSPInstance = TSPInstance(distanceMatrix, numberOfCities)

		pheremoneMatrix = AS._createPheremoneMatrix()

		assert len(pheremoneMatrix) == numberOfCities

		for row in pheremoneMatrix: 
			assert len(row) == numberOfCities
			for trail in row:
				assert isinstance(trail, float)
				assert trail >= 0

		for row in range(numberOfCities):
			for column in range(numberOfCities):
				assert pheremoneMatrix[row][column] == pheremoneMatrix[column][row]


	def test_AntsInitialization(self):
		AS = AntSystem()
		arg = {
			"maxIterations": 10,
			"numberOfAnts": 15
		}

		numberOfCities = 20
		## NOTE: This provides an Assymetric TSP distance matrix
		distanceMatrix = [[random.randint(0, 100) for _ in range(numberOfCities)] for _ in range(numberOfCities)]

		AS._setHyperparameters(arg)
		AS.TSPInstance = TSPInstance(distanceMatrix, numberOfCities)
		ants = AS._createAnts()

		assert isinstance(ants, set) ## check the type of the container
		assert len(ants) == arg["numberOfAnts"] ## check the size of the container
		
		for ant in ants: 
			assert isinstance(ant, Ant) ## check the contents of the container are ants
			assert ant.tourDistance == 0 ## There should be no movement as the ant hasn't moved between cities

			assert isinstance(ant.tour, dict) ## the ant.tour should be a dictionary (ordered)
			assert len(ant.tour) == 1 ## the ant should be initialized with a single start city
			assert next(iter(ant.tour.values())) is None ## the start city should have argument set to None
			assert 0 <= next(iter(ant.tour.keys())) < AS.TSPInstance.numberOfCities ## The startcity should be a valid index integer
			
	def test_SystemInitialization(self):
		...
		