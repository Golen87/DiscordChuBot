import random
import json
import os.path
import math

from pokedex.tables import *
from pokedex.Move import Move
from pokedex.Pokemon import Pokemon


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


## Return Pokemon object from fuzzy name
# @param name: Pokemon name written by user
# @param rnd: Whether to pick randomly in case of multiple results
def getPokemonByName(name, rnd=False):
	simplify = lambda x:x.replace('-',' ').lower()
	name = simplify(name)

	result = []
	for pokemon in pokedexDB:
		if name == 'random':
			result.append(pokemon)
		if name == simplify(pokemon["species"]):
			result.append(pokemon)
		if name == simplify(pokemon["name"]) or name == simplify(pokemon["title"]):
			return Pokemon(pokemon)
	if not result:
		raise UserWarning("@mention Invalid name. I don't recognize that Pokemon!")

	if rnd:
		return Pokemon(random.choice(result))
	return Pokemon(result[0])

## Return Move object from fuzzy name
# @param name: Move name written by user
# @param pokemon: What pokemon to pick random move from
def getMoveByName(name, pokeObj=None):
	simplify = lambda x:x.replace('-',' ').lower()
	name = simplify(name)

	if name == 'random' and pokeObj:
		movename = random.choice(pokeObj.getMoves())
		return getMoveByName(movename)

	for movedata in movesDB:
		if name in [simplify(movedata["name"]), simplify(movedata["title"])]:
			return Move(movedata)
	raise UserWarning("@mention Invalid name. I don't recognize that move!")


# User exception used in Attack. Ends attack prematurely to print logs and save data.
class EndAttack(Exception):
	pass


# Return whether a 1-100 percentage check succeeds
def chanceTest(percent):
	r = random.randint(1,100)
	return r <= percent


# Return type advantage
def typeChart(atkType, defType):
	if atkType in types and defType in types:
		return effChart[types.index(atkType)][types.index(defType)]
	return None


def typeAdvantage(pokedata, move):
	# No, yuck
	if move == "is_confused":
		return 1
	pokemon = pokedata.getPokemon()
	eff = 1
	for pokeType in pokemon.getTypes():
		p = types.index(pokeType)
		m = types.index(move.getType())
		eff *= effChart[m][p]
	return eff

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

def modifier(pokeAtk, pokeDef, move):
	eff = typeAdvantage(pokeDef, move)
	rand = random.randint(85,100) / 100.0
	stab = 1
	if move.getType() in pokeAtk.getPokemon().getTypes():
		stab = 1.5
	burn = 1
	if pokeAtk.hasStatus('burn') and move.getDamageClass() == "physical":
		burn = 0.5
	crit = 1
	i = random.randint(1,critMod(move))
	if 1 <= i <= 25 and move.getName() != 'is_confused':
		crit = 1.5
	return eff * rand * stab * burn * crit

def ailmentAttack(pokedata, move, log):
	ailment = move.getAilment()
	if chanceTest(move.getAilmentChance()):
		if pokedata.addStatus(ailment):
			log += [getAilmentMessage(ailment, 'start', False)]

def flinchAttack(pokedata, move):
	if chanceTest(move.getFlinchChance()):
		pokedata.setFlinched()

def stageAttack(pokedata, move, log, attacker=True):
	if chanceTest(move.getStatChance()):
		for stat in move.getStatChanges():
			stage = move.getStatChanges()[stat]
			raiseStage(pokedata, stage, stat, log, attacker)

# Inflict ailment on pokemon, unless they're immune or already have it
def setAilment(pokeDef, move, log):
	ailment = move.getAilment()
	if not ailment:
		return

	print("YES", ailment)
	if ailment in ailmentImmunities:
		for type in pokeDef.getPokemon().getTypes():
			if type in ailmentImmunities[ailment]:
				log += ["The move failed!"]
				return
	if pokeDef.addStatus(ailment):
		pokeDef.startTurnCount(ailment)
		log += [getAilmentMessage(ailment, 'start', False)]
	else:
		log += ["The move failed!"]

