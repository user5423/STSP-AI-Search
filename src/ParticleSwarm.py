from typing import List, Dict, Any, Set, Optional, Union, Tuple
import random
import sys
import math
from supportingDS import TSPInstance, TSPSolver

## TODO: It is possible that distance is float -- we need to check this
distanceType = int 
cityType = int
matrixType = List[List[distanceType]]
neighboursType = Set[cityType]
tourType = Dict[cityType, None]
velocityType = List[Tuple[cityType, cityType]]

## NOTE: I't would be better to subclass `ParticleSwarm` and `AntSystem` and create a superclass with
## basic functions needed by generic TSPSolvers (e.g. hyperparameter setting) and creating abstract methods

## BUG: Every time we execute PSO, the particles never change their routes
## Therefore after x iterations, there are only y tours every discovered
## where y is the number of particles. This means that our _runParticleIteration() is buggedS

## TODO: Perform a systematic sweep of the algorithm implementation

class Particle:
	def __init__(self, startTour: tourType, startVelocity: Any, startDistance: int) -> None:
		self.bestTour: tourType = startTour
		self.currentTour: tourType = startTour
		self.nextTour: Optional[tourType] = None

		self.bestDistance: int = startDistance
		self.currentDistance: int = startDistance

		self.currentVelocity: velocityType = startVelocity
		self.nextVelocity: Optional[velocityType] = None

		return None


