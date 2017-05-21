
# Pokemon types
types = [
	"normal",
	"fighting",
	"flying",
	"poison",
	"ground",
	"rock",
	"bug",
	"ghost",
	"steel",
	"fire",
	"water",
	"grass",
	"electric",
	"psychic",
	"ice",
	"dragon",
	"dark",
	"fairy"
]

# Effective type chart
effChart = [
	#No Fi Fl Po Gr Ro Bu Gh St Fi Wa Gr El Ps Ic Dr Da Fa
	[1, 1, 1, 1, 1,.5, 1, 0,.5, 1, 1, 1, 1, 1, 1, 1, 1, 1], # Normal
	[2, 1,.5,.5, 1, 2,.5, 0, 2, 1, 1, 1, 1,.5, 2, 1, 2,.5], # Fighting
	[1, 2, 1, 1, 1,.5, 2, 1,.5, 1, 1, 2,.5, 1, 1, 1, 1, 1], # Flying
	[1, 1, 1,.5,.5,.5, 1,.5, 0, 1, 1, 2, 1, 1, 1, 1, 1, 2], # Poison
	[1, 1, 0, 2, 1, 2,.5, 1, 2, 2, 1,.5, 2, 1, 1, 1, 1, 1], # Ground
	[1,.5, 2, 1,.5, 1, 2, 1,.5, 2, 1, 1, 1, 1, 2, 1, 1, 1], # Rock
	[1,.5,.5,.5, 1, 1, 1,.5,.5,.5, 1, 2, 1, 2, 1, 1, 2,.5], # Bug
	[0, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1,.5, 1], # Ghost
	[1, 1, 1, 1, 1, 2, 1, 1,.5,.5,.5, 1,.5, 1, 2, 1, 1, 2], # Steel
	[1, 1, 1, 1, 1,.5, 2, 1, 2,.5,.5, 2, 1, 1, 2,.5, 1, 1], # Fire
	[1, 1, 1, 1, 2, 2, 1, 1, 1, 2,.5,.5, 1, 1, 1,.5, 1, 1], # Water
	[1, 1,.5,.5, 2, 2,.5, 1,.5,.5, 2,.5, 1, 1, 1,.5, 1, 1], # Grass
	[1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 2,.5,.5, 1, 1,.5, 1, 1], # Electric
	[1, 2, 1, 2, 1, 1, 1, 1,.5, 1, 1, 1, 1,.5, 1, 1, 0, 1], # Psychic
	[1, 1, 2, 1, 2, 1, 1, 1,.5,.5,.5, 2, 1, 1,.5, 2, 1, 1], # Ice
	[1, 1, 1, 1, 1, 1, 1, 1,.5, 1, 1, 1, 1, 1, 1, 2, 1, 0], # Dragon
	[1,.5, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1,.5,.5], # Dark
	[1, 2, 1,.5, 1, 1, 1, 1,.5,.5, 1, 1, 1, 1, 1, 2, 2, 1], # Fairy
]


#--- Stats ---#

stats = ["Attack", "Defense", "HP", "Sp.Atk", "Sp.Def", "Speed"]

statsAlias = {
	"Attack": ["atk"],
	"Defense": ["def", "defence"],
	"HP": ["health", "hitpoints"],
	"Sp.Atk": ["special atk", "special attack"],
	"Sp.Def": ["special def", "special defence", "special defense"],
	"Speed": ["spd"],
}

# Check if stat is correct
def checkStat(value):
	simplify = lambda x:x.replace('-',' ').replace('.',' ').lower()
	for stat in stats:
		if simplify(value) == simplify(stat):
			return stat
	for stat in statsAlias:
		for spelling in statsAlias[stat]:
			if simplify(value) == simplify(spelling):
				return stat
	raise UserWarning("@mention Invalid stat. Use `!stats` for information on what stats you can train!")


#--- Stages ---#

stageStats = ["Attack", "Defense", "Sp.Atk", "Sp.Def", "Speed", "Accuracy", "Evasion"]

stageStatsAlias = {
	"Attack": ["atk"],
	"Defense": ["def", "defence"],
	"Sp.Atk": ["special atk", "special attack"],
	"Sp.Def": ["special def", "special defence", "special defense"],
	"Speed": ["spd"],
	"Accuracy": ["acc"],
	"Evasion": ["eva", "evasiveness"],
}

