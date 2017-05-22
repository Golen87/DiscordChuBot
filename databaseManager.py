import json
import os.path

from User import User
from Channel import Channel

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
		'channels': {},
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
			if type(database) != dict:
				database = {}
			repair(database, createDatabase())
			return database
	return createDatabase()


#--- Users ---#

# Save user to database
def saveUser(userObj):
	database = loadDatabase()
	database['users'][userObj.getId()] = userObj.serialize()
	saveDatabase(database)

# Load user from database
def loadUser(member):
	database = loadDatabase()
	userObj = User(member.id, member.name)
	if member.id in database['users']:
		userObj.deserialize(database['users'][member.id])
	return userObj

# Load user from database
def loadAllUsers():
	database = loadDatabase()
	allUsers = []
	for id in database['users']:
		userObj = User(id)
		userObj.deserialize(database['users'][id])
		allUsers.append(userObj)
	return allUsers


# Load top list of balance
def getTopList():
	scoreMap = []
	for user in loadAllUsers():
		scoreMap.append((user.getName(), user.getBalance()))
	scoreMap.sort(key=lambda x:x[1], reverse=True)
	return scoreMap


#--- Channels ---#

# Save channel to database
def saveChannel(channelObj):
	database = loadDatabase()
	database['channels'][channelObj.getId()] = channelObj.serialize()
	saveDatabase(database)

# Load channel from database
def loadChannel(channel):
	database = loadDatabase()
	channelObj = Channel(channel.id, channel.name)
	if channel.id in database['channels']:
		channelObj.deserialize(database['channels'][channel.id])
	return channelObj


#--- Pokemon ---#

# Create new pokemon data for the user
def createPokemon(member):
	userObj = loadUser(member)
	return userObj.createPokedata()

# Save pokemon data to database
def savePokedata(pokedata):
	saveUser(pokedata.getOwner())

# Load pokemon data from database
def loadPokedata(member, isMe=True):
	userObj = loadUser(member)
	if userObj.getPokedata():
		return userObj.getPokedata()
	if isMe:
		raise UserWarning("@mention You don't have a Pokemon yet. Use `!setpoke` to get started!")
	else:
		m = "{} doesn't have a Pokemon yet. ".format(member.mention)
		m += "Encourage them to use `!setpoke` to get started!"
		raise UserWarning(m)

#def setWeather(member, weather, isMe=True):
#	pokedata = loadPokemon(member, isMe)
#	pokedata['weather'] = weather
#	savePokemon(member, pokedata)
#	return
