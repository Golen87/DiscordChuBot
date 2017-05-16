import random
import json
import os.path
import math

from pokedex.tables import *
from pokedex.Move import Move


# Load json database directly
def loadJson(path):
	if os.path.isfile(path):
		with open(path) as f:
			database = json.load(f)
			return database
	raise Exception("Couldn't open database '{}'!".format(path))

pokedexDB = loadJson("pokedex/pokemon.json")
movesDB = loadJson("pokedex/moves.json")
itemsDB = loadJson("pokedex/items.json")


## Pokedex data ##

# Initialize pokemon datablob by setting start vales and randomizing
def initPokemon(pokedata, pokemon):
	rawdata = getPokemonData(pokemon)
	pokedata['pokemon'] = rawdata['name']
	pokedata['title'] = rawdata['title']
	pokedata['status'] = ['']
	pokedata['nature'] = random.choice(list(natures.keys()))
	pokedata['iv'] = {stat: random.randint(0,31) for stat in stats}
	pokedata['ev'] = {stat: 0 for stat in stats}
	pokedata['stage'] = {stat: 0 for stat in stageStats}
	pokedata['moveset'] = [None for m in range(4)]
	pokedata['hp'] = getCurrentStats(pokedata, 'HP')


# Return a unique pokemon name by searching
def findPokemonName(name, rnd=False):
	std = lambda x:x.replace('-',' ').lower()
	name = std(name)

	result = []
	for pokemon in pokedexDB:
		if name == 'random':
			result.append(pokemon)
		if name == std(pokemon["species"]):
			result.append(pokemon)
		if name == std(pokemon["name"]) or name == std(pokemon["title"]):
			return pokemon["name"]
	if not result:
		raise UserWarning("@mention Invalid name. I don't recognize that Pokemon!")

	if rnd:
		return random.choice(result)['name']
	return result[0]["name"]

# Return json data of pokemon by given name
def getPokemonData(name, field=None):
	for pokemon in pokedexDB:
		if name == pokemon['name']:
			if field:
				if field in pokemon:
					return pokemon[field]
				raise UserWarning("@mention Invalid field. '{}' is missing in the database!".format(field))
			return pokemon
	raise UserWarning("@mention Invalid name. I don't recognize that Pokemon!")

def getPokemonName(name):
	return getPokemonData(name, 'title')

def getPokemonStats(name, stat=None):
	base = getPokemonData(name, "stats")
	if stat:
		stat = checkStat(stat)
		return base[stat]
	return base

def getPokemonType(name):
	return getPokemonData(name, "types")


## Move data ##

# Return Move object from fuzzy name
def getMoveByName(name, pokemon=None):
	simplify = lambda x:x.replace('-',' ').lower()
	name = simplify(name)

	if name == 'random' and pokemon:
		pokename = findPokemonName(pokemon)
		movename = random.choice(getPokemonData(pokename)['moves'])
		return getMoveByName(movename)

	for movedata in movesDB:
		if name in [simplify(movedata["name"]), simplify(movedata["title"])]:
			return Move(movedata)
	raise UserWarning("@mention Invalid name. I don't recognize that move!")

# Return whether a pokemon may learn a move
def canLearnMove(pokemon, move):
	moves = getPokemonData(pokemon)['moves']
	if move.getName() in moves:
		return True
	raise UserWarning("@pokemon is not able to learn **{}**!".format(move))

# Return whether a pokemon knows a move
def knowsMove(pokedata, move):
	return move.getTitle() in pokedata['moveset']

# Add new move to the pokemon's moveset
def learnMove(pokedata, move, slot=None):
	if knowsMove(pokedata, move):
		raise UserWarning("**{0}** already knows **{1}**!".format(pokedata['title'], move))

	canLearnMove(pokedata['pokemon'], move)
	if slot:
		oldMove = pokedata['moveset'][slot-1]
		pokedata['moveset'][slot-1] = move.getTitle()
		return oldMove
	else:
		for m in range(4):
			if not pokedata['moveset'][m]:
				pokedata['moveset'][m] = move.getTitle()
				return None
	m = "**{0}** wants to learn **{1}** but **{0}** already knows 4 moves! ".format(pokedata['title'], move)
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
	m = move.getType()
	t1 = types.index(t1)
	m = types.index(m)
	a = effChart[m][t1]
	effectiveness = a
	if len(getPokemonType(name)) == 2:
		t2 = getPokemonType(name)[1]
		t2 = types.index(t2)
		b = effChart[m][t2]
		effectiveness *= b
	if move == "is_confused":
		effectiveness = 1
	return effectiveness

