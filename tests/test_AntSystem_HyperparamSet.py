import sys
import copy
import pytest

sys.path.insert(0, "./src")
sys.path.insert(0, "../src")
from AntSystem import AntSystem


class Test_AntSystem_HyperparameterSetting:
	def test_NoneHyperparameters(self):
		AS = AntSystem()

		argument = None
		
		expectedValue = copy.deepcopy(AS.hyperparameters)

		AS._setHyperparameters(argument)
		assert AS.hyperparameters == expectedValue

	
	def test_InvalidTypeHyperparameter(self):
		AS = AntSystem()

		argument = []

		expectedException = Exception
		expectedMessage = f'The hyperparameters argument needs to be a dictionary, not a {type(argument)}'

		with pytest.raises(expected_exception=expectedException) as excinfo:
			AS._setHyperparameters(argument)

		assert str(excinfo.value) == expectedMessage

	
	def test_InvalidKeyHyperparameter(self):
		AS = AntSystem()

		randomKey = "randomKey"
		argument =  {
			f"{randomKey}": 0,
		}

		expectedException = Exception
		expectedMessage = f"The parameter {randomKey} is not a supported hyperparameter by the AntSystem class"

		with pytest.raises(expected_exception=expectedException) as excinfo:
			AS._setHyperparameters(argument)

		assert str(excinfo.value) == expectedMessage
	

	def test_InvalidKeysHyperparameter(self):
		AS = AntSystem()
		
		randomKey1 = "randomKey1"
		randomKey2 = "randomKey2"
		argument =  {
			f"{randomKey1}": 0,
			f"{randomKey2}": 0
		}

		expectedException = Exception
		expectedMessage = f"The parameter {randomKey1} is not a supported hyperparameter by the AntSystem class"

		with pytest.raises(expected_exception=expectedException) as excinfo:
			AS._setHyperparameters(argument)

		assert str(excinfo.value) == expectedMessage


	def test_InvalidTypeIntHyperparameter(self):
		AS = AntSystem()
		
		key = "alpha"
		valType = float
		argument =  {
			f"{key}": 0
		}

		expectedException = Exception
		expectedMessage = f"The parameter {key} needs to be a {valType}, not a {type(argument[key])}"

		with pytest.raises(expected_exception=expectedException) as excinfo:
			AS._setHyperparameters(argument)

		assert str(excinfo.value) == expectedMessage


	def test_InvalidTypeFloatHyperparameter(self):
		AS = AntSystem()
		
		key = "numberOfAnts"
		valType = int
		argument =  {
			f"{key}": 2.0
		}

		expectedException = Exception
		expectedMessage = f"The parameter {key} needs to be a {valType}, not a {type(argument[key])}"

		with pytest.raises(expected_exception=expectedException) as excinfo:
			AS._setHyperparameters(argument)

		assert str(excinfo.value) == expectedMessage






	## Testing float type ranges






	def test_ParameterFloatValueBelowRange(self):
		AS = AntSystem()
		
		key = "alpha"
		## valType = float

		## NOTE: This is the same values in the definition - they are displayed here for verbosity
		AntSystem._supportedHyperparameters[key]['start'] = 0.0
		AntSystem._supportedHyperparameters[key]['end'] = float('inf')

		argument =  {
			f"{key}": -1.0
		}

		expectedException = Exception
		expectedMessage = f"The parameter {key} needs to be a value in between {AntSystem._supportedHyperparameters[key]['start']} and {AntSystem()._supportedHyperparameters[key]['end']}"

		with pytest.raises(expected_exception=expectedException) as excinfo:
			AS._setHyperparameters(argument)

		assert str(excinfo.value) == expectedMessage


	def test_ParameterFloatValueAboveRange(self):
		AS = AntSystem()
		
		key = "alpha"
		## valType = float
		## NOTE: Modifying it to check behaviour when value above range
		AntSystem._supportedHyperparameters[key]['start'] = 0.0
		AntSystem._supportedHyperparameters[key]['end'] = 10.0

		argument =  {
			f"{key}": 11.3
		}

		expectedException = Exception
		expectedMessage = f"The parameter {key} needs to be a value in between {AntSystem._supportedHyperparameters[key]['start']} and {AntSystem()._supportedHyperparameters[key]['end']}"

		with pytest.raises(expected_exception=expectedException) as excinfo:
			AS._setHyperparameters(argument)

		assert str(excinfo.value) == expectedMessage

		## NOTE: Reseting the definition back to the original
		AntSystem._supportedHyperparameters[key]['start'] = 0.0
		AntSystem._supportedHyperparameters[key]['end'] = float('inf')


	def test_ParameterFloatValueOnLowerBound(self):
		AS = AntSystem()
		
		key = "alpha"
		## valType = float
		## NOTE: Modifying it to check behaviour when value above range

		argument =  {
			f"{key}": 0.0
		}

		expectedValue = copy.deepcopy(AS.hyperparameters)
		expectedValue[key] = 0.0
		AS._setHyperparameters(argument)
		assert AS.hyperparameters == expectedValue


	def test_ParameterFloatValueOnUpperBound(self):
		AS = AntSystem()
		
		key = "alpha"
		## valType = float
		argument =  {
			f"{key}": sys.float_info.max
		}
		
		expectedValue = copy.deepcopy(AS.hyperparameters)
		expectedValue[key] = sys.float_info.max

		AS._setHyperparameters(argument)
		assert AS.hyperparameters == expectedValue

	def test_ParameterFloatValueInRange(self):
		AS = AntSystem()
		
		key = "alpha"
		## valType = float

		argument =  {
			f"{key}": 10.2
		}

		expectedValue = copy.deepcopy(AS.hyperparameters)
		expectedValue[key] = argument[key]

		AS._setHyperparameters(argument)
		assert AS.hyperparameters == expectedValue






	## Testing int type ranges






	def test_ParameterIntValueBelowRange(self):
		AS = AntSystem()
		
		key = "maxIterations"
		## valType = int

		argument =  {
			f"{key}": 0
		}

		expectedException = Exception
		expectedMessage = f"The parameter {key} needs to be a value in between {AntSystem._supportedHyperparameters[key]['start']} and {AntSystem()._supportedHyperparameters[key]['end']}"

		with pytest.raises(expected_exception=expectedException) as excinfo:
			AS._setHyperparameters(argument)

		assert str(excinfo.value) == expectedMessage


	def test_ParameterIntValueAboveRange(self):
		AS = AntSystem()
		
		key = "maxIterations"
		## valType = int
		## NOTE: Modifying it to check behaviour when value above range
		AntSystem._supportedHyperparameters[key]['start'] = 1
		AntSystem._supportedHyperparameters[key]['end'] = 10

		argument =  {
			f"{key}": 12
		}

		expectedException = Exception
		expectedMessage = f"The parameter {key} needs to be a value in between {AntSystem._supportedHyperparameters[key]['start']} and {AntSystem()._supportedHyperparameters[key]['end']}"

		with pytest.raises(expected_exception=expectedException) as excinfo:
			AS._setHyperparameters(argument)

		assert str(excinfo.value) == expectedMessage

		## NOTE: Reseting the definition back to the original
		AntSystem._supportedHyperparameters[key]['start'] = 0
		AntSystem._supportedHyperparameters[key]['end'] = sys.maxsize


	def test_ParameterIntValueOnLowerBound(self):
		AS = AntSystem()
		
		key = "maxIterations"
		## valType = int
		argument =  {
			f"{key}": 1
		}

		expectedValue = copy.deepcopy(AS.hyperparameters)
		expectedValue[key] = 1
		AS._setHyperparameters(argument)
		assert AS.hyperparameters == expectedValue


	def test_ParameterIntValueOnUpperBound(self):
		AS = AntSystem()
		
		key = "maxIterations"
		## valType = int
		argument =  {
			f"{key}": sys.maxsize
		}
		
		expectedValue = copy.deepcopy(AS.hyperparameters)
		expectedValue[key] = sys.maxsize

		AS._setHyperparameters(argument)
		assert AS.hyperparameters == expectedValue

