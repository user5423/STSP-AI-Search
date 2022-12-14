## Consider hyperparameter automated setting and implementing a min-max system
## Here's a link https://www.diva-portal.org/smash/get/diva2:1214402/FULLTEXT01.pdf
import sys
import collections
from typing import Any, Dict, List, Set, Tuple

from AntSystem import AntSystem
from supportingDS import TSPInstance

distanceType = int 
cityType = int
matrixType = List[List[distanceType]]
neighboursType = Set[cityType]
tourType = Dict[cityType, None]

## TODO Our enhancement priorities in order are:
##      1. Implementing a function to automate ant and iterations setting (DONE)
##      2. Consider including Min and Max for pheremones (Doing)
##      3. Consider including only the best movement in the pheremone advancement (TODO)


class MaxMinAntSystem(AntSystem):
	def __init__(self):
		super().__init__()
		## NOTE: The below values that are listed as None, are automatically generated by the program
		self.hyperparameters: Dict[str, Any] = {
			"maxIterations": 10000,## TODO: Find out what a good rule of thumb is
			"numberOfAnts": None,	## TODO: Find out what a good rule of thumb is
			"alpha": 1.0,			## edge weighting in city selection (experimental says around 1 is a good value)
			"beta": 3.0,			## pheremone weighting in city selection (experimental says around 2 <= x <= 5 is a good value)
			"rho": 0.5,				## pheremone decay rate after a synchronized cycle
			"min_p": None,            ## the minimum pheremone rate ## TODO: Find a good value
			"max_p": None             ## the maximum pheremone rate ## TODO: Find a good value
		}


	_supportedHyperparameters: Dict[str, Dict[str, Any]] = {
		"alpha": {"valType": float,
					"start": 0.0,
					"end": sys.float_info.max
		},
		"beta": {"valType": float,
					"start": 0.0,
					"end": sys.float_info.max
		},
		"rho": {"valType": float,
					"start": 0.0,
					"end": 1.0
		},				
	}


	def _executeNewBestTourTrigger(self, bestDistance):
		self._calculateTauMax(bestDistance)

	def _initializeDataStructures(self, distanceMatrix: matrixType, numberOfCities: int) -> None:
		self.visitedEdges = collections.Counter()
		self.TSPInstance = TSPInstance(distanceMatrix, numberOfCities)
		self._setNumberOfAnts()
		self._setNumberOfIterations()

		self._bestTour, self._bestDistance = self.TSPInstance.nearestNeighbour()
		self._calculateTauMax(self._bestDistance)
		self._calculateTauMin()

		self.pheremoneMatrix = self._createPheremoneMatrix()
		self.ants = self._createAnts()

	def _createPheremoneMatrix(self):
		## If the initial pheremones is too low, then the initial movements of the ant will heavily influence future iterations
		## If the initial pheremones are too high, then the many iterations can be wasted by ants doing the same thing
		initialPheromoneDeposit = self.hyperparameters["max_p"]
		return [[initialPheromoneDeposit for _ in range(self.TSPInstance.numberOfCities)] for _ in range(self.TSPInstance.numberOfCities)]


	def _setNumberOfAnts(self) -> int:
		## This is quite important, but something that we want to pplary around with
		## Let's start using a constant multiplier
		# self.hyperparameters['numberOfAnts'] = 30
		self.hyperparameters['numberOfAnts'] = int(self.TSPInstance.numberOfCities * 0.3)
		## However, we could try with a gradient (i.e.) going from 30% to 20% as number of cities increase

	def _setNumberOfIterations(self) -> int:
		## This is pretty irrelevant during our timer as we will keep on executing until the solver class kicks us out
		self.hyperparameters['maxIterations'] //= self.hyperparameters["numberOfAnts"]


	def _advancePheremoneCycle(self) -> None:
		iterAnts = iter(self.ants)
		startAnt = next(iterAnts)

		worstAnts = []
		bestAnts = [startAnt]
		bestDistance = startAnt.tourDistance
		for ant in iterAnts:
			if ant.tourDistance < bestDistance:
				worstAnts.extend(bestAnts)
				bestAnts = [ant]
				bestDistance = ant.tourDistance
			elif ant.tourDistance == bestDistance:
				bestAnts.append(ant)
			else:
				worstAnts.append(ant)

		bestCityTrips = self._getBestIterationCities(bestAnts)
		worstCityTrips = self._getWorstIterationCities(worstAnts)


		## Now we need to perform the evaporation/deposit
		self._calculateNewPheremoneWorst(worstCityTrips)

		## If we have multiple best paths, then we use them all 
		self._calculateNewPheremoneBest(bestCityTrips, bestDistance)

	def _getBestIterationCities(self, bestAnts):
		bestCities = collections.Counter()
		for ant in bestAnts:
			iterableTour = iter(ant.tour)
			currentCity = next(iterableTour)
			for nextCity in iterableTour:
				self._addCityToCounter(bestCities, currentCity, nextCity)

			self._addCityToCounter(bestCities, ant.startCity, nextCity)

		return bestCities

	def _getWorstIterationCities(self, worstAnts):
		worstCities = set()
		for ant in worstAnts:
			iterableTour = iter(ant.tour)
			currentCity = next(iterableTour)
			for nextCity in iterableTour:
				self._addCityToSet(worstCities, currentCity, nextCity)

			self._addCityToSet(worstCities, ant.startCity, nextCity)

		return worstCities

	def _addCityToCounter(self, counter, current, destination):
		if counter[(current, destination)]:
			counter[(current, destination)] += 1
		elif counter[(destination, current)]:
			counter[(destination, current)] += 1
		else: 
			counter[(current, destination)] += 1

	def _addCityToSet(self, citySet, current, destination):
		if (current, destination) not in citySet and (destination, current) not in citySet:
			citySet.add((current, destination,))

	def _calculateNewPheremoneBest(self, bestCityTrips: collections.Counter[Tuple[cityType, cityType]], bestDistance: float) -> None:
		deposit = 1 / bestDistance if bestDistance != 0 else float("inf")
		## TODO: Consider doubling up for cities that overlap between ants
		for (currentCity, nextCity), count in bestCityTrips.items():
			evaporation = (1 - self.hyperparameters['rho']) * self.pheremoneMatrix[currentCity][nextCity]
			newPheremoneLevel = evaporation + deposit
			## NOTE: We added a basic pheremone min max system here !!!!
			newPheremoneLevel = self._employMinMaxPheremoneBoundaries(newPheremoneLevel)
			self.pheremoneMatrix[currentCity][nextCity] = newPheremoneLevel
			self.pheremoneMatrix[nextCity][currentCity] = newPheremoneLevel

	def _calculateNewPheremoneWorst(self, worstCityTrips: Set[Tuple[cityType, cityType]]) -> None:
		## TODO: Consider doubling up for cities that overlap between ants
		for currentCity, nextCity in worstCityTrips:
			evaporation = (1 - self.hyperparameters['rho']) * self.pheremoneMatrix[currentCity][nextCity]
			newPheremoneLevel = evaporation ## There is no adding of values here
			## NOTE: We added a basic pheremone min max system here !!!!
			newPheremoneLevel = self._employMinMaxPheremoneBoundaries(newPheremoneLevel)
			self.pheremoneMatrix[currentCity][nextCity] = newPheremoneLevel
			self.pheremoneMatrix[nextCity][currentCity] = newPheremoneLevel


	def _employMinMaxPheremoneBoundaries(self, newPheremoneLevel: float) -> float:
		if newPheremoneLevel > self.hyperparameters['max_p']:
			newPheremoneLevel = self.hyperparameters['max_p']
		elif newPheremoneLevel < self.hyperparameters['min_p']:
			newPheremoneLevel = self.hyperparameters['min_p']
		return newPheremoneLevel

	def _calculateTauMax(self, bestDistance):
		self.hyperparameters["max_p"] = 1 / (self.hyperparameters["rho"] * bestDistance)

	def _calculateTauMin(self):
		## https://stackoverflow.com/questions/30056657/in-a-max-min-ant-system-mmas-how-does-the-initial-pheromone-depend-on-the-bes
		n = self.hyperparameters["maxIterations"]
		self.hyperparameters["min_p"] = self.hyperparameters["max_p"] * (1-(0.05)**(1/n))/((n/2-1)*(0.05)**(1/n))



def main() -> None:
	distanceMatrix = [] ## NOTE: This will need to be loaded in from a file (or defined here)
	numberOfCities = len(distanceMatrix)

	## NOTE: You can add another potiional argument "hyperparameters" to tune the hyperparamaeters
	MMAS = MaxMinAntSystem()
	MMAS.run(distanceMatrix, numberOfCities, timer=59.0)

if __name__ == "__main__":
	main()


	