def critMod(move):
	critstage = move.getCritRate() #add item stuff to that as well sometimes later
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
	critchance = critMod(move)
	i = random.randint(1,critchance)
	rand = random.randint(85,100)
	rand = rand/100
	owo = move.getDamageClass() == "physical"
	stab = 1
	burn = 1
	crit = 1
	if getPokemonType(name) == move.getType():
		stab = 1.5
	if ((pokedata1['status'] == 'burn') and owo):
		burn = 0.5
	if 1 <= i <= 25 and move.getName() != 'is_confused':
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

def ailmentAttack(pokedata, move, log):
	ailment = move.getAilment()
	chance = move.getAilmentChance()
	i = random.randint(1, 100)
	if 1 <= i <= chance:
		if ailment in ('burn', 'freeze', 'poison', 'bad-poison', 'sleep', 'paralysis'):
			if pokedata['status'][0] == '':
				pokedata['status'][0] = ailment
				if ailment == 'burn':
					log += ["The target caught on fire!"]
				if ailment == 'freeze':
					log += ["The target froze solid!"]
				if ailment == 'poison':
					log += ["The target got poisoned!"]
				if ailment == 'bad-poison':
					log += ["The target got badly poisoned!"]
				if ailment == 'sleep':
					log += ["The target fell asleep!"]
				if ailment == 'paralysis':
					log += ["@opponent is paralysed! It can't move!"]
		else:
			if ailment not in pokedata['status']:
				pokedata['status'].append(ailment)
				if ailment == 'confusion':
					log += ["The target got confused!"]

def flinchAttack(pokedata, move):
	flinch = move.getFlinchChance()
	i = random.randint(1, 100)
	if 1 <= i <= flinch:
		pokedata['is_flinched'] = True

def stageAttack(pokedata, move, log, attacker=True):
	chance = move.getStatChance()
	i = random.randint(1, 100)
	if 1 <= i <= chance:
		for stat in move.getData()["stat_changes"]:
			stage = move.getData()["stat_changes"][stat]

			raiseStage(pokedata, stage, stat, log, attacker)

def setAilment(pokedata, move, log):
	ailment = move.getAilment()
	type = getPokemonType(pokedata['pokemon'])
	if ailment in ('burn', 'freeze', 'poison', 'bad-poison', 'sleep', 'paralysis'):
		if pokedata['status'][0] == '':
			if ailment == 'burn':
				pokedata['status'][0] = ailment
				log += ["The target caught on fire!"]
			if ailment == 'freeze':
				pokedata['status'][0] = ailment
				log += ["The target froze solid!"]
			if ailment == 'poison' and type not in ['poison', 'steel']:
				pokedata['status'][0] = ailment
				log += ["The target got poisoned!"]
			if ailment == 'poison' and type not in ['poison', 'steel']:
				pokedata['status'][0] = ailment
				log += ["The target got badly poisoned!"]
			if ailment == 'sleep':
				pokedata['status'][0] = ailment
				log += ["The target fell asleep!"]
			if (ailment == 'paralysis') and ('electric' not in type):
				pokedata['status'][0] = ailment
				log += ["The target got paralysed. It's maybe unable to move!"]
			else:
				log += ["The move failed!"]
			return
		else:
			log += ["The move failed!"]
	else:
		if ailment not in pokedata['status']:
			pokedata['status'].append(ailment)
			if ailment == 'confusion':
				log += ["The target got confused!"]

def turnCount(pokedata):
	pokedata['turn_count'][0] = pokedata['turn_count'][0] + 1

def dotDmg(pokedata, log):
	if pokedata['status'][0] == 'poison':
		stats = getCurrentStats(pokedata, 'HP')
		dmg = math.floor(stats/8.0)
		newHp = max(0, pokedata['hp'] - dmg)
		pokedata['hp'] = newHp
		log += ["Your Pokemon got hurt by the poison."]
		log += ['It now has ({}/{}) hp!'.format(newHp, stats)]
		return
	if pokedata['status'][0] == 'burn':
		stats = getCurrentStats(pokedata, 'HP')
		dmg = math.floor(stats/16.0)
		newHp = max(0, pokedata['hp'] - dmg)
		pokedata['hp'] = newHp
		log += ["Your Pokemon got hurt by the burn."]
		log += ['It now has ({}/{}) hp!'.format(newHp, stats)]
		return
	if pokedata['status'][0] == 'bad-poison':
		n = 1.0 + pokedata['turn_count']
		stats = getCurrentStats(pokedata, 'HP')
		dmg = math.floor(n*stats/16.0)
		newHp = max(0, pokedata['hp'] - dmg)
		pokedata['hp'] = newHp
		turnCount(pokedata)
		log += ["Your Pokemon got hurt by the poison."]
		log += ['It now has ({}/{}) hp!'.format(newHp, stats)]
		return

