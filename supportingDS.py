import random
import time
import threading
from typing import List, Set, Tuple, Any
from functools import partial
## TODO: It is possible that distance is float -- we need to check this
distanceType = int 
cityType = int

matrixType = List[List[distanceType]]
neighboursType = Set[cityType]
tourType = Set[cityType]


class TSPSolver:
	def __init__(self) -> None:
		## These should be overwritten
		self._bestTour = None
		self._bestDistance = 0
		self._outputDict = {}
		self.mainThreadEvent = None
		self.executionThread = None

	def run(self, *args,  timer: float = 59.0, **kwargs) -> Tuple[tourType, distanceType]:
		startTime = time.time()
		self.mainThreadEvent = threading.Event()
		self.executionThread = threading.Thread(target=self._executeSolver, args=args, kwargs=kwargs, daemon=True)

		if timer == -1:
			self.executionThread.start()
			self.executionThread.join()
		elif timer >= 0:
			self.executionThread.start()
			self.mainThreadEvent.wait(timer)
		else:
			raise Exception("You need to specify a valid timer value")

		endTime = time.time()
		print(f"\n\nTime spent executing: {round(endTime - startTime, 2)} seconds\n\n")
		return self._returnResults()

	def _executeSolver(self, *args, **kwargs):
		self._solve(*args, **kwargs)
		self._wakeupMainThread()

	def _wakeupMainThread(self) -> None:
		self.mainThreadEvent.set()
		
	def _solve(self, *args, **kwargs):
		## This should be overrided by the child class
		...

	def _returnResults(self) -> Tuple[tourType, distanceType]:
		## This should be overrided by the child class
		...



class TSPInstance:
	def __init__(self, distanceMatrix: matrixType, numberOfCities: int) -> None:
		self.distanceMatrix = distanceMatrix
		self.numberOfCities = numberOfCities
		self.cities = [i for i in range(numberOfCities)]

	def neighbours(self, startCity: cityType) -> neighboursType:
		## The neighbours of i is the i^th row (represents city i --> k)
		return self.distanceMatrix[startCity]

	def distance(self, startCity: cityType, endCity: cityType) -> distanceType:
		return self.distanceMatrix[startCity][endCity]

	def nearestNeighbour(self) -> Tuple[tourType, distanceType]:
		startCity = random.randint(0, self.numberOfCities-1)
		currentCity = startCity
		visitedCities = {}
		visitedDistance = 0

		## We don't need to search for the last city - hence -1
		for _ in range(self.numberOfCities-1):
			visitedCities[currentCity] = True
			closestCity = None
			closestDistance = float('inf')
			for city, distance in enumerate(self.neighbours(currentCity)):
				if city not in visitedCities and distance < closestDistance:
					closestCity = city
					closestDistance = distance

			if closestCity is None:
				raise Exception(f'The city {currentCity} should have a nearest neighbours')
			
			visitedDistance += self.distance(currentCity, closestCity)
			currentCity = closestCity

		## Finally, we need to make a cycle back to the startCity
		visitedDistance += self.distance(currentCity, startCity)
		visitedCities[currentCity] = True
		## We have the visitedCities so can now return the tour
		return visitedCities, visitedDistance



	def minimumSpanningTree(self) -> Any:
		return

	def multiFragement(self) -> Any:
		return