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


# Create new root database
def createUser():
	return {
		'name': '',
		'balance': 0,
		'cookies': 0,
		'daily': 0,
		'pokemon': '',
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


# Get user's pokemon
def getPokemon(member):
	return loadUser(member)['pokemon']

# Set user's pokemon
def setPokemon(member, pokemon):
	userdata = loadUser(member)
	userdata['pokemon'] = pokemon
	saveUser(member, userdata)