def attack(pokeAtk, pokeDef, log, move, confusion=False):
	if not confusion:
		knowsMove(pokeAtk, move)
	power = move.getPower()
	acc = move.getAccuracy()
	stats1 = getCurrentStats(pokeAtk)
	stats2 = getCurrentStats(pokeDef)
	if not confusion:
		if 'confusion' in pokeAtk["status"]:
			i = random.randint(1,100)
			if (1 <= i <= 25) or (pokeAtk["turn_count"][1] == 4):
				pokeAtk['turn_count'][1] = 0
				pokeAtk['status'].remove('confusion')
				log += "The Pokemon snapped out of its confusion. "
			elif (1 <= i <= 67):
				i = random.randint(1,100)
				pokeAtk['turn_count'][1] += 1
				log += "The Pokemon is confused. "
			else:
				pokeAtk['turn_count'][1] += 1
				log += "The Pokemon is confused. "
				return attack(pokeAtk, pokeAtk, log, move='is_confused', confusion=True)
	if pokeAtk["status"][0] == 'paralysis':
		i = random.randint(1,100)
		if (1 <= i <= 25):
			log += ["The Pokemon is paralyzed and couldn't move!"]
			return
		else:
			pass
	if pokeAtk["status"][0] == 'sleep':
		i = random.randint(1,100)
		if (1 <= i <= 33) ^ (pokeAtk["turn_count"][0] == 3):
			pokeAtk["status"][0] = ''
			pokeAtk["turn_count"][0] = 0
			log += ["The Pokemon woke up!"]
		else:
			turnCount(pokeAtk)
			log += ["The Pokemon is fast asleep."]
			return
	if pokeAtk["status"][0] == 'freeze':
		i = random.randint(1,100)
		if 1 <= i <= 20:
			log += ["The Pokemon thawed out!"]
		else:
			log += ["The Pokemon is frozen solid and couldn't move!"]
			return
	if move not in unique:
		log += ["@pokemon used {}!".format(move)]
		if acc is None:
			acc = 100
		else:
			acc = acc * (stageMod(pokeAtk, 'Accuracy')/stageMod(pokeDef, 'Evasiveness'))
		i = random.randint(1,100)
		a, d = 1, 1
		dclass = move.getDamageClass()
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
				effect = typeAdvantage(pokeDef, move)
				if effect >= 2:
					log += ["It's super effective!"]
				if 0 < effect <= 0.5:
					log += ["It's not very effective..."]
				if effect == 0:
					log += ["It has no effect on @opponent!"]
				newHp = max(0, pokeDef['hp'] - damage)
				pokeDef['hp'] = newHp
				if move == "is_confused" and confusion:
					log += ["It hurt itself in confusion."]
				if damage != 0:
					log += ['@opponent took **{}** damage!'.format(damage)]
				if stats2['HP'] != newHp:
					log += ['It now has ({}/{}) hp!'.format(newHp, stats2['HP'])]
				flinchAttack(pokeDef, move)
				ailmentAttack(pokeDef, move, log)
				if move.getCategory() == 'damage+lower':
					stageAttack(pokeDef, move, log, False)
				if move.getCategory() == 'damage+raise':
					stageAttack(pokeAtk, move, log, True)
				dotDmg(pokeAtk, log)
				return
			else:
				log += ["The move missed!"]
				dotDmg(pokeAtk, log)
				return
		if dclass == "status" and "unique" not in move.getCategory():
			if 1 <= i <= acc:
				setAilment(pokeDef, move, log)
				dotDmg(pokeAtk, log)
				return
			else:
				log += ['The attack missed!']
				dotDmg(pokeAtk, log)
				return

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
		name = pokedata['pokemon']
		nature = pokedata['nature']
		iv = pokedata['iv'][stat]
		ev = pokedata['ev'][stat]
		basic = 60.0 if stat == 'HP' else 5.0
		current = (math.floor(base + iv/2.0 + math.floor(ev/4.0)/2.0) + basic) * natureMod(nature, stat)
		current = math.floor(current)
		if stat == 'Speed':
			if pokedata["status"][0] == 'paralysis':
				current = math.floor(current/2.0)
		if name == 'shedinja' and stat == 'HP':
			current = 1
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

def raiseStage(pokedata, value, stat, log=[], attacker=True):
	def clamp(num):
		newNum = max(-6, min(6, num + value))
		return newNum, newNum - num
	stat = checkStageStat(stat)
	pokedata['stage'][stat], diff = clamp(pokedata['stage'][stat])
	adv = ["", "", " sharply", " drastically"]
	name = '@attacker' if attacker else '@opponent'
	if diff == 0:
		log += [name + " cannot {} its {} any further.".format(["lower", "raise"][value>0], stat)]
	if diff > 0:
		log += [name + "'s {} rose{}!".format(stat, adv[abs(diff)])]
	if diff < 0:
		log += [name + "'s {}{} fell!".format(stat, adv[abs(diff)])]

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
	pokedata['turn_count'] = [0, 0]
