import asyncio, time

#--- Class Channel ---#
class Channel:

	# Initialize Channel
	def __init__(self, id, name=''):
		self.id = id
		self.name = name
		
		self.weather = None
		self.timestamps = {
			'weather': 0,
		}
		self.statistics = {
			'weather': 0,
		}

	# Debug printing
	def __repr__(self):
		return '#' + self.getName()


	#--- Save/Load ---#

	def serialize(self):
		return {
			'weather': self.weather,
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

		if 'weather' in data:
			self.weather = data['weather']
		loadDict(self.timestamps, 'timestamps')
		loadDict(self.statistics, 'statistics')


	#--- Identification ---#

	def getId(self):
		return self.id

	def getName(self):
		return self.name


	#--- Weather, Pokemon ---#

	def getWeather(self):
		return self.weather

	def setWeather(self, weather):
		self.weather = weather


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
