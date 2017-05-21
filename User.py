import time

from pokedex.Pokedata import Pokedata


#--- Class User ---#
class User:

	# Initialize User
	def __init__(self, id, name=''):
		self.id = id
		self.name = name
		self.pokedata = None
		self.balance = {
			'money': 0,
			'cookies': 0,
			'caps': 0,
			'items': {},
		}
		self.timestamps = {
			'daily': 0,
			'attack': 0,
			'learn': 0,
			'setpoke': 0,
			'heal': 0,
		}
		self.statistics = {
			'battlesWon': 0,
			'battlesLost': 0,
			'damageDealt': 0,
			'damageTaken': 0,
		}

	# Debug printing
	def __repr__(self):
		return self.getTitle()


	#--- Save/Load ---#

	def serialize(self):
		return {
			'name': self.name,
			'pokedata': None if self.pokedata == None else self.pokedata.serialize(),
			'balance': self.balance,
			'timestamps': self.timestamps,
			'statistics': self.statistics,
		}

	## 
	# @param data: imported dictionary from json database
	def deserialize(self, data):
		def loadDict(var, name):
			if name in data:
				for key in var:
					if key in data[name]:
						var[key] = data[name][key]

		if 'name' in data:
			self.name = data['name']
		if 'pokedata' in data:
			if data['pokedata'] != None:
				self.pokedata = Pokedata(self)
				self.pokedata.deserialize(data['pokedata'])
		loadDict(self.balance, 'balance')
		loadDict(self.timestamps, 'timestamps')
		loadDict(self.statistics, 'statistics')


	#--- Identification ---#

	def getId(self):
		return self.id

	def getName(self):
		return self.name

	def getPokedata(self):
		return self.pokedata

	def createPokedata(self):
		self.pokedata = Pokedata(self)
		return self.pokedata


	#--- Balance ---#

	def getBalance(self):
		return self.balance['money']

	def incBalance(self, value):
		self.balance['money'] += value

	def getCookies(self):
		return self.balance['cookies']

	def incCookies(self, value):
		self.balance['cookies'] += value

	def getCaps(self):
		return self.balance['caps']

	def incCaps(self, value):
		self.balance['caps'] += value


	#--- Timestamps ---#

	def setTimestamp(self, name):
		self.timestamps[name] # Name check
		self.timestamps[name] = int(time.time())

	def getTimeRemaining(self, name, span):
		return span - (time.time() - self.timestamps[name])


	#--- Statistics ---#

	def getStatistic(self, name):
		return self.statistics[name]

	def incStatistic(self, name, value):
		self.statistics[name] # Name check
		self.statistics[name] += value
		return self.statistics[name]