# Damage Over Time from ailments
def dotDmg(pokedata, log, weather):
	maxHP = pokedata.getStat('HP')

	if pokedata.hasStatus('poison'):
		damage = maxHP // 8
		pokedata.damage(damage)
		log += [getAilmentMessage('poison', 'hurt')]
		showHP(pokedata, log)

	if pokedata.hasStatus('burn'):
		damage = maxHP // 16
		pokedata.damage(damage)
		log += [getAilmentMessage('burn', 'hurt')]
		showHp(pokedata, log)

	if pokedata.hasStatus('bad-poison'):
		turn = 1 + pokedata.getTurnCount('bad-poison')
		damage = turn * maxHP // 16
		pokedata.damage(damage)
		log += [getAilmentMessage('bad-poison', 'hurt')]
		showHp(pokedata, log)

	if not weather['current']:
		return

	# Skip weather below if immune to weather
	if weather['current'] in weatherImmunities:
		for type in pokedata.getPokemon().getTypes():
			if type in weatherImmunities[weather['current']]:
				return

	if 'hurt' in weatherMessages[weather['current']]:
		damage = maxHP // 16
		pokedata.damage(damage)
		log += [getWeatherMessage(weather['current'], 'hurt')]
		showHp(pokedata, log)

def preAilmentCheck(pokedata, log):
	if pokedata.toggleFlinch():
		raise EndAttack("@attacker flinched and couldn't move.")

	ailment = 'confusion'
	if pokedata.hasStatus(ailment):
		i = random.randint(1,100)
		if i <= 25 or pokedata.getTurnCount(ailment) == 4:
			pokedata.clearStatus(ailment)
			pokedata.clearTurnCount('ailment')
			log += [getAilmentMessage(ailment, 'end')]
		elif i <= 67:
			log += [getAilmentMessage(ailment, 'cont')]
		else:
			log += [getAilmentMessage(ailment, 'cont')]
			# No thanks
			move = getMoveByName('is_confused')
			return attack(pokedata, pokedata, log, move)

	ailment = 'paralysis'
	if pokedata.hasStatus(ailment):
		if chanceTest(25):
			raise EndAttack(getAilmentMessage(ailment, 'cont'))

	ailment = 'sleep'
	if pokedata.hasStatus(ailment):
		if chanceTest(33) or pokedata.getTurnCount('ailment') == 3:
			pokedata.clearStatus('sleep')
			pokedata.clearTurnCount('ailment')
			log += [getAilmentMessage(ailment, 'end')]
		else:
			raise EndAttack(getAilmentMessage(ailment, 'cont'))

	ailment = 'freeze'
	if pokedata.hasStatus(ailment):
		if chanceTest(20):
			pokedata.clearStatus(ailment)
			pokedata.clearTurnCount('ailment')
			log += [getAilmentMessage(ailment, 'end')]
		else:
			raise EndAttack(getAilmentMessage(ailment, 'cont'))

