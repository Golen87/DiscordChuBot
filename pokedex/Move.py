import random, math


#--- Class Move ---#
class Move:

	# Initialize Move
	# @param data: imported dictionary from json database
	def __init__(self, data):
		self._data = data

	# Debug printing
	def __repr__(self):
		return '**{}**'.format(self.getTitle())


	#--- Identification ---#

	def getId(self):
		return self._data['id']

	def getName(self):
		return self._data['name']


	#--- Text ---#

	def getTitle(self):
		return self._data['title']

	def getFlavorText(self):
		return self._data['flavor_text']

	def getEffect(self):
		return self._data['effect']

	def getEffectShort(self):
		return self._data['effect_short']

	def getEffectChance(self):
		return self._data['effect_chance']


	#--- Basic ---#

	def getType(self):
		return self._data["type"]

	# ["status", "special", "physical"]
	def getDamageClass(self):
		return self._data["damage_class"]

	# "damage+raise", "damage+lower", "damage+ailment", "damage+heal"
	# "ailment", "ohko", , "heal", "damage", "field-effect", "net-good-stats", "swagger", "force-switch", "unique", "whole-field-effect"
	def getCategory(self):
		return self._data['meta']['category']

	def getPp(self):
		return self._data['pp']

	# 0 - 100 (%)
	def getAccuracy(self):
		return self._data["accuracy"]

	def getPower(self):
		return self._data['power']

	# -7 to 5
	def getPriority(self):
		return self._data['priority']

	# "user", "ally", "user-or-ally", "user-and-allies", "all-opponents", "all-other-pokemon", "all-pokemon"
	# "selected-pokemon", "selected-pokemon-me-first", "random-opponent", "specific-move"
	# "users-field", "opponents-field", "entire-field"
	def getTarget(self):
		return self._data['target']

	# [0, 1, 6]
	def getCritRate(self):
		return self._data['meta']['crit_rate']


	#--- Buffs and debuffs ---#

	# 0 - 100 (%)
	def getStatChance(self):
		return self._data['meta']['stat_chance']

	def getStatChanges(self):
		return self._data['stat_changes']

	# 0 - 100 (%)
	def getAilmentChance(self):
		return self._data['meta']['ailment_chance']

	# [None,
	#  "burn", "paralysis", "freeze", "sleep", "poison", "bad-poison",
	#  "confusion", "embargo", "perish-song", "ingrain", "leech-seed", "unknown", "nightmare", "yawn", "disable", "trap", "no-type-immunity", "torment", "heal-block", "infatuation"]
	def getAilment(self):
		ailment = self._data['meta']['ailment']
		if ailment == "none":
			return None
		return ailment

	# 0 - 100 (%)
	def getFlinchChance(self):
		return self._data['meta']['flinch_chance']


	#--- Health ---#

	# [-25, 0, 25, 50]
	def getHealing(self):
		return self._data['meta']['healing']

	# If drain > 0, steal from opponent. This means the move has "heal"
	# If drain < 0, apply recoil damage.
	# [-50, -33, -25, 0, 50, 75]
	def getDrain(self):
		return self._data['meta']['drain']


	#--- Repeating move ---#

	# [None, [2-6, 2-6]]
	def getHits(self):
		hits = [self._data['meta']['min_hits'], self._data['meta']['max_hits']]
		if None in hits:
			return None
		return hits

	# [None, [2-15, 2-15]]
	def getTurns(self):
		turns = [self._data['meta']['min_turns'], self._data['meta']['max_turns']]
		if None in turns:
			return None
		return turns