# Check if stagestat is correct
def checkStageStat(value):
	simplify = lambda x:x.replace('-',' ').replace('.',' ').lower()
	for stat in stageStats:
		if simplify(value) == simplify(stat):
			return stat
	for stat in stageStatsAlias:
		for spelling in stageStatsAlias[stat]:
			if simplify(value) == simplify(spelling):
				return stat
	raise UserWarning("@mention Invalid stat. Use `!stages` for information on what stages you can train!")


# Pokemon natures
natures = {
	#Nature      Atk  Def   HP  SpA  SpD  Spd
	"Hardy":	[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
	"Lonely":	[1.1, 0.9, 1.0, 1.0, 1.0, 1.0],
	"Brave":	[1.1, 1.0, 1.0, 1.0, 1.0, 0.9],
	"Adamant":	[1.1, 1.0, 1.0, 0.9, 1.0, 1.0],
	"Naughty":	[1.1, 1.0, 1.0, 1.0, 0.9, 1.0],
	"Bold":		[0.9, 1.1, 1.0, 1.0, 1.0, 1.0],
	"Docile":	[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
	"Relaxed":	[1.0, 1.1, 1.0, 1.0, 1.0, 0.9],
	"Impish":	[1.0, 1.1, 1.0, 0.9, 1.0, 1.0],
	"Lax":		[1.0, 1.1, 1.0, 1.0, 0.9, 1.0],
	"Timid":	[0.9, 1.0, 1.0, 1.0, 1.0, 1.1],
	"Hasty":	[1.0, 0.9, 1.0, 1.0, 1.0, 1.1],
	"Serious":	[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
	"Jolly":	[1.0, 1.0, 1.0, 0.9, 1.0, 1.1],
	"Naive":	[1.0, 1.0, 1.0, 1.0, 0.9, 1.1],
	"Modest":	[0.9, 1.0, 1.0, 1.1, 1.0, 1.0],
	"Mild":		[1.0, 0.9, 1.0, 1.1, 1.0, 1.0],
	"Quiet":	[1.0, 1.0, 1.0, 1.1, 1.0, 0.9],
	"Bashful":	[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
	"Rash":		[1.0, 1.0, 1.0, 1.1, 0.9, 1.0],
	"Calm":		[0.9, 1.0, 1.0, 1.0, 1.1, 1.0],
	"Gentle":	[1.0, 0.9, 1.0, 1.0, 1.1, 1.0],
	"Sassy":	[1.0, 1.0, 1.0, 1.0, 1.1, 0.9],
	"Careful":	[1.0, 1.0, 1.0, 0.9, 1.1, 1.0],
	"Quirky":	[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
}


# ?
unique = []


#--- Ailments ---#

ailments = ["burn", "paralysis", "freeze", "sleep", "poison", "bad-poison", "confusion", "embargo", "perish-song", "ingrain", "leech-seed", "unknown", "nightmare", "yawn", "disable", "trap", "no-type-immunity", "torment", "heal-block", "infatuation"]
ailmentsSpecial = ['burn', 'freeze', 'poison', 'bad-poison', 'sleep', 'paralysis']

ailmentImmunities = {
	'burn': ['fire'],
	'freeze': ['ice'],
	'poison': ['poison', 'steel'],
	'bad-poison': ['poison', 'steel'],
	'paralysis': ['electric'],
}

ailmentMessages = {
	"paralysis": {
		"start": "@ is paralyzed! It may be unable to move!",
		"cont": "@ is paralyzed! It can't move!",
	},
	"sleep": {
		"start": "@ fell asleep!",
		"cont": "@ is fast asleep!",
		"end": "@ woke up!",
	},
	"freeze": {
		"start": "@ was frozen solid!",
		"cont": "@ is frozen solid!",
		"end": "@ thawed out!",
	},
	"burn": {
		"start": "@ was burned!",
		"hurt": "@ is hurt by its burn!",
	},
	"poison": {
		"start": "@ was poisoned!",
		"hurt": "@ is hurt by poison!",
	},
	"bad-poison": {
		"start": "@ was badly poisoned!",
		"hurt": "@ is hurt by poison!",
	},
	"confusion": {
		"start": "@ became confused!",
		"cont": "@ is confused!",
		"hurt": "It hurt itself in its confusion!",
		"end": "@ snapped out of its confusion!",
	},
}

def getAilmentMessage(ailment, stage, attacker=True):
	name = '@attacker' if attacker else '@defender'
	message = ailmentMessages[ailment][stage]
	message = message.replace('@', name)
	return message
