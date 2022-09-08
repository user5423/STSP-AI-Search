# https://www.researchgate.net/publication/281415529_A_combination_of_genetic_algorithm_and_particle_swarm_optimization_method_for_solving_traveling_salesman_problem
import math
import random
from typing import List, Dict, Set, Tuple, Optional, Any

from ParticleSwarm import ParticleSwarm

## TODO: It is possible that distance is float -- we need to check this
distanceType = int 
cityType = int
matrixType = List[List[distanceType]]
neighboursType = Set[cityType]
tourType = Dict[cityType, None]
velocityType = List[Tuple[cityType, cityType]]



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

class GeneticParticle:
	def __init__(self, startTour: tourType, startDistance: int) -> None:
		self.bestTour: tourType = startTour
		self.bestDistance: int = startDistance

		self.currentTour: tourType = startTour
		self.currentDistance: int = startDistance






class GeneticParticleSwarm(ParticleSwarm):
	def __init__(self) -> None:
		## TODO: Need to find out what improvements can be made first
		super().__init__()
		self.hyperparameters: Dict[str, Any] = {
			"maxIterations": 10000,	## TODO: Find out what a good rule of thumb is
			"numberOfParticles": 100,	## TODO: Find out what a good rule of thumb is
			"alpha": 0.7,			    ## The cognitive factor - Lecture recommends 0.5 <= x <= 1
			"beta": 2.8, 			    ## The social learning factor - Lecture recommends 2.5 <= x <= 3.0
			"theta": 0.50,              ## THe inertia function - Lecture Recommends 0.4 <= x <= 0.8
		}

	def _createParticles(self):
		particles = set()
		for _ in range(self.hyperparameters["numberOfParticles"]):
			startTour = self._selectParticleStartTour()
			startDistance = self._calculateTourDistance(startTour)
			particles.add(GeneticParticle(startTour, startDistance))
		return particles

	def _selectParticleStartTour(self):
		tour, _ = self.TSPInstance.nearestNeighbour()
		return tour

	def _heuristicCrossover(self, tour1: tourType, tour2: tourType) -> tourType:
		## THis takes two tours and ouputs a single one
		tourList1 = self._tourToList(tour1)
		tourList2 = self._tourToList(tour2)

		outputTourList = []
		outputTourDict = {}
		x = 0
		while x < max(2,math.ceil(self.TSPInstance.numberOfCities//10)):
			selectedCity = self._selectRandomCity()
			if selectedCity not in outputTourList:
				outputTourList.append(selectedCity)
				outputTourDict[selectedCity] = True
				x += 1

		## NOTE: Divergences between report and pseudocode
		## There's somehting fucked with the pseucode presented in the report
		## There's some weird expression in the while loop condition, and the
		## counters i and j are set to 2 (I believe they are using 1-indexing)
		i = j = 0
		while len(outputTourList) != self.TSPInstance.numberOfCities:
			if tourList1[i] in outputTourDict and tourList2[j] in outputTourDict:
				## we skip crossover iteration, and increment both counters
				i =  min(i+1, self.TSPInstance.numberOfCities-1)
				j =  min(j+1, self.TSPInstance.numberOfCities-1)
			elif tourList1[i] in outputTourDict:
				## We concatenate tourList[j] into the output (since it is not there yet)
				outputTourDict[tourList2[j]] = True
				outputTourList.append(tourList2[j])
				j =  min(j+1, self.TSPInstance.numberOfCities-1)
			elif tourList2[j] in outputTourDict:
				## We concatenate tourList[i] into the output (since it is not there yet)
				outputTourDict[tourList1[i]] = True
				outputTourList.append(tourList1[i])
				i =  min(i+1, self.TSPInstance.numberOfCities-1)
			else:
				lastCity = outputTourList[-1]
				if self.TSPInstance.distance(lastCity, tourList1[i]) \
					 < self.TSPInstance.distance(lastCity, tourList2[j]):
					outputTourList.append(tourList1[i])
					outputTourDict[tourList1[i]] = True
					i =  min(i+1, self.TSPInstance.numberOfCities-1)
				else:
					outputTourList.append(tourList2[j])
					outputTourDict[tourList2[j]] = True
					j =  min(j+1, self.TSPInstance.numberOfCities-1)

		return outputTourDict

	def _runParticleMainBody(self) -> None:
		for particle in self.particles:
			childTour = self._heuristicCrossover(particle.bestTour, self._bestTour)
			childTourDistance = self._calculateTourDistance(childTour)
			
			if childTourDistance < particle.bestDistance:
				particle.childTour = childTour
				particle.bestDistance = childTourDistance

			if childTourDistance < self._bestDistance:
				self._bestTour = childTour
				self._bestDistance = childTourDistance
				
		## Insert the selected City at the beginning of both solutions
	def _tourToList(self, tour: tourType) -> List[int]:
		return list(tour.keys())

	def _selectRandomCity(self):
		return random.randint(0, self.TSPInstance.numberOfCities-1)


def main() -> None:
	distanceMatrix = [] ## NOTE: This will need to be loaded in from a file (or defined here)
	numberOfCities = len(distanceMatrix)

	## NOTE: You can add another potiional argument "hyperparameters" to tune the hyperparmaeters
	GPS = GeneticParticleSwarm()
	GPS.run(distanceMatrix, numberOfCities, timer=59.0)


if __name__ == "__main__":
	main()
  