import json
import os.path

DBPath = 'database.json'

# Repair missing keys in data
def repair(data, template):
	for key in template:
		if key not in data:
			data[key] = template[key]


# Create new root database
def createDatabase():
	return {
		'users': {},
	}

# Save dictionary to json database
def saveDatabase(database):
	with open('database.json', 'w') as f:
		json.dump(database, f)

# Load dictionary from json database
def loadDatabase():
	if os.path.isfile(DBPath):
		with open(DBPath) as f:
			database = json.load(f)
			repair(database, createDatabase())
			return database
	return createDatabase()


# Create new userdata blob. This contains everything related to one user.
def createUser():
	return {
		'name': '',
		'balance': 0,
		'cookies': 0,
		'daily': 0,
		'pokemon': None,
		'hp': 0,
	}

# Save user to database
def saveUser(member, userdata):
	database = loadDatabase()
	database['users'][member.id] = userdata
	saveDatabase(database)

# Load user from database
def loadUser(member):
	database = loadDatabase()
	if member.id in database['users']:
		repair(database['users'][member.id], createUser())
		return database['users'][member.id]
	user = createUser()
	user['name'] = member.name
	return user

# Load user from database
def loadAllUsers():
	database = loadDatabase()
	allUsers = []
	for id in database['users']:
		repair(database['users'][id], createUser())
		allUsers.append(database['users'][id])
	return allUsers


# Get user's balance
def getBalance(member):
	return loadUser(member)['balance']

# Set user's balance
def setBalance(member, balance):
	userdata = loadUser(member)
	userdata['balance'] = balance
	saveUser(member, userdata)

# Set user's balance relative
def incBalance(member, balance):
	setBalance(member, getBalance(member) + balance)


# Get user's cookies
def getCookies(member):
	return loadUser(member)['cookies']

# Set user's cookies
def setCookies(member, cookies):
	userdata = loadUser(member)
	userdata['cookies'] = cookies
	saveUser(member, userdata)

# Set user's cookies relative
def incCookies(member, cookies):
	setCookies(member, getCookies(member) + cookies)


# Get user's 'daily' timestamp
def getDailyTimestamp(member):
	return loadUser(member)['daily']

# Set user's 'daily' timestamp
def setDailyTimestamp(member, timestamp):
	userdata = loadUser(member)
	userdata['daily'] = timestamp
	saveUser(member, userdata)


# Load top list of balance
def getTopList():
	scoreMap = []
	for user in loadAllUsers():
		scoreMap.append((user['name'], user['balance']))
	scoreMap.sort(key=lambda x:x[1], reverse=True)
	return scoreMap



# Create new pokemondata blob
def createPokemon():
	return {
		'pokemon': '',
		'status': '',
		'hp': 0,
		'nature': '',
		'iv': {}, # Set by pokedexManager
		'ev': {},
		'stage': {},
		'moveset': [],
		'setpoke-timestamp': 0,
		'attack-timestamp': 0,
		'learn-timestamp': 0,
	}

# Save pokemon to database
def savePokemon(member, pokedata):
	userdata = loadUser(member)
	userdata['pokemon'] = pokedata
	saveUser(member, userdata)

# Load pokemon from database
def loadPokemon(member):
	userdata = loadUser(member)
	if userdata['pokemon']:
		repair(userdata['pokemon'], createUser())
	return userdata['pokemon']


# Get user's pokemon's name
def getPokemonValue(member, key):
	pokedata = loadPokemon(member)
	if pokedata:
		if key in pokedata:
			return pokedata[key]
	return None

# Get user's pokemon's name
def getPokemonName(member):
	return getPokemonValue(member, 'pokemon')

# Get user's pokemon's health
def getPokemonHp(member):
	return getPokemonValue(member, 'hp')

# Get user's pokemon's status
def getPokemonStatus(member):
	return getPokemonValue(member, 'status')

# Get user's pokemon's status
def getPokemonMoveset(member):
	return getPokemonValue(member, 'moveset')


# Set user's pokemon's health
def setPokemonHp(member, hp):
	pokemon = loadPokemon(member)
	if pokemon:
		pokemon['hp'] = hp
		savePokemon(member, pokemon)
