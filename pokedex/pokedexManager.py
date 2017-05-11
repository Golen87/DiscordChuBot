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
	for stat in stats:
		pokedata['iv'][stat] = random.randint(0,31)
		pokedata['ev'][stat] = 0
	for stat in stageStats:
		pokedata['stage'][stat] = 0
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
				return None
			return pokemon
	return None

def getPokemonName(name):
	return getPokemonData(name, "name")


def getPokemonStats(name, stat=None):
	base = getPokemonData(name, "base")
	if stat:
		if stat in base:
			return base[stat]
		return None
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
				return None
			return move
	return None

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
	return False

# Return whether a pokemon knows a move
def knowsMove(pokedata, move):
	return move in pokedata['moveset']

# Add new move to the 
def learnMove(pokedata, move, slot=None):
	if slot:
		oldMove = pokedata['moveset'][slot-1]
		pokedata['moveset'][slot-1] = move
		return oldMove
	else:
		for m in range(4):
			if not pokedata['moveset'][m]:
				pokedata['moveset'][m] = move
				return None
	return False


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
    rand = rand/100.0
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

def attack(poke1, poke2, move):
    power = getMovePower(move)
    acc = getMoveAccuracy(move)
    stats1 = getCurrentStats(poke1)
    stats2 = getCurrentStats(poke2)
    acc = acc * (stageMod(poke1, 'Accuracy')/stageMod(poke2, 'Evasiveness'))
    i = random.randint(1,100)
    a, d = 1, 1
    if 1 <= i <= acc:
        if getMoveCategory(move) == "physical":
            a = stageMod(poke1, 'Attack') * stats1['Attack']
            d = stageMod(poke2, 'Defense') * stats2['Defense']
        elif getMoveCategory(move) == "special":
            a = stageMod(poke1, 'Sp.Atk') * stats1['Sp.Atk']
            d = stageMod(poke2, 'Sp.Def') * stats1['Sp.Def']
        damage = (((22.0*power*a/d)/50.0)+2.0)*modifier(poke1, poke2, move)
        damage = math.floor(damage)
        if getMoveCategory(move) == "status":
            damage = 0
    else: 
        damage = -1
    return damage

# Return stat(s) modifier for a nature
def natureMod(nature, stat=None):
	if stat:
		return natures[nature][stats.index(stat)]
	else:
		return natures[nature]

# Return current stat by combining: base, iv, ev, nature
def getCurrentStats(pokedata, stat=None):
	if stat:
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
