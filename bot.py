import discord, asyncio, random, re, time
import speech
import cards
from utils import *
import databaseManager as database
import pokedex.pokedexManager as pokedex

client = discord.Client()

response_history = []

cracks = ['Ok', 'Okay', 'Ack', 'Ah', 'Ehem', 'Oh', 'Uh', 'Um', 'Right', 'Wait', 'Well then']
stuttering = cracks[:]
stuttering += cracks[:]
stuttering += [w + '...' for w in cracks]
stuttering += [w + '!' for w in cracks]
stuttering += [w[0] + '-' + w.lower() for w in cracks]

deck = cards.Cards()


@client.event
async def on_ready():
	print(BLU + 'Successfully logged in as {} ({})'.format(client.user.name, client.user.id) + WHI)

@client.event
async def on_message(message):
	logMessage(message)
	if message.author == client.user: return

	# whatis (alt)
	#content = message.content
	#for s in '_*':
	#	if content.startswith(s) and content.endswith(s):
	#		content = content[1:-1]
	#if len(message.content.split(' ')) > 1:
	#	if message.content.startswith('_examines'):
	#		pass
	# NAH

	command = getCommand(message)
	if command in commandlist:
		send = lambda content : SEND(message, formatUserTags(message, content))
		response = await checkArgs(message, send)
		if not response:
			try:
				response = await commandlist[command][0](message, send)
			except UserWarning as error:
				response = await send(str(error))
		global response_history
		if response == 'delete':
			return
		if not response:
			print(RED + 'Warning: Function "{}" did not return sent message!'.format(command) + WHI)
		response_history.append((message, response))
		response_history = response_history[-100:]

@client.event
async def on_message_edit(oldMessage, newMessage):
	logMessage(newMessage, "edit")
	if newMessage.author == client.user: return

	global response_history
	for i in range(len(response_history)):
		userMessage,myMessage = response_history[i]
		if oldMessage.id == userMessage.id:
			command = getCommand(newMessage)
			if command in commandlist:
				send = lambda content : EDIT(myMessage, formatUserTags(newMessage, content))
				await send(random.choice(stuttering))
				response = await checkArgs(newMessage, send)
				if not response:
					try:
						response = await commandlist[command][0](newMessage, send)
					except UserWarning as error:
						response = await send(str(error))
				if response == 'delete':
					return
				response_history[i] = (newMessage, response)

@client.event
async def on_message_delete(message):
	logMessage(message, "delete")

@client.event
async def on_member_join(member):
	server = member.server
	fmt = 'Welcome {0.mention} to {1.name}!'
	await client.send_message(server, fmt.format(member, server))


# Pretty print message
def logMessage(message, msgtype = ''):
	time = message.timestamp.strftime('[%H:%M:%S]')

	userColor = YEL
	if message.author == client.user:
		userColor = CYA

	extra = '{}({}) '.format(RED, msgtype) if msgtype else ''

	print('{} {} {} {}: {}'.format(
		BLA + time,
		MAG + message.server.name,
		'#' + message.channel.name,
		userColor + message.author.name,
		extra + WHI + message.content)
	)

# Replace tags in error message to data
def formatUserTags(message, text):
	if "@currency" in text:
		text = text.replace("@currency", Currency)
	if "@cookies" in text:
		text = text.replace("@cookies", Cookies)
	if "@user" in text:
		text = text.replace("@user", getNick(message.author))
	if "@mention" in text:
		text = text.replace("@mention", message.author.mention)
	if "@poss" in text:
		text = text.replace("@poss", addPossForm(getNick(message.author)))
	if "@pokemon" in text:
		user = database.loadUser(message.author)
		if user.getPokedata():
			text = text.replace("@pokemon", str(user.getPokedata()))
		else:
			print("{}{} doesn't have a pokemon, yet @pokemon was called.{}".format(RED, getNick(message.author), WHI))
	return text


# Discord send_message
async def SEND(message, content):
	return await client.send_message(message.channel, content)

