import random
import json
import os.path
import math

from pokedex.tables import *


# Load json database directly
def loadJson(path):
	if os.path.isfile(path):
		with open(path) as f:
			database = json.load(f)
			return database
	return {}

pokedexDB = loadJson("pokedex/pokedex.json")
movesDB = loadJson("pokedex/moves.json")
itemsDB = loadJson("pokedex/items.json")


## Pokedex data ##

# Initialize pokemon datablob by setting start vales and randomizing
def initPokemon(pokedata, pokemon):
	pokedata['pokemon'] = getPokemonName(pokemon)
	pokedata['status'] = ['']
	pokedata['nature'] = random.choice(list(natures.keys()))
	pokedata['iv'] = {stat: random.randint(0,31) for stat in stats}
	pokedata['ev'] = {stat: 0 for stat in stats}
	pokedata['stage'] = {stat: 0 for stat in stageStats}
	pokedata['moveset'] = [None for m in range(4)]
	pokedata['hp'] = getCurrentStats(pokedata, 'HP')


# Return json data of pokemon by given name
def getPokemonData(name, field=None):
	name = name.lower()
	for pokemon in pokedexDB:
		if name == pokemon["name"].lower():
			if field:
				if field in pokemon:
					return pokemon[field]
				raise UserWarning("@mention Invalid field. Some data is missing in the database!")
			return pokemon
	raise UserWarning("@mention Invalid name. I don't recognize that Pokemon!")

def getPokemonName(name):
	return getPokemonData(name, "name")


def getPokemonStats(name, stat=None):
	base = getPokemonData(name, "base")
	if stat:
		stat = checkStat(stat)
		return base[stat]
	return base

def getPokemonType(name):
	return getPokemonData(name, "type")


## Move data ##

# Return json data of move by given name
def getMoveData(name, field=None):
	name = name.lower()
	for move in movesDB:
		if name == move["title"].lower():
			if field:
				if field in move:
					return move[field]
				raise UserWarning("@mention Invalid field. '{}' is missing in the database!".format(field))
			return move
	raise UserWarning("@mention Invalid name. I don't recognize that move!")

def getMoveName(name):
	return getMoveData(name, "title")

def getMoveType(name):
	return getMoveData(name, "type")

def getMoveMeta(name):
	return getMoveData(name, "meta")

def getMovePower(name):
	power = getMoveData(name, "power")
	if not power:
		return 0
	return power

def getMoveCategory(name):
	return getMoveData(name, "damage_class")

def getMoveAccuracy(name):
	return getMoveData(name, "accuracy")

# Return whether a pokemon may learn a move
def canLearnMove(pokemon, move):
	moveid = getMoveData(move)['id']
	sets = getPokemonData(pokemon)['skills'].values()
	for moves in sets:
		if moveid in moves:
			return True
	raise UserWarning("**{}** is not able to learn **{}**!".format(getPokemonName(pokemon), move))

# Return whether a pokemon knows a move
def knowsMove(pokedata, move):
	return move in pokedata['moveset']

# Add new move to the pokemon's moveset
def learnMove(pokedata, move, slot=None):
	if knowsMove(pokedata, move):
		raise UserWarning("**{0}** already knows **{1}**!".format(pokedata['pokemon'], move))

	if slot:
		oldMove = pokedata['moveset'][slot-1]
		pokedata['moveset'][slot-1] = move
		return oldMove
	else:
		for m in range(4):
			if not pokedata['moveset'][m]:
				pokedata['moveset'][m] = move
				return None
	m = "**{0}** wants to learn **{1}** but **{0}** already knows 4 moves! ".format(pokedata['pokemon'], move)
	m += "To make space for **{0}**, use `!learnmove *move* *1–4*`!".format(move)
	raise UserWarning(m)


# Return type advantage
def typeChart(atkType, defType):
	if atkType in types and defType in types:
		return effChart[types.index(atkType)][types.index(defType)]
	return None


def typeAdvantage(pokedata, move):
	name = pokedata['pokemon']
	t1 = getPokemonType(name)[0]
	m = getMoveType(move)
	t1 = types.index(t1)
	m = types.index(m)
	a = effChart[m][t1]
	effectiveness = a
	if len(getPokemonType(name)) == 2:
		t2 = getPokemonType(name)[1]
		t2 = types.index(t2)
		b = effChart[m][t2]
		effectiveness *= b
	return effectiveness

