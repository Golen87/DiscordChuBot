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
		'timestamps': {
			'learn': 0,
			'setpoke': 0,
			'attack': 0,
		},
		'pokemon': None,
		'caps': 0,
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

# Get user's caps
def getCaps(member):
	return loadUser(member)['caps']

# Increase user's caps relative
def incCaps(member, caps=1):
	userdata = loadUser(member)
	userdata['caps'] += caps
	saveUser(member, userdata)


# Get user's 'daily' timestamp
def getDailyTimestamp(member):
	return loadUser(member)['daily']

# Set user's 'daily' timestamp
def setDailyTimestamp(member, timestamp):
	userdata = loadUser(member)
	userdata['daily'] = timestamp
	saveUser(member, userdata)

# Get user's timestamp of a given name
def getTimestamp(member, stamp):
	userdata = loadUser(member)
	if stamp not in userdata['timestamps']:
		raise Exception("'{}' is not a timestamp.".format(stamp))
	return userdata['timestamps'][stamp]

# Set user's timestamp of a given name
def setTimestamp(member, stamp, time):
	userdata = loadUser(member)
	if stamp not in userdata['timestamps']:
		raise Exception("'{}' is not a timestamp.".format(stamp))
	userdata['timestamps'][stamp] = time
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
		'title': '',
		'status': [''],
		'is_flinched': False,
		'turn_count': [0, 0],
		'hp': 0,
		'nature': '',
		'iv': {}, # Set by pokedexManager
		'ev': {},
		'stage': {},
		'moveset': [],
		'weather': '',
		'item': '',
		'battles_won': 0,
		'battles_lost': 0,
	}

# Save pokemon to database
def savePokemon(member, pokedata):
	userdata = loadUser(member)
	userdata['pokemon'] = pokedata
	saveUser(member, userdata)

# Load pokemon from database
def loadPokemon(member, isMe=True):
	userdata = loadUser(member)
	if userdata['pokemon']:
		repair(userdata['pokemon'], createUser())
		return userdata['pokemon']
	if isMe:
		raise UserWarning("You don't have a Pokemon yet. Use `!setpoke` to get started!")
	else:
		m = "{} doesn't have a Pokemon yet. ".format(member.mention)
		m += "Encourage them to use `!setpoke` to get started!"
		raise UserWarning(m)


# Get user's pokemon's name
def getPokemonValue(member, key, isMe=True):
	pokedata = loadPokemon(member, isMe)
	if pokedata:
		if key in pokedata:
			return pokedata[key]
	return None

# Get user's pokemon's name
def getPokemonName(member, isMe=True):
	return getPokemonValue(member, 'title', isMe)

# Get user's pokemon's health
def getPokemonHp(member, isMe=True):
	return getPokemonValue(member, 'hp', isMe)

# Get user's pokemon's status
def getPokemonStatus(member, isMe=True):
	return getPokemonValue(member, 'status', isMe)

# Get user's pokemon's status
def getPokemonMoveset(member, isMe=True):
	return getPokemonValue(member, 'moveset', isMe)


# Set user's pokemon's health
def setPokemonHp(member, hp, isMe=True):
	pokedata = loadPokemon(member, isMe)
	pokedata['hp'] = hp
	savePokemon(member, pokedata)
	return pokedata['hp']

def setWeather(member, weather, isMe=True):
	pokedata = loadPokemon(member, isMe)
	pokedata['hp'] = weather
	savePokemon(member, pokedata)
	return

# Return whether a pokemon flinched. Happens only one turn
def togglePokemonFlinch(member, isMe=True):
	pokedata = loadPokemon(member, isMe)
	flinch = pokedata['is_flinched']
	pokedata['is_flinched'] = False
	savePokemon(member, pokedata)
	return flinch

# Add one win to the user
def incPokemonBattlesWon(member, isMe=True):
	pokedata = loadPokemon(member, isMe)
	pokedata['battles_won'] += 1
	savePokemon(member, pokedata)
	return pokedata['battles_won']

# Add one lost to the user
def incPokemonBattlesLost(member, isMe=True):
	pokedata = loadPokemon(member, isMe)
	pokedata['battles_lost'] += 1
	savePokemon(member, pokedata)
	return pokedata['battles_lost']

# Add one lost to the user
def getPokemonBattleStats(member, isMe=True):
	pokedata = loadPokemon(member, isMe)
	return pokedata['battles_won'], pokedata['battles_lost']