# Discord edit_message
async def EDIT(message, content):
	return await client.edit_message(message, content)

# Discord edit_message
async def DELETE(message):
	return await client.delete_message(message)

# Check if args are OK
async def checkArgs(message, send):
	args = getArgs(message)
	req = commandlist[getCommand(message)][1]
	for bundle in re.findall(r'\[([^]]*)\]', req):
		req = req.replace(bundle, '')
	req = req.split()
	opt = [arg for arg in req if arg.startswith('[')]
	if commandlist[getCommand(message)][2] == 'args':
		if len(req) - len(opt) <= len(args)+1 <= len(req):
			return None
	if commandlist[getCommand(message)][2] == 'content':
		if len(req) - len(opt) <= len(args)+1:
			return None
	return await send(commandlist[getCommand(message)][1])

# Return a member mentioned in a message, including name/nick
def findMember(message, name):
	for m in client.get_all_members():
		if name.lower() in [m.nick.lower() if m.nick else '', m.name.lower()] or m in message.mentions:
			return m
	raise UserWarning("@mention Invalid target. I don't know who _{}_ is!".format(name))

@client.event
async def bwark(message, send):
	a = getContent(message)
	if a == "":
		return await send("Bwark!")

# Help
async def help(message, send):
	args = getArgs(message)
	if len(args) == 0:
		m = ', '.join(['!'+c for c in sorted(commandlist.keys())])
		return await send(m)
	elif len(args) == 1:
		m = args[0][1:] if args[0].startswith('!') else args[0]
		if m in commandlist:
			return await send(commandlist[m][1])
		else:
			message.content = ''
			return await help(message, send)


# Sleep
async def sleep(message, send):
	temp = await send('Sleeping...')
	await asyncio.sleep(5)
	return await EDIT(temp, 'Done sleeping')

# Count
async def count(message, send):
	number = 1
	temp = await send('Counting... ' + str(number))
	await asyncio.sleep(1)
	while number < 10:
		number += 1
		temp = await EDIT(temp, 'Counting... ' + str(number))
		await asyncio.sleep(1)
	return await EDIT(temp, 'Done counting')

# Hello
async def hello(message, send):
	m = 'Hello {0.author.mention}!'.format(message)
	return await send(m)

# Guess
async def guess(message, send):
	await send('Guess a number between 1 to 10')

	def guess_check(m):
		return m.content.isdigit()

	guess = await client.wait_for_message(timeout=10.0, author=message.author, check=guess_check)
	answer = random.randint(1, 10)
	if guess is None:
		fmt = 'Sorry, you took too long. It was {}.'
		await send(fmt.format(answer))
		return
	if int(guess.content) == answer:
		await send('You are right!')
	else:
		await send('Sorry. It is actually {}.'.format(answer))

# Choose
async def choose(message, send):
	def getFlavor():
		return 'I choose _{0}.upper()_!'

	content = getContent(message)
	args = re.split(',| or |\|', content)
	args = list(filter(None, map(str.strip, args)))
	um = random.choice(stuttering)
	um = um if um[-1] in '.!' else um + '.'
	um = um + ' '
	if args:
		if len(args) > 1:
			m = 'I choose _{}_!'.format(random.choice(args).strip())
			if random.random() < 0.5:
				m = um + m
		else:
			m = 'I choose... _{}_?'.format(random.choice(args).strip())
			if random.random() < 0.7:
				m = um + m
	else:
		return await send(commandlist[getCommand(message)][1])
	return await send(m)

# Temporary CAH
async def tcah(message, send):
	content = getContent(message)
	if not content:
		black = deck.getRandomBlack(-1)
		whites = [deck.getRandomWhite() for i in range(black['pick'])]
		m = cards.insertWhiteInBlack(black['text'], whites)
		return await send(m)
	else:
		whites = list(map(str.strip, re.split('\||\/|\\\\', content)))
		if deck.isAcceptableLength(len(whites)):
			black = deck.getRandomBlack(len(whites))
			m = cards.insertWhiteInBlack(black['text'], whites)
			return await send(m)
		else:
			m = random.choice(stuttering)
			return await send(m)

