import math, random

from pokedex.tables import *
from pokedex.pokedexManager import getPokemonByName, getMoveByName


#--- Class Pokedata ---#
class Pokedata:

	# Initialize Pokedata
	def __init__(self, owner):
		self.owner = owner
		self.pokeName = ''
		self.title = ''
		self.pokeObj = None

		# Body
		self.nature = ''
		self.iv = {s:0 for s in stats}
		self.ev = {s:0 for s in stats}
		self.heldItem = ''

		# Battle, reset upon heal
		self.hp = 0
		self.stages = {s:0 for s in stageStats}
		self.status = []
		self.turnCount = {}
		self.isFlinched = False
		self.moveset = [{'move': None, 'pp': 0, 'max': 0} for m in range(4)]

		# Copy statistics from User.
		# User stores all-time stats, while Pokedata stores for the current Pokemon.
		self.statistics = {key:0 for key in owner.statistics}

	# Debug printing
	def __repr__(self):
		return '**{}**'.format(self.getTitle())


	#--- Save/Load ---#

	def serialize(self):
		return {
			'pokeName': self.pokeName,
			'title': self.title,

			# Body
			'nature': self.nature,
			'iv': self.iv,
			'ev': self.ev,
			'heldItem': self.heldItem,

			# Battle, reset upon heal
			'hp': self.hp,
			'stages': self.stages,
			'status': self.status,
			'turnCount': self.turnCount,
			'isFlinched': self.isFlinched,
			'moveset': self.moveset,

			# Fun trivia
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

		if 'pokeName' in data:
			self.pokeName = data['pokeName']
			self.pokeObj = None
		if 'title' in data:
			self.title = data['title']

		# Body
		if 'nature' in data:
			self.nature = data['nature']
		if 'iv' in data:
			self.iv = data['iv']
		if 'ev' in data:
			self.ev = data['ev']
		if 'heldItem' in data:
			self.heldItem = data['heldItem']

		# Battle, reset upon heal
		if 'hp' in data:
			self.hp = data['hp']
		if 'stages' in data:
			self.stages = data['stages']
		if 'status' in data:
			self.status = data['status']
		if 'turnCount' in data:
			self.turnCount = data['turnCount']
		if 'isFlinched' in data:
			self.isFlinched = data['isFlinched']
		if 'moveset' in data:
			self.moveset = data['moveset']

		# Fun trivia
		loadDict(self.statistics, 'statistics')

	# Initialize data by setting start vales from the selected pokemon
	def initialize(self, pokemon):
		self.pokeName = pokemon.getName()
		self.pokeObj = pokemon
		self.title = pokemon.getTitle()
		self.nature = random.choice(list(natures.keys()))
		self.iv = {s:random.randint(0,31) for s in stats}
		self.hp = self.getStat('HP')


	#--- Identification ---#

	# User object that created this instance
	def getOwner(self):
		return self.owner

	# Return Pokemon object of current species
	def getPokemon(self):
		if self.pokeObj:
			return self.pokeObj
		self.pokeObj = getPokemonByName(self.pokeName)
		return self.pokeObj

	def getPokeName(self):
		return self.pokeName

	def getTitle(self):
		return self.title


	#--- Body ---#

	def getNature(self):
		return self.nature

	def getHeldItem(self):
		return self.heldItem


	#--- EV/IV ---#

	def getIV(self):
		return self.iv

	def maxIV(self, stat):
		if self.iv[stat] == 31:
			raise UserWarning("Your @pokemon has already fully hypertrained its {}!".format(stat))
		self.iv[stat] = 31

	def getEV(self):
		return self.ev

	def trainEV(self, value, stat):
		totalRemaining = 510 - sum(self.ev.values())
		if totalRemaining <= 0:
			raise UserWarning("Your @pokemon is already fully trained!")
		if value <= 0:
			raise UserWarning("@mention Invalid value. Please specify a value between (1–252)!")

		remaining = 252 - self.ev[stat]
		if remaining <= 0:
			raise UserWarning("Your @pokemon has already fully trained its {}-EV!".format(stat))

		inc = min(value, remaining, totalRemaining)
		self.ev[stat] += inc
		return inc

	def resetEV(self, stat=None):
		if stat:
			stat = checkStat(stat)
			self.ev[stat] = 0
		else:
			self.ev = {s:0 for s in stats}


	#--- Stats ---#

	# Return current stats
	def getStats(self):
		return {s: self.getStat(s) for s in stats}

	# Return current stat by combining base, iv, ev, nature
	def getStat(self, stat):
		if self.getPokemon() == 'shedinja' and stat == 'HP':
			return 1

		# Level 50
		basic = (60) if stat == 'HP' else (5)
		base = self.getPokemon().getStat(stat)
		iv, ev = self.iv[stat], self.ev[stat]

		value = basic + int( base + iv/2 + ev//4/2 )
		value = int( value * self.natureMod(stat) )

		# Please move this to attack?
		if stat == 'Speed' and self.hasStatus('paralysis'):
			value //= 2

		return value

	# Return stat modifier for a nature
	def natureMod(self, stat):
		return natures[self.nature][stats.index(stat)]


	#--- Health ---#

	def getHp(self):
		return self.hp

	def damage(self, damage):
		self.hp -= damage
		self.hp = max(0, min(self.getStat('HP'), self.hp))
		return self.hp

	def heal(self, healing):
		return self.damage(-healing)

	# Reset hp, stages, status, pp.
	# Could separate into smaller functions for more specific healing items
	def fullRestore(self):
		self.hp = self.getStat('HP')
		self.stages = {s:0 for s in stageStats}
		self.status = []
		self.turnCount = {}
		self.isFlinched = False
		for m in range(4):
			self.moveset[m]['pp'] = self.moveset[m]['max']


	#--- Stages ---#

	def getStages(self):
		return self.stages

	# Increase stage by value and return the difference
	def raiseStage(self, stat, value):
		oldValue = self.stages[stat]
		self.stages[stat] = max(-6, min(6, self.stages[stat] + value))
		return self.stages[stat] - oldValue

	def stageMod(self, stat):
		stage = self.stages[stat]
		if stat in ['Evasion', 'Accuracy']:
			if stage >= 0:
				return (3+stage)/3
			else:
				return 3/(3-stage)
		else:
			if stage >= 0:
				return (2+stage)/2
			else:
				return 2/(2-stage)


	#--- Battle ---#

	def getStatus(self):
		return self.status

	def hasStatus(self, status):
		return status in self.status

	def addStatus(self, newStatus):
		if self.hasStatus(newStatus):
			return False
		if newStatus in ailmentsSpecial:
			for s in ailmentsSpecial:
				if s in self.status:
					return False
		self.status.append(newStatus)
		return True

	def clearStatus(self, status):
		self.status.remove(status)

	def getTurnCount(self, name):
		return self.turnCount[name]

	def startTurnCount(self, name):
		self.turnCount[name] = 0

	def incTurnCount(self):
		for key in self.turnCount:
			self.turnCount[key] += 1

	def clearTurnCount(self, name):
		self.turnCount.pop(name, None)

	def setFlinched(self):
		self.isFlinched = True

	def toggleFlinch(self):
		flinched = self.isFlinched
		self.isFlinched = False
		return flinched

	def getAttackCooldown(self):
		mod = self.stageMod('Speed')
		speed = self.getStat('Speed')
		cooldown = 30 - speed*mod/51
		return cooldown


	#--- Moves ---#

	def getMoveset(self):
		return self.moveset

	def getMovesetTable(self):
		table = []
		for i in range(4):
			move = self.moveset[i]
			if move['move']:
				row = '{}) {} ({}/{})'.format(i+1, move['move'], move['pp'], move['max'])
			else:
				row = '{}) -'.format(i+1)
			table.append(row)
		return "```Python\n{}```".format('\n'.join(table))

	# Return the slot of a move if the pokemon knows it
	def knowsMove(self, move):
		for i in range(len(self.moveset)):
			if move.getTitle() == self.moveset[i]['move']:
				return i+1
		return False

	# Add new move to the pokemon's moveset
	def learnMove(self, move, slot=None):
		def setMove(m):
			m['move'] = move.getTitle()
			m['pp'] = move.getPp()
			m['max'] = move.getPp()

		if self.knowsMove(move):
			raise UserWarning("@pokemon already knows {}!".format(move))

		if not self.getPokemon().canLearnMove(move):
			raise UserWarning("@pokemon is not able to learn {}!".format(move))

		if slot:
			oldMove = self.moveset[slot-1]['move']
			setMove(self.moveset[slot-1])
			return oldMove
		else:
			for m in range(4):
				if not self.moveset[m]['move']:
					setMove(self.moveset[m])
					return None
		m = "@pokemon wants to learn {} but @pokemon already knows 4 moves! ".format(move)
		m += "To make space for {}, use `!learnmove *move* *1–4*`!".format(move)
		raise UserWarning(m)

	def useMove(self, move):
		for i in range(len(self.moveset)):
			if move.getTitle() == self.moveset[i]['move']:
				self.moveset[i]['pp'] = max(0, self.moveset[i]['pp'] - 1)

	def canUseMove(self, move):
		if not self.knowsMove(move):
			return False
		for i in range(len(self.moveset)):
			if move.getTitle() == self.moveset[i]['move']:
				return self.moveset[i]['pp'] > 0

	#--- Statistics ---#

	def getStatistic(self, name):
		return self.statistics[name]

	def incStatistic(self, name, value):
		self.statistics[name] # Name check
		self.statistics[name] += value
		self.owner.incStatistic(name, value) # Not viable, but 
		return self.statistics[name]