def attack(pokeAtk, pokeDef, log, move, weather):
	a, d = 1, 1
	pokeAtk.incTurnCount()
	#if not confusion:
	preAilmentCheck(pokeAtk, log)

	power = move.getPower()
	acc = move.getAccuracy()

	#if move not in unique:
	log += ["@attacker used {}!".format(move)]
	pokeAtk.useMove(move)

	if acc is None:
		acc = 100
	if move.getCategory() == 'ohko':
		acc = 30
	else:
		acc = acc * (pokeAtk.stageMod('Accuracy') / pokeDef.stageMod('Evasion'))

	dclass = move.getDamageClass()

	target = move.getTarget()
	if target != "user":
		if dclass != "status":
			if chanceTest(acc):
				if dclass == "physical":
					a = pokeAtk.stageMod('Attack') * pokeAtk.getStat('Attack')
					d = pokeDef.stageMod('Defense') * pokeDef.getStat('Defense')
				elif dclass == "special":
					a = pokeAtk.stageMod('Sp.Atk') * pokeAtk.getStat('Sp.Atk')
					d = pokeDef.stageMod('Sp.Def') * pokeDef.getStat('Sp.Def')
				if move.getCategory() == 'ohko':
					power = 1
				damage = (((22.0*power*a/d)/50.0)+2.0)*modifier(pokeAtk, pokeDef, move)
				damage = math.floor(damage)
				if move.getCategory() == 'ohko':
					damage = pokeDef.getStat('HP')
					log += ["A OHKO-move."]
				effect = typeAdvantage(pokeDef, move)
				if effect >= 2:
					log += ["It's super effective!"]
				if 0 < effect <= 0.5:
					log += ["It's not very effective..."]
				if effect == 0:
					log += ["It has no effect on @defender!"]
				newHp = pokeDef.damage(damage)
				if move == "is_confused":# and confusion:
					log += ["It hurt itself in confusion."]
				if damage != 0:
					log += ['@defender took **{}** damage!'.format(damage)]
				if pokeDef.getStat('HP') != newHp:
					showHp(pokeDef, log)
				flinchAttack(pokeDef, move)
				ailmentAttack(pokeDef, move, log)
				if move.getCategory() == 'damage+lower':
					stageAttack(pokeDef, move, log, False)
				if move.getCategory() == 'damage+raise':
					stageAttack(pokeAtk, move, log, True)
				if move.getDrain() > 0:
					healing = math.floor(damage * move.getDrain()/100.0)
					newhp = pokeAtk.heal(healing)
					log += ["@attacker drained {} of @defender's hp.".format(healing)]
					showHp(pokeAtk, log)
				if move.getDrain() < 0:
					healing = math.floor(damage * move.getDrain()/100.0)
					newhp = pokeAtk.heal(healing)
					log += ["@attacker got damaged by the recoil ({}).".format(healing)]
					showHp(pokeAtk, log)
			else:
				log += ["The move missed!"]
		elif dclass == "status" and "unique" not in move.getCategory():
			if chanceTest(acc):
				if move.getCategory() == "ailment":
					setAilment(pokeDef, move, log)

				elif move.getCategory() == "net-good-stats":
					for stat in move.getStatChanges():
						stage = move.getStatChanges()[stat]
						raiseStage(pokeDef, stage, stat, log, False)

				elif move.getCategory() == "whole-field-effect":
					if move.getName() in weatherMessages:
						weather['current'] = move.getName()
						weather['new'] = move.getName()
						log += [getWeatherMessage(move.getName(), 'start')]
			else:
				log += ['The attack missed!']
	else:
		if move.getCategory() == "net-good-stats":
			for stat in move.getStatChanges():
				stage = move.getStatChanges()[stat]
				raiseStage(pokeAtk, stage, stat, log)
		if move.getCategory() == 'heal':
			mod = 1
			if move.getName() in ['morning-sun', 'synthesis', 'moonlight']:
				pass
				if weather['current'] == 'sunny-day':
					mod = 4/3
				elif weather['current']:
					mod = 1/2
			healing = math.floor(mod * pokeAtk.getStat('HP') * move.getHealing()/100.0)
			newhp = pokeAtk.heal(healing)
			log += ["@attacker healed itself by {} hp.".format(healing)]
			showHp(pokeAtk, log)

	dotDmg(pokeAtk, log, weather)


def raiseStage(pokedata, value, stat, log=[], attacker=True):
	stat = checkStageStat(stat)
	diff = pokedata.raiseStage(stat, value)
	name = '@attacker' if attacker else '@defender'
	adv = [" sharply", " drastically"][abs(diff)-2] if 2 <= abs(diff) <= 3 else ""

	if diff == 0:
		log += [name + " cannot {} its {} any further.".format(["lower", "raise"][value>0], stat)]
	if diff > 0:
		log += [name + "'s {} rose{}!".format(stat, adv)]
	if diff < 0:
		log += [name + "'s {}{} fell!".format(stat, adv)]

def resetStage(pokedata, stat=None):
	if stat:
		stat = checkStageStat(stat)
		pokedata['stage'][stat] = 0
	else:
		pokedata['stage'] = {stat: 0 for stat in stageStats}

def showHp(pokedata, log):
	hp = pokedata.getHp()
	maxHp = pokedata.getStat('HP')
	for message in log:
		if message.startswith('It now has ('):
			log.remove(message)
	log += ['It now has ({}/{}) hp!'.format(hp, maxHp)]


def getAttackCooldown(pokedata):
	mod = pokedata.stageMod('Speed')
	speed = pokedata.getStat('Speed')
	time = 30.0 - speed*mod/51.0
	return time

def stopWeather(weather):
	return getWeatherMessage(weather, 'end')