# Check balance
async def checkBalance(message, send):
	user = database.loadUser(message.author)
	balance = user.getBalance()
	cookies = user.getCookies()
	extra = (cookies > 0) * ', and **{:,}** @cookies'.format(cookies)
	text = '{}, you have a balance of **{:,}** @currency{}.'.format(message.author.mention, balance, extra)
	return await send(text)

# Check top list of balance
async def checkTop(message, send):
	await clearPreviousCommands(message.author, 'top')
	args = getArgs(message)
	#print(args)

	toplist = database.getTopList()[:10]
	nameWidth = len(sorted(toplist, key=lambda x:len(x[0]))[-1][0])
	message = '```#--name{}+-@currency-\n'.format('-'*(nameWidth-3))

	for i in range(len(toplist)):
		name, balance = toplist[i]
		message += '{}. {} | {:,}\n'.format(i+1, name.ljust(nameWidth), balance)
	message += '```'
	return await send(message)

# Beg for coins
async def beg(message, send):
	await clearPreviousCommands(message.author, 'beg')
	coins = random.randint(0, 5)
	if coins > 1:
		user = database.loadUser(message.author)
		user.incBalance(coins)
		database.saveUser(user)
		return await send('_tosses you **{:,}** @currency!_'.format(coins))
	else:
		return await send('_spits on you for begging!_')

# Acquire daily coin bonus
async def claimDaily(message, send):
	await clearPreviousCommands(message.author, 'daily')

	user = database.loadUser(message.author)
	remaining = user.getTimeRemaining('daily', DailyCooldown)
	if remaining > 0:
		waitTime = getDurationString(remaining)
		return await send('{}, your daily bonus refreshes in _{}_.'.format(message.author.mention, waitTime))
	else:
		user.setTimestamp('daily')
		user.incBalance(DailyReward)

		extra = ''
		if random.random() < DailyCookieChance:
			user.incCookies(1)
			extra = ', and got a @cookies'

		database.saveUser(user)
		return await send('{}, you received your **{:,}** daily @currency{}!'.format(message.author.mention, DailyReward, extra))

# Search and remove last paired input from user
async def clearPreviousCommands(member, cmdToRemove):
	global response_history
	for i in range(len(response_history)-1,-1,-1):
		try:
			userMessage,myMessage = response_history[i]
		except:
			return # End of array. Some other process removed it
		if userMessage.author == member:
			command = getCommand(userMessage)
			if command in commandlist and command == cmdToRemove:

				# Special case. Don't remove winning messages
				if command == 'slot' and 'you won' in myMessage.content:
					continue

				response_history.pop(i)
				try:
					await DELETE(userMessage)
					await DELETE(myMessage)
				except discord.Forbidden:
					print("{}Warning: Missing permission to delete messages.{}".format(RED, WHI))


# Execute slotmachine and reward player
async def slotmachine(message, send):
	await clearPreviousCommands(message.author, 'slot')
	args = getArgs(message)
	user = database.loadUser(message.author)

	if args[0] in ['10', '20', '30']:
		bet = int(args[0])
		level = 1 + ['10', '20', '30'].index(args[0])
		if user.getBalance() >= bet:
			user.incBalance(-bet)
		else:
			return await send("You don't have enough @currency.")
	else:
		return await send("You can bet 10, 20, or 30.")

	price_money, price_cookies, image = runSlotmachine(10, level)
	user.incBalance(price_money)
	user.incCookies(price_cookies)
	database.saveUser(user)

	winText = ''
	if price_money > 0:
		winText = '\n{}, you won **{:,}** @currency! You now have **{:,}**.'.format(message.author.mention, price_money, user.getBalance())
	if price_cookies > 0:
		winText = '\n{}, you won **{:,}** @cookies! You now have **{:,}**.'.format(message.author.mention, price_cookies, user.getCookies())
	return await send("You pay **{:,}** @currency!\n".format(bet) + image + winText)

