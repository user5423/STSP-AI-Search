from typing import List, Dict, Any, Set, Optional, Union, Tuple, Counter
import random
import collections
import sys
from supportingDS import TSPInstance, TSPSolver

## TODO: It is possible that distance is float -- we need to check this
distanceType = int 
cityType = int
matrixType = List[List[distanceType]]
neighboursType = Set[cityType]
tourType = Dict[cityType, None]


## BUG: Replace sets with OrderedSet equivealent (e.g. dict or collections.MutableSet)
## IMPORTANT!: Python sets are unordered so the code built so far will not work as anticipated

## TODO: There is no point using collections.counter for visitedEdges as the deposit can only
## be calculated after all ants have completed their cycles

## TODO: We need to handle redundancy in the matrix (i.e. city i --> j means that city j --> i need to be updated)
## I feel like it is possible that there are instances in the below code were we haven't handled this redundancy correctly

class Ant:
	def __init__(self, startCity: cityType) -> None:
		self.tour: tourType = {startCity: None}
		self.startCity: cityType = startCity
		self.tourDistance: distanceType = 0


class AntSystem(TSPSolver):
	def __init__(self) -> None:
		super().__init__()
		self.ants: Optional[Set[Ant]] = set()
		self.TSPInstance: Optional[TSPInstance] = None
		self.visitedEdges: Optional[Counter] = None
		self.pheremoneMatrix: Optional[List[List[float]]]= None

		## TODO: What should we set the initial best tour to?? RANDOM tour??
		self._bestTour = None
		self._bestDistance = float('inf')

		self._bestIterationTour = None
		self._bestIterationDistance = float('inf')

		self.hyperparameters: Dict[str, Any] = {
			"maxIterations": 100000,## TODO: Find out what a good rule of thumb is
			"numberOfAnts": 30,		## TODO: Find out what a good rule of thumb is
			"alpha": 1.0,			## edge weighting in city selection (experimental says around 1 is a good value)
			"beta": 3.0,			## pheremone weighting in city selection (experimental says around 2 <= x <= 5 is a good value)
			"rho": 0.5				## pheremone decay rate after a synchronized cycle
		}

		return None

	_supportedHyperparameters: Dict[str, Dict[str, Any]] = {
		"maxIterations": {"valType": int,
							"start": 1,
							"end": sys.maxsize
		},
		"numberOfAnts": {"valType": int, 
							"start": 1,
							"end": sys.maxsize
		},
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
		
	## NOTE: We split up iteration best from all time best to enable a elitist of minmax style _advancePheremoneCycle() method
	def _solve(self, distanceMatrix: matrixType, 
					 numberOfCities: int, 
					 hyperparameters: Optional[Dict[str, Any]] = None) -> None:

		self._setHyperparameters(hyperparameters)
		self._initializeDataStructures(distanceMatrix, numberOfCities)

		for i in range(self.hyperparameters['maxIterations']):
			self._bestIterationTour = None
			self._bestIterationDistance = float('inf')

			for ant in self.ants:
				self._runAntCycle(ant)

			## We then check whether this iteration beat the previous best
			if self._bestIterationDistance < self._bestDistance:
				self._bestTour = self._bestIterationTour
				self._bestDistance = self._bestIterationDistance
				self._executeNewBestTourTrigger(self._bestDistance)

			## This method should handle evaporation and deposit of pheremones
			self._advancePheremoneCycle()
			## Between cycles, we want to reset the tour and tourDistance
			self._resetAntCycle()

		return None

	
	def _executeNewBestTourTrigger(self, bestDistance):
		...

	def _returnResults(self) -> Tuple[List[int], int]:
		## TODO: Maybe check the current uncompleted iteration in case there was a better tour that wasn't updated yet
		if self._bestIterationDistance < self._bestDistance:
			return list(self._bestIterationTour), self._bestIterationDistance
		return list(self._bestTour), self._bestDistance
  

	def _setHyperparameters(self, hyperparameters: Optional[Dict[str, any]] = None) -> None:
		## Checks the hyperparameter object type
		if hyperparameters is None:
			return
		elif not isinstance(hyperparameters, dict):
			print(type(hyperparameters))
			raise Exception(f'The hyperparameters argument needs to be a dictionary, not a {type(hyperparameters)}')
		
		for key, val in hyperparameters.items():
			## Checks parameter existence
			try:
				definition = AntSystem._supportedHyperparameters[key]
			except KeyError as e:
				raise Exception(f"The parameter {key} is not a supported hyperparameter by the AntSystem class") from e

			## Checks parameter  type
			if not isinstance(val, definition['valType']):
				raise Exception(f"The parameter {key} needs to be a {definition['valType']}, not a {type(val)}")
				
			## Checks parameter value
			if definition['valType'] in (int, float):
				if not (definition['start'] <= val <= definition['end']):
					raise Exception(f"The parameter {key} needs to be a value in between {definition['start']} and {definition['end']}")
			
			## Finally set the new hyperparameter value
			self.hyperparameters[key] = val


	def _initializeDataStructures(self, distanceMatrix: matrixType, numberOfCities: int) -> None:
		self.TSPInstance = TSPInstance(distanceMatrix, numberOfCities)
		self.visitedEdges = collections.Counter()
		self.pheremoneMatrix = self._createPheremoneMatrix()
		self.ants = self._createAnts()


	def _createPheremoneMatrix(self) -> None:
		## If the initial pheremones is too low, then the initial movements of the ant will heavily influence future iterations
		## If the initial pheremones are too high, then the many iterations can be wasted by ants doing the same thing
		initialPheromoneDeposit = self._getInitialPheremoneDeposit()
		return [[initialPheromoneDeposit for _ in range(self.TSPInstance.numberOfCities)] for _ in range(self.TSPInstance.numberOfCities)]

		## NOTE: If you use * multipication you set each of the rows to look at the same array (Is this a python bug??)
		## BUG: On the second multiplication, the rows get reused which means that 2d_matrix[row] is the same as 2d_matrix[all_rows]
		## return [[initialPheremonDeposit] * self.TSPInstance.numberOfCities] * self.TSPInstance.numberOfCities


	def _getInitialPheremoneDeposit(self) -> None:
		## NOTE: The lecture provided a basic method of using NearestNeighbour to get a tour, and then 
		## using a mathematical formula to calculate the general spread of pheremones across each vertex
		_, distance = self.TSPInstance.nearestNeighbour()
		## NOTE: In the lecture the formula was initialDeposit = N/L^nn (i.e. numberOfCities / distance of NN tour)
		if distance >= 0:
			return self.TSPInstance.numberOfCities / distance
		elif distance == 0:
			return float("inf")
		else:
			raise Exception("This program does not support TSP Instances that have negative distances")


	def _advancePheremoneCycle(self) -> None:

		## Calculate the deposits
		deposits = {}
		for ant in self.ants:
			self._calculateAntDeposit(ant, deposits)

		## Calculate new pheremone using deposits and constant evaporation rate rho
		self._calculateNewPheremone(deposits)


	def _calculateAntDeposit(self, ant, deposits):
			## NOTE: The lecture provided a basic mathematical formula to calculate this, which we will use for our basic implememntation at the moment.
			iterableTour = iter(ant.tour)
			currentCity = next(iterableTour)
			for nextCity in iterableTour:
				deposit = self._calculatePheremoneDeposit(currentCity, nextCity, ant.tourDistance)
				self._incrementDepositDistance(deposits, deposit, currentCity, nextCity)
				currentCity = nextCity

			## We also need to add the distance of the final city back to the startCity
			## NOTE: Instead of going from current --> start (i.e. chronologically), we are going the same way
			## as it is symmetric TSP so doens't matter -- it in fact helps us reduce redundancy
			deposit = self._calculatePheremoneDeposit(ant.startCity, currentCity, ant.tourDistance)
			self._incrementDepositDistance(deposits, deposit, ant.startCity, currentCity)


	def _calculatePheremoneDeposit(self, startCity: cityType, currentCity: cityType, tourDistance: int) -> float:
		if tourDistance > 0:
			return self.TSPInstance.distance(startCity, currentCity) / tourDistance
		return float("inf")


	def _calculateNewPheremone(self, deposits: Dict[Tuple[cityType, cityType], float]) -> None:
		## Calculate the evaporation, and update the pheremone matrix with the new values
		for (currentCity, nextCity), deposit in deposits.items():
			evaporation = (1 - self.hyperparameters['rho']) * self.pheremoneMatrix[currentCity][nextCity]
			newPheremoneLevel = evaporation + deposit ## NOTE: Elist Ant System adds an additional weighting to the best route's edges
			self.pheremoneMatrix[currentCity][nextCity] = newPheremoneLevel
			self.pheremoneMatrix[nextCity][currentCity] = newPheremoneLevel


	def _incrementDepositDistance(self, dictionary: Dict[Tuple[int, int], Union[int, float]], value: Union[int, float], currentCity: cityType, nextCity: cityType) -> None:
		## NOTE: This is a STSP (I think), so we need to ensure that any matrices don't have redundant mismatches
		## ==> Hence updating values in both directions
		if dictionary.get((currentCity, nextCity)):
			dictionary[(currentCity, nextCity)] += value
		elif dictionary.get((nextCity, currentCity)):
			dictionary[(nextCity, currentCity)] += value
		else:
			dictionary[(currentCity, nextCity)] = value


	def _runAntCycle(self, ant: Ant) -> None:
		## NOTE: THis is the main body that directs the ant on how to perform its cycle
		currentCity = ant.startCity
		## NOTE: This is not needed as the ant is already initialied with the startCity
		## ant.tour[currentCity] = None 
		for _ in range(self.TSPInstance.numberOfCities-1):
			selectedCity = self._probabilisticallySelectNextCity(ant, currentCity)
			self._incrementVisitedEdges(currentCity, selectedCity)
			ant.tour[selectedCity] = None
			ant.tourDistance += self.TSPInstance.distance(currentCity, selectedCity)
			currentCity = selectedCity

		## NOTE: We still need to add the final edge from endCity ---> startCity
		self._incrementVisitedEdges(currentCity, selectedCity)
		ant.tourDistance += self.TSPInstance.distance(selectedCity, ant.startCity)
		## We need to ensure that we keep track of the best-tour in the current iteration
		self._updateBestIterationTour(ant.tour, ant.tourDistance)


	def _incrementVisitedEdges(self, currentCity: cityType, selectedCity: cityType) -> None:
		self.visitedEdges[(currentCity, selectedCity)] += 1


	def _updateBestIterationTour(self, tour: tourType, tourDistance: int) -> None:
		if tourDistance < self._bestIterationDistance:
			self._bestIterationTour = tour
			self._bestIterationDistance = tourDistance


	def _probabilisticallySelectNextCity(self, ant: Ant,  currentCity: cityType) -> cityType:
		## TODO: Evaluate the code below to see if the time complexity can be improved
		denominator = 0
		numerators = []
		probabilities = []

		for neighbour, distance in enumerate(self.TSPInstance.neighbours(currentCity)):
			if neighbour not in ant.tour:
				pheremoneLevel = self.pheremoneMatrix[currentCity][neighbour]
				heuristicDesirability = 100000000 if distance == 0 else 1 / distance
				## NOTE: Weird things happen at infinity !!!
				numerator = (pheremoneLevel**self.hyperparameters['alpha']) * (heuristicDesirability**self.hyperparameters['beta'])
				# input(numerator)
				numerators.append((neighbour, numerator))
				denominator += numerator

		## With the numerators and denominator we can calculate each of the probabilities
		for neighbour, numerator in numerators:
			probabilities.append((neighbour, numerator/denominator))

		## Now that we have the exact probabilities of each neighbour, we can now select the city
		## NOTE: Maybe this could use structure the problem so that we can use binary search 
		## (e.g. logarithmic time complexity instead of linear time)
		selectedProbability = random.uniform(0, 1)
		cumulativeProbability = 0
		selectedCity = None
		for neighbour, probability in probabilities:
			cumulativeProbability += probability
			if cumulativeProbability >= selectedProbability:
				selectedCity = neighbour
				break

		if selectedCity is None:
			## BUG: There may be an issue where cumulativeprobability (0.9999) >= selectedProbability (1) due to floating point inprecission
			raise Exception("There was no city selected when trying to create an ant-cycle")

		return selectedCity


	def _createAnts(self) -> None:
		## NOTE: How should we place ants on vertices??
		return {Ant(self._selectAntPlacement()) for _ in range(self.hyperparameters['numberOfAnts'])}
		
	
	def _selectAntPlacement(self) -> cityType:
		## NOTE: This is a hyperparameter method -- Right now, we want our basic implementation up and 
		##running so we will provide a basic method with no way to swap in a new strategy (method)
		## NOTE: For now we'll use a uniform distribution to randomly select cities (excluding overlapping)
		_initialPlacements = set()

		## TODO: Remove this exception, it's fine for multiple ants to start on the same city
		if self.TSPInstance.numberOfCities - len(_initialPlacements) > 0:
			while ((startCity := random.randint(0, self.TSPInstance.numberOfCities-1)) in _initialPlacements): pass
			_initialPlacements.add(startCity)
			return startCity
		else:
			raise Exception("Too Many Ants for the number of cities")

	
	def _resetAntCycle(self) -> None:
		for ant in self.ants:
			ant.tourDistance = 0
			ant.tour = {ant.startCity: None}

		self.visitedEdges.clear()


def main() -> None:
	AS = AntSystem()
	AS.run(timer=59.0)


if __name__ == "__main__":
	main()
  