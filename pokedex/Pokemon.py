import random, math


#--- Class Pokemon ---#
class Pokemon:

	# Initialize Pokemon
	# @param data: imported dictionary from json database
	def __init__(self, data):
		self._data = data

	# Debug printing
	def __repr__(self):
		return self.getTitle()


	#--- Identification ---#

	def getId(self):
		return self._data['id']
	
	def getName(self):
		return self._data['name']


	#--- About ---#

	def getTitle(self):
		return self._data["title"]

	def getSpecies(self):
		return self._data["species"]

	def getOrder(self):
		return self._data["order"]

	def getForms(self):
		return self._data["forms"]

	def getHeight(self):
		return self._data["height"]

	def getWeight(self):
		return self._data["weight"]


	#--- Battle ---#

	def getTypes(self):
		return self._data["types"]

	def getStats(self):
		return self._data["stats"]

	def getMoves(self):
		return self._data["moves"]

	def getAbilities(self):
		return self._data["abilities"]


	#--- Reward ---#

	def getBaseExperience(self):
		return self._data["base_experience"]

	def getEffort(self):
		return self._data["effort"]

	def getHeldItems(self):
		return self._data["held_items"]
