
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

# All stats
stats = ["Attack", "Defense", "HP", "Sp.Atk", "Sp.Def", "Speed"]

# All stage stats
stageStats = ["Attack", "Defense", "Sp.Atk", "Sp.Def", "Speed", "Accuracy", "Evasiveness"]

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

#
unique = []

ailments = ['burn', 'freeze', 'poison', 'bad-poison', 'sleep', 'paralysis']
"confusion"

# Ailment
ailmentMessages = {
	"paralysis": [
		["@opponent is paralyzed! It may be unable to move!"],
		["@opponent is paralyzed! It can't move!"],
	],
	"sleep": [
		["@opponent fell asleep!"],
		["@opponent is fast asleep!"],
		["@opponent woke up!"],
	],
	"freeze": [
		["@opponent was frozen solid!"],
		["@opponent is frozen solid!"],
		["@opponent thawed out!"],
	],
	"burn": [
		["@opponent was burned!"],
		["@opponent is hurt by its burn!"],
	],
	"poison": [
		["@opponent was poisoned!"],
		["@opponent is hurt by poison!"],
	],
	"bad-poison": [
		["@opponent was badly poisoned!"],
		["@opponent is hurt by poison!"],
	],
	"confusion": [
		["@opponent became confused!"],
		["@opponent is confused!", "It hurt itself in its confusion!"],
		["@opponent is confused!", "@opponent snapped out of its confusion!"],
	],
}