# Test
async def test(message, send):
	content = getContent(message)
	#try:
	#	return await send(eval(content))
	#except Exception as e:
	#	return await send(e)
	#response = await send('I will delete these in five seconds.')
	#await asyncio.sleep(5)
	#try:
	#	await DELETE(message)
	#	await DELETE(response)
	#except discord.Forbidden:
	#	await EDIT(response, "I don't have the permission to delete messages.")
	#return 'delete'


# Set pokemon (i am) by creating a new pokemon for the user
async def setpoke(message, send):
	content = getContent(message)

	pokemon = pokedex.getPokemonByName(content, True)
	pokedata = database.createPokemon(message.author)
	pokedata.initialize(pokemon)
	database.savePokedata(pokedata)
	m = '@user is now {} @pokemon.'.format(aOrAn(pokemon))
	return await send(m)

# Check what pokemon a user is
async def whatis(message, send):
	content = getContent(message)
	if not content:
		return await send(commandlist[getCommand(message)][1])

	user = findMember(message, content)
	pokemon = str(database.loadPokedata(user, False))
	m = '{} is {} {}!'.format(user.mention, aOrAn(pokemon), pokemon)
	return await send(m)

# Attack user's pokemon with a selected move
async def attack(message, send):
	content = getContent(message)

	if getCommand(message) == 'attack':
		# !attack USER with MOVE
		result = re.search('(.*)\swith\s(.*)', content)
		if not result:
			return await send(commandlist[getCommand(message)][1])
		other = findMember(message, result.group(1))
		move = pokedex.getMoveByName(result.group(2))
	elif getCommand(message) == 'use':
		# !use MOVE on USER
		result = re.search('(.*)\son\s(.*)', content)
		if result:
			move = pokedex.getMoveByName(result.group(1))
			other = findMember(message, result.group(2))
		else:
			result = re.search('(.*)', content)
			if result:
				move = pokedex.getMoveByName(result.group(1))
				other = message.author
			else:
				return await send(commandlist[getCommand(message)][1])
	else:
		return await send(commandlist[getCommand(message)][1])

	pokeAtk = database.loadPokedata(message.author)
	if message.author.id == other.id:
		pokeDef = pokeAtk
	else:
		pokeDef = database.loadPokedata(other, False)
	attacker = pokeAtk.getOwner()
	defender = pokeDef.getOwner()

	if not pokeAtk.knowsMove(move):
		raise UserWarning("Your @pokemon doesn't know that move yet. Use `!learnmove` to learn it!")
	if not pokeAtk.canUseMove(move):
		raise UserWarning("{} is out of PP!".format(move.getName()))

	if pokeAtk.getHp() == 0:
		raise UserWarning("Your @pokemon is unable to fight. Use `!heal` first!".format())
	if pokeDef.getHp() == 0:
		raise UserWarning("The opponent's {} is unable to fight.".format(pokeDef))

	remaining = attacker.getTimeRemaining('attack', pokeAtk.getAttackCooldown())
	if remaining > 0:
		waitTime = getDurationString(remaining)
		raise UserWarning('@mention Your attack refreshes in _{}_.'.format(waitTime))
	attacker.setTimestamp('attack')

	# Attack start
	try:
		log = []
		pokedex.attack(pokeAtk, pokeDef, log, move)

		if pokeAtk == pokeDef and pokeAtk.getHp() == 0:
			log += ["Your @attacker fainted!"]
		else:
			if pokeDef.getHp() == 0:
				won = pokeAtk.incStatistic('battlesWon', 1)
				pokeDef.incStatistic('battlesLost', 1)
				log += ["Opponent's @defender fainted!"]
				if won > 0 and won % 10 == 0:
					attacker.incCaps(1)
					log += ["{} You earned a bottlecap! Use it to `!hypertrain`.".format(message.author.mention)]
			if pokeAtk.getHp() == 0:
				won = pokeDef.incStatistic('battlesWon', 1)
				pokeAtk.incStatistic('battlesLost', 1)
				log += ["Your @attacker fainted!"]
				if won > 0 and won % 10 == 0:
					defender.incCaps(1)
					log += ["{} You earned a bottlecap! Use it to `!hypertrain`.".format(other.mention)]
		raise pokedex.EndAttack()
	except pokedex.EndAttack as message:
		database.saveUser(attacker)
		database.saveUser(defender)

		if str(message):
			log += [str(message)]
		log = '\n'.join(log)
		log = log.replace('@attacker', str(pokeAtk))
		log = log.replace('@defender', str(pokeDef))
		return await send(log)