def critMod(move):
	meta = getMoveMeta(move)
	critstage = meta['crit_rate']	#add item stuff to that as well sometimes later
	if critstage == 0:
		return 400
	if critstage == 1:
		return 200
	if critstage == 2:
		return 50
	if critstage >= 3:
		return 25

def modifier(pokedata1, pokedata2, move):
	eff = typeAdvantage(pokedata2, move)
	name = pokedata1['pokemon']
	meta = getMoveMeta(move)
	critchance = critMod(move)
	i = random.randint(1,critchance)
	rand = random.randint(85,100)
	rand = rand/100
	owo = getMoveCategory(move) == "physical"
	stab = 1
	burn = 1
	crit = 1
	if getPokemonType(name) == getMoveType(move):
		stab = 1.5
	if ((pokedata1['status'] == 'burn') and owo):
		burn = 0.5
	if 1 <= i <= 25:
		crit = 1.5
	mod = eff * rand * stab * burn * crit
	return mod

def stageMod(pokedata, stat):
	stage = pokedata['stage'][stat]
	s = 1
	if stat not in ('Evasiveness', 'Accuracy'):
		if stage >= 0:
			s = (2.0 + stage)/2.0
			return s
		else:
			s = 2.0/(2.0 - stage)
			return s
	else:
		if stage >= 0:
			s = (3.0 + stage)/3.0
			return s
		else:
			s = 3.0/(3.0 - stage)
			return s

def ailementAttack(pokedata, move):
	meta = getMoveMeta(move)
	ailment = meta['ailment']
	chance = meta['ailment_chance']
	i = random.randint(1, 100)
	if 1 <= i <= chance:
		if ailment in ('burn', 'freeze', 'poison', 'bad-poison', 'sleep', 'paralysis'):
			pokedata['status'][0] = ailment
		else:
			if ailment not in pokedata['status']:
				pokedata['status'].append(ailment)

def flinchAttack(pokedata, move):
	meta = getMoveMeta(move)
	flinch = meta['flinch_chance']
	i = random.randint(1, 100)
	if 1 <= i <= flinch:
		pokedata['is_flinched'] = True

def stageAttack(pokedata, move):
	meta = getMoveMeta(move)
	chance = meta['stat_chance']
	i = random.randint(1, 100)
	if 1 <= i <= chance:
		for stat in getMoveData(move)["stat_changes"]:
			stage = getMoveData(move)["stat_changes"][stat]

			raiseStage(pokedata, stage, stat)

def setAilement(pokedata, move):
	meta = getMoveMeta(move)
	ailment = meta['ailment']
	if ailment in ('burn', 'freeze', 'poison', 'bad-poison', 'sleep', 'paralysis'):
		if pokedata['status'][0] == '':
			pokedata['status'][0] = ailment
		else:
			raise UserWarning("The move failed!")
	else:
		if ailment not in pokedata['status']:
			pokedata['status'].append(ailment)

def turnCount(pokedata):
	pokedata['turn_count'] = pokedata['turn_count'] + 1

def attack(pokeAtk, pokeDef, move):
	knowsMove(pokeAtk, move)
	meta = getMoveMeta(move)
	dclass = getMoveCategory(move)
	power = getMovePower(move)
	acc = getMoveAccuracy(move)
	stats1 = getCurrentStats(pokeAtk)
	stats2 = getCurrentStats(pokeDef)
	if pokeAtk["status"][0] == 'sleep'
		i = random.randint(1,100)
		if (1 <= i <= 33) ^ (pokeAtk["turn_count"] == 3):
			#something something log
		else:
			turnCount(pookeAtk)
			#something something log
			return None
	if move not in unique:
		if acc is None:
			acc = 100
		else:
			acc = acc * (stageMod(pokeAtk, 'Accuracy')/stageMod(pokeDef, 'Evasiveness'))
		i = random.randint(1,100)
		a, d = 1, 1
		if dclass != "status":
			if 1 <= i <= acc:
				if dclass == "physical":
					a = stageMod(pokeAtk, 'Attack') * stats1['Attack']
					d = stageMod(pokeDef, 'Defense') * stats2['Defense']
				elif dclass == "special":
					a = stageMod(pokeAtk, 'Sp.Atk') * stats1['Sp.Atk']
					d = stageMod(pokeDef, 'Sp.Def') * stats1['Sp.Def']
				damage = (((22.0*power*a/d)/50.0)+2.0)*modifier(pokeAtk, pokeDef, move)
				damage = math.floor(damage)

			else:
				raise UserWarning('The attack missed!')

			flinchAttack(pokeDef, move)
			ailementAttack(pokeDef, move)
			if meta['category'] == 'damage+lower':
				stageAttack(pokeDef, move)
			if meta['category'] == 'damage+raise':
				stageAttack(pokeAtk, move)
			return damage
		if dclass == "status" and meta["category"] != "unique":
			if 1 <= i <= acc:
				setAilement(pokeDef, move)
			else:
				raise UserWarning('The attack missed!')