class ParticleSwarm(TSPSolver):
	def __init__(self) -> None:
		super().__init__()
		self.particles: Optional[Set[Particle]] = set()
		self.TSPInstance: Optional[TSPInstance] = None
		self._bestTour = None
		self._bestDistance = float("inf")

		self.hyperparameters: Dict[str, Any] = {
			"maxIterations": 100000,	## TODO: Find out what a good rule of thumb is
			"numberOfParticles": 10,	## TODO: Find out what a good rule of thumb is
			"alpha": 0.7,			    ## The cognitive factor - Lecture recommends 0.5 <= x <= 1
			"beta": 2.8, 			    ## The social learning factor - Lecture recommends 2.5 <= x <= 3.0
			"theta": 0.50,              ## THe inertia function - Lecture Recommends 0.4 <= x <= 0.8
		}

		return None


	def _solve(self, distanceMatrix: matrixType, numberOfCities: int, hyperparameters: Optional[Dict[str, Any]] = None, timeLimit: float = 55.0) -> tourType:
		self._setHyperparameters(hyperparameters)
		self._initializeDataStructures(distanceMatrix, numberOfCities)
		
		## THis needs to be defined after the initialization of the particles
		self._bestTour, self._bestDistance = self._bestCurrentParticleTour()
		
		for _ in range(self.hyperparameters["maxIterations"]):
			self._runParticleMainBody()

		return None

	def _runParticleMainBody(self) -> None:
		## TODO: Rename this to something nicer
		for _ in range(self.hyperparameters["maxIterations"]):
			## NOTE: It is important to evaluate the structures and order of operations
			## as this formulas may use updated positions, when we wish to use the old one
			for particle in self.particles:
				self._runParticleIteration(particle)

			## Splitting the two for loops allows to avoid using new values instead of old ones if we use a non-global neighbourhood
			for particle in self.particles:
				self._cleanupForNextIteration(particle)

		return None

	def _returnResults(self) -> Tuple[List[int], int]:
		## TODO: Maybe check the current uncompleted iteration in case there was a better tour that wasn't updated yet
		return list(self._bestTour), self._bestDistance


	def _runParticleIteration(self, particle: Particle) -> None:
		# bestNeighbourhoodTour = self.getBestNeighbourhoodTour(particle)
		## NOTE: This is likley to be computationaly expensive, so consider ditching it,
		## and using the global values instead (e.g. _bestTour variable) 
		bestNeighbourhoodTour = self._bestTour
		# print("Calculating Next Tour")
		particle.nextTour = self._getNewParticlePosition(particle)
		# print("Calculating Next Velocity")
		particle.nextVelocity = self._getNewParticleVelocity(particle, bestNeighbourhoodTour)			
		# print("Calculating New Best Tour")
		particle.bestTour, particle.bestDistance = self._getNewParticleBestPosition(particle)
		# print(f"Particle Velocity Length: {len(particle.nextVelocity)}")

	def _cleanupForNextIteration(self, particle: Particle) -> None:
		particle.currentTour = particle.nextTour
		particle.nextTour = None
		particle.currentDistance = self._calculateTourDistance(particle.currentTour)

		particle.currentVelocity = particle.nextVelocity
		particle.nextVelocity = None

		if particle.bestDistance < self._bestDistance:
			print(f"New best distance: {self._bestDistance}")
			self._bestDistance = particle.bestDistance
			self._bestTour = particle.bestTour


	def _getNewParticlePosition(self, particle: Particle) -> tourType:
		## This applies the set of velocity (ammendments) to a tour to get a new tour (position)
		return self._applyAmmendments(particle.currentTour, particle.currentVelocity)


	## TODO: Consider adding memoization
	def _applyAmmendments(self, tour: tourType, velocity: velocityType) -> tourType:
		tourList = list(tour.keys())
		for first, second in velocity:
			temp = tourList[first]
			tourList[first] = tourList[second]
			tourList[second] = temp
		tour = dict.fromkeys(tourList, None)
		return tour


	def _getNewParticleVelocity(self, particle: Particle, bestNeighbourhoodTour: tourType) -> velocityType:
		## NOTE: The general formula is as below

		## p.nextVelocity = theta*p.currentVelocity + 
		## 					alpha*epsilon*(p.bestTour - p.currentTour) +
		##					beta*epsilon'*(p.bestNeighbourhoodTour - p.currentTour)

		alpha = self.hyperparameters["alpha"]
		beta = self.hyperparameters["beta"]
		theta = self.hyperparameters["theta"]

		## TODO: random.randint uses a uniform distribution, but we will want epsilon to be closer to 1
		epsilon1 = random.uniform(0.6,1.0)
		epsilon2 = random.uniform(0.6,1.0)

		velocity =  self._velocityMultiply(theta, particle.currentVelocity) + \
					self._velocityMultiply(alpha*epsilon1, self._tourSubtract(particle.bestTour, particle.currentTour)) + \
					self._velocityMultiply(beta*epsilon2, self._tourSubtract(bestNeighbourhoodTour, particle.currentTour))

		## NOTE: Works better without dimension limit
		# velocity = velocity[:self.TSPInstance.numberOfCities]
		return velocity


	def _velocityMultiply(self, constant: Union[int, float], velocity: velocityType) -> velocityType:
		velocityLength = len(velocity)
		return [velocity[i%velocityLength] for i in range(math.ceil(velocityLength*constant))]


	def _tourSubtract(self, firstTour: tourType, secondTour: tourType) -> velocityType:
		## NOTE: This performs a bubble swap against secondTour
		keyOrder = {city:counter for counter, city in enumerate(secondTour.keys())}
		workingTour = {counter:city for counter, city in enumerate(firstTour.keys())}
		ammendments = []
		## TODO: This requires performing bubble sort to get from firstTour --> secondTour using secondTour as the keys
		for _ in range(len(firstTour)):
			isSwapPerformed = False
			iterableTour = iter(workingTour.keys())
			currentCity = next(iterableTour)

			for counter, nextCity in enumerate(iterableTour, 1):
				if keyOrder[currentCity] > keyOrder[nextCity]:
					temp = workingTour[counter-1]
					workingTour[counter-1] = workingTour[counter]
					workingTour[counter] = temp

					isSwapPerformed = True
					ammendments.append((counter-1, counter))

			if isSwapPerformed is False:
				break

		return ammendments


	def _getNewParticleBestPosition(self, particle: Particle) -> tourType:
		if particle.currentDistance < particle.bestDistance:
			return particle.currentTour, particle.currentDistance
		return particle.bestTour, particle.bestDistance


	def _getBestNeighbourhoodTour(self, particle: Particle) -> tourType:
		## TODO: Implement a algorithm to get the best tour for all particles in the neighbourhood for all iterations performed
		...


	_supportedHyperparameters: Dict[str, Dict[str, Any]] = {
		"maxIterations": {"valType": int,
							"start": 1,
							"end": sys.maxsize
		},
		"numberOfParticles": {"valType": int, 
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
		"theta": {"valType": float,
					"start": 0.0,
					"end": sys.float_info.max
		},
						
	}


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
				definition = ParticleSwarm._supportedHyperparameters[key]
			except KeyError as e:
				raise Exception(f"The parameter {key} is not a supported hyperparameter by the `ParticleSwarm` class") from e

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
		self.particles = self._createParticles()
		return None


	def _createParticles(self) -> Set[Particle]:
		particles = set()
		for _ in range(self.hyperparameters["numberOfParticles"]):
			startTour = self._selectParticleStartTour()
			startVelocity = self._selectParticleStartVelocity()
			startDistance = self._calculateTourDistance(startTour)
			particles.add(Particle(startTour, startVelocity, startDistance))

		return particles


	def _selectParticleStartTour(self) -> tourType:
		return dict.fromkeys(random.sample(self.TSPInstance.cities, self.TSPInstance.numberOfCities), None)


	def _selectParticleStartVelocity(self) -> velocityType:
		## In continuous PSO, the velocity was easily randomized
		## --> The velocity was in R^d where velocity = {val_1, ..., val_d}
		## Here the velocity is descritized so needs to lead to another city

		## We could define the particle start to be a setthe of random swaps
		## --> How many swaps do we select??
		## ==> Maybe something relative to the number of cities??
		## --> How far away should the swaps be??
		## ==> Swaps that are close to each other may have less impact to the route

		## For now we'll do 20% rounded up of the self.TSPInstance.numberOfCities, or at least one swap
		velocity = [tuple(random.randint(0, self.TSPInstance.numberOfCities-1) for _ in range(2)) \
					for _ in range(max(5,self.TSPInstance.numberOfCities//10))]
		return velocity


	def _bestCurrentParticleTour(self):
		iterableParticles = iter(self.particles)
		firstParticle = next(iterableParticles)

		bestTour = firstParticle.currentTour
		bestDistance = self._calculateTourDistance(bestTour)

		for particle in iterableParticles:
			tour = particle.currentTour
			distance = self._calculateTourDistance(tour)
			if distance < bestDistance:
				bestDistance = distance
				bestTour = tour

		return bestTour, bestDistance


	## NOTE: Consider memoization -- but make sure to validate that it works with dict
	def _calculateTourDistance(self, tour: tourType) -> int:
		distance = 0
		iterableTour = iter(tour)
		startCity = next(iterableTour)
		currentCity = startCity
		for nextCity in iterableTour:
			distance += self.TSPInstance.distance(currentCity, nextCity)
			currentCity = nextCity

		## NOTE: We need to add the final distance from final city to the start city
		distance += self.TSPInstance.distance(currentCity, startCity)
		return distance