###
#	this whole section works but is dumb af since dot is not getting applied IN TURN. but no clue how to fix that.	
#	if move.getTitle() == 'Sunny Day':	
#		for users in database.loadAllUsers():
#			database.setWeather(users, 'sunny')
#		log += ["The sunlight turned harsh!"]
#	if move.getTitle() == 'Hail':
#		print("test", move)
#		for users in database.loadAllUsers():
#			database.setWeather(users, 'hail')
#		log += ["It started to hail!"]
#	if move.getTitle() == 'Rain Dance':
#		for users in database.loadAllUsers():
#			database.setWeather(users, 'rain')
#		log += ["TIt started to rain!"]
#	if move.getTitle() == 'Sandstorm':
#		for users in database.loadAllUsers():
#			database.setWeather(users, 'sandstorm')
#		log += ["A sandstorm came up! DUDUDUDUDUDU."]
###

async def battles(message, send):
	pokedata = database.loadPokedata(message.author)
	won = pokedata.getStatistic('battlesWon')
	lost = pokedata.getStatistic('battlesLost')
	raise UserWarning("Your @pokemon has won {} and lost {} battles so far!".format(won, lost))

# Heal your pokemon to full max health
async def heal(message, send):
	pokedata = database.loadPokedata(message.author)
	if pokedata.getHp() != 0:
		return await send("Your Pokemon can still fight! Only fainted Pokemon are able to `!heal`.")
	pokedata.fullRestore()
	database.savePokedata(pokedata)

	hp = pokedata.getHp()
	m = '@poss @pokemon was fully restored to ({0}/{0}) hp!'.format(hp)
	return await send(m)

# Teach your pokemon a new move, given that it's allowed
async def learnmove(message, send):
	content = getContent(message)
	if not content:
		return await send(commandlist[getCommand(message)][1])
	try:
		movename, slot = content.rsplit(' ', 1)
		slot = int(slot)
		if slot < 1 or slot > 4:
			raise UserWarning("@mention Invalid slot. It has to be between 1–4!")
	except:
		movename = content
		slot = None

	pokedata = database.loadPokedata(message.author)
	move = pokedex.getMoveByName(movename, pokedata.getPokemon())

	oldMove = pokedata.learnMove(move, slot)
	database.savePokedata(pokedata)

	if slot and oldMove != None:
		return await send('1, 2 and... Poof! @poss @pokemon forgot **{}** and... @pokemon learned {}!'.format(oldMove, move))
	else:
		return await send('@poss @pokemon learned {}!'.format(move))

# Check your Pokemon's stats
async def stats(message, send):
	pokedata = database.loadPokedata(message.author)
	stats = pokedata.getStats()
	table = ['{:>7}: {}'.format(stat, stats[stat]) for stat in stats]
	return await send("@poss @pokemon```Python\n{}```".format('\n'.join(table)))

# Check your Pokemon's stages
async def stages(message, send):
	pokedata = database.loadPokedata(message.author)
	stages = pokedata.getStages()
	table = ['{:>8}: {}'.format(stat, stages[stat]) for stat in stages]
	return await send("@poss @pokemon```Python\n{}```".format('\n'.join(table)))

# Check your Pokemon's moveset
async def moveset(message, send):
	pokedata = database.loadPokedata(message.author)
	table = pokedata.getMovesetTable()
	return await send("@poss @pokemon {}".format(table))

