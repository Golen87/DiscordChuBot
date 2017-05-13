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
	pokedata['status'] = ''
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
		if name == move["name"].lower():
			if field:
				if field in move:
					return move[field]
				raise UserWarning("@mention Invalid field. Some data is missing in the database!")
			return move
	raise UserWarning("@mention Invalid name. I don't recognize that move!")

def getMoveName(name):
	return getMoveData(name, "name")

def getMoveType(name):
	return getMoveData(name, "type")

def getMovePower(name):
	power = getMoveData(name, "power")
	if not power:
		return 0
	return power

def getMoveCategory(name):
	return getMoveData(name, "category")

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

# Add new move to the 
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
	
def modifier(pokedata1, pokedata2, move):
	eff = typeAdvantage(pokedata2, move)
	name = pokedata1['pokemon']
	i = random.randint(1,400)
	rand = random.randint(85,100)
	rand = rand/100
	owo = getMoveCategory(move) == "physical"
	stab = 1
	burn = 1
	crit =1
	if getPokemonType(name) == getMoveType(move):
		stab = 1.5
	if ((pokedata1['status'] == 'burn') and owo):
		burn = 0.5
	if i <= i <= 25:
		crit = 1.5
	mod = eff * rand * stab * burn * crit
	return mod

def stageMod(pokedata, stat):
	stage = pokedata['stage'][stat]
	s = 1
	if stat not in ('Evasiveness', 'Accuracy'):
		if stage <= 0:
			s = (2.0 + stage)/2.0
			return s
		else:
			s = 2.0/(2.0 + stage)
			return s
	else:
		if stage <= 0:
			s = (3.0 + stage)/3.0
			return s
		else:
			s = 3.0/(3.0 + stage)
			return s

def attack(pokeAtk, pokeDef, move):
	knowsMove(pokeAtk, move)
	power = getMovePower(move)
	acc = getMoveAccuracy(move) # Crash if null accuracy
	stats1 = getCurrentStats(pokeAtk)
	stats2 = getCurrentStats(pokeDef)
	acc = acc * (stageMod(pokeAtk, 'Accuracy')/stageMod(pokeDef, 'Evasiveness'))
	i = random.randint(1,100)
	a, d = 1, 1
	if 1 <= i <= acc:
		if getMoveCategory(move) == "physical":
			a = stageMod(pokeAtk, 'Attack') * stats1['Attack']
			d = stageMod(pokeDef, 'Defense') * stats2['Defense']
		elif getMoveCategory(move) == "special":
			a = stageMod(pokeAtk, 'Sp.Atk') * stats1['Sp.Atk']
			d = stageMod(pokeDef, 'Sp.Def') * stats1['Sp.Def']
		damage = (((22.0*power*a/d)/50.0)+2.0)*modifier(pokeAtk, pokeDef, move)
		damage = math.floor(damage)
		if getMoveCategory(move) == "status":
			damage = 0
	else:
		raise UserWarning('The attack missed!')
	return damage

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


def getTotalEV(pokedata):
	return sum([pokedata['ev'][stat] for stat in stats])

def trainEV(pokedata, value, stat):
	totalRemaining = 510 - getTotalEV(pokedata)
	stat = checkStat(stat)
	if totalRemaining <= 0:
		raise UserWarning("**{}** is already fully trained!".format(pokedata['pokemon']))
	if value <= 0:
		raise UserWarning("@mention Invalid value. Please specify a value between (1–252)!")

	remaining = 252 - pokedata['ev'][stat]
	if remaining <= 0:
		raise UserWarning("**{}** has already fully trained its {}-EV!".format(pokedata['pokemon'], stat))

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