# Return stat(s) modifier for a nature
def natureMod(nature, stat=None):
	if stat:
		return natures[nature][stats.index(stat)]
	else:
		return natures[nature]

# Check if stat is correct
def checkStat(value):
	for stat in stats:
		if value.lower() == stat.lower():
			return stat
	raise UserWarning("@mention Invalid stat. Use `!stats` for information on what stats you can train!")

def checkStageStat(value):
	for stat in stageStats:
		if value.lower() == stat.lower():
			return stat
	raise UserWarning("@mention Invalid stat. Use `!stages` for information on what stages you can train!")

# Return current stat by combining: base, iv, ev, nature
def getCurrentStats(pokedata, stat=None):
	if stat:
		stat = checkStat(stat)
		base = getPokemonStats(pokedata['pokemon'], stat)
		nature = pokedata['nature']
		iv = pokedata['iv'][stat]
		ev = pokedata['ev'][stat]
		basic = 60.0 if stat == 'HP' else 5.0
		current = (base + iv/2.0 + ev/8.0 + basic) * natureMod(nature, stat)
		current = math.floor(current)
		return current
	else:
		return {s: getCurrentStats(pokedata, s) for s in stats}
def getCurrentStages(pokedata, stat=None):
	if stat:
		return pokedata['stage'][stat]
	else:
		return {s: getCurrentStages(pokedata, s) for s in stageStats}

def getTotalEV(pokedata):
	return sum([pokedata['ev'][stat] for stat in stats])

def trainEV(pokedata, value, stat):
	totalRemaining = 510 - getTotalEV(pokedata)
	stat = checkStat(stat)
	if totalRemaining <= 0:
		raise UserWarning("Your @pokemon is already fully trained!")
	if value <= 0:
		raise UserWarning("@mention Invalid value. Please specify a value between (1–252)!")

	remaining = 252 - pokedata['ev'][stat]
	if remaining <= 0:
		raise UserWarning("Your @pokemon has already fully trained its {}-EV!".format(stat))

	inc = min(value, remaining, totalRemaining)
	pokedata['ev'][stat] += inc
	return inc

def resetEV(pokedata, stat=None):
	if stat:
		stat = checkStat(stat)
		pokedata['ev'][stat] = 0
	else:
		pokedata['ev'] = {stat: 0 for stat in stats}

def maxIV(pokedata, stat=None):
	if stat:
		stat = checkStat(stat)
		pokedata['iv'][stat] = 31
	else:
		pokedata['iv'] = {stat: 31 for stat in stats}

def raiseStage(pokedata, stage, stat=None):
	def clamp(value):
		return max(-6, min(6, value))
	if stat:
		stat = checkStageStat(stat)
		pokedata['stage'][stat] = clamp(pokedata['stage'][stat] + stage)
	else:
		pokedata['stage'] = {stat: clamp(pokedata['stage'][stat] + stage) for stat in stageStats}

def resetStage(pokedata, stat=None):
	if stat:
		stat = checkStageStat(stat)
		pokedata['stage'][stat] = 0
	else:
		pokedata['stage'] = {stat: 0 for stat in stageStats}


# Fully restore a pokemon
def restorePokemon(pokedata):
	pokedata['hp'] = getCurrentStats(pokedata, 'HP')
	resetStage(pokedata)
	pokedata["status"] = ['']