# Train your Pokemon's EV
async def trainev(message, send):
	value, stat = getArgs(message)
	if not value.isdigit():
		return await send(commandlist[getCommand(message)][1])
	value = int(value)
	stat = pokedex.checkStat(stat)

	pokedata = database.loadPokedata(message.author)
	result = pokedata.trainEV(value, stat)
	database.savePokedata(pokedata)
	return await send("@poss @pokemon trained and increased its {}-EV by ({})!".format(stat, result))

#Reset your Pokemon's EV
async def resetev(message, send):
	pokedata = database.loadPokedata(message.author)
	pokedata.resetEV()
	database.savePokedata(pokedata)
	return await send("Your Pokemon's EVs have been reset!")

async def hypertrain(message, send):
	user = database.loadUser(message.author)
	if user.getCaps() <= 0:
		raise UserWarning("@mention You don't have enough bottlecaps to pay the hypertraining. Win more battles to get some!")

	args = getArgs(message)
	stat = pokedex.checkStat(args[0])
	user.getPokedata().maxIV(stat)
	user.incCaps(-1)
	database.saveUser(user)

	return await send("@user payed a bottlecap. @pokemon hypertrained its {}!".format(stat))

async def admin(message, send):
	args = getArgs(message)
	try:
		value = int(args[0])
	except:
		raise UserWarning("@mention Invalid stage. It has to be between -6–6!")
	try:
		stat = args[1]
	except:
		return await send(commandlist[getCommand(message)][1])

	pokedata = database.loadPokedata(message.author)
	log = []
	pokedex.raiseStage(pokedata, value, stat, log)
	database.savePokedata(pokedata)

	log = '\n'.join(log)
	log = log.replace('@attacker', str(pokedata))
	return await send(log)


# List of commands
commandlist = {
	'help': [help, '!help [*command*]', 'args'],

	# Pokemon
	'setpoke': [setpoke, '!setpoke *pokemon*', 'content'],
	'whatis': [whatis, '!whatis *username*', 'args'],
	'stats': [stats, '!stats', 'content'],
	'moveset': [moveset, '!moveset', 'content'],
	'attack': [attack, '!attack *username* with *attack*', 'content'],
	'use': [attack, '!use *attack* [on *username*]', 'content'],
	'heal': [heal, '!heal', 'args'],
	'learnmove': [learnmove, '!learnmove *move* [*1–4*]', 'content'],
	'trainev': [trainev, '!trainev *1–252* *stat*', 'args'],
	'resetev': [resetev, '!resetev', 'args'],
	'hypertrain': [hypertrain, '!hypertrain *stat*', 'args'],
	'stages': [stages, '!stages', 'content'],
	'admin': [admin, '!admin *stages* *stat*', 'args'],
	'battles': [battles, '!battles', 'args'],

	# General
	#'sleep': [sleep, '!sleep', 'args'],
	#'count': [count, '!count', 'args'],
	#'hello': [hello, '!hello', 'args'],
	#'guess': [guess, '!guess', 'args'],
	#'choose': [choose, '!choose *item* [, *item* ...] [or *item*]', 'content'],
	#'tcah': [tcah, '!tcah [*phrase* ...]', 'content'],
	#'test': [test, '!test *.*', 'content'],

	# Casino
	#'balance': [checkBalance, '!balance', 'args'],
	#'top': [checkTop, '!top', 'args'],
	#'beg': [beg, '!beg', 'args'],
	#'daily': [claimDaily, '!daily', 'args'],
	#'slot': [slotmachine, '!slot *10*|*20*|*30*', 'args'],
	'bwark': [bwark, "bwark", "content"],
}


# Token
with open('token.txt') as f:
	token = f.readlines()[0].strip()
client.run(token)

# To add bot to server, see https://discordapp.com/developers/docs/topics/oauth2
# There is a link to the "add to server" API under "Adding bots to guilds"
