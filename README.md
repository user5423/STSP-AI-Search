# STPS AI Search

This provides two AI Search ALgorithms adapted for TSP Search Problem.
Additionally, each algorithm contains their own enhancements.

The following search algorithms implemented in python are:
1. Ant System
2. Min Max Ant System
3. Particle Swarm
4. Genetic Particle Swarm

### Usage

Usage is pretty simple, all search algorithms implement the same interface

```
## First you want to load a matrix that contains distances betwen each city
## This should be a n*n matrix where n = number of cities
## You'll likely want to load them in from a file

distanceMatrix = [[...],...]
numberOfCities = len(distanceMatrix)


## Searching TSP Matrix using Ant System (w/ default time = 59 seconds)
AS = AntSystem()
AS.run(distanceMatrix, numberOfCities)

## Searching TSP Matrix using Particle System (w/ custom time = 30 seconds)
PS = ParticleSwarm()
PS.run(distanceMatrix, numberOfCities, timer=30)

## Searching TSP Matrix using Genetic Particle Swarm (which runs until default iteration limit exhausted)
GPS = GeneticParticleSwarm()
GPS.run(distanceMatrix, numberOfCities, timer=-1)

## Searching TSP Matrix using Max Min Ant System (w/ custom hyperparameters)
hyperparams = {"iterations": 10000}
MMAS = MinMaxAntSystem()
MMAS.run(dinstanceMatrix, numberOfCities, hyperparams)

```

To customize the hyperparams, take a look at the the source code. There should
be a class attribute called __supportedHyperparameters that provide you with
information on the available parameters

If you don't specify a specific hyperparameter in the dictionary you pass into
the `searchClass.run()` method, then the default hyperparameter is taken which
should be found in the `searchClass__init__()` method as `self.hyperparameters`


### NOTE

This code has been repurposed from coursework that I worked on.
This had certain implementation restrictions which explains certain implementation details
I modified it quickly to be more user-friendly, but there are no guarantees
Although there is some testing for Ant System, there is no testing performed for Particle Swarm

