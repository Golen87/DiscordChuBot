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
	if "@user" in text:
		text = text.replace("@user", getNick(message.author))
	if "@mention" in text:
		text = text.replace("@mention", message.author.mention)
	if "@poss" in text:
		text = text.replace("@poss", addPossForm(getNick(message.author)))
	if "@pokemon" in text:
		text = text.replace("@pokemon", "**{}**".format(database.getPokemonName(message.author)))
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
	balance = database.getBalance(message.author)
	cookies = database.getCookies(message.author)
	extra = (cookies > 0) * ', and **{:,}** {}'.format(cookies, Cookies)
	text = '{}, you have a balance of **{:,}** {}{}.'.format(message.author.mention, balance, Currency, extra)
	return await send(text)

# Check top list of balance
async def checkTop(message, send):
	await clearPreviousCommands(message.author, 'top')
	args = getArgs(message)
	#print(args)

	toplist = database.getTopList()[:10]
	nameWidth = len(sorted(toplist, key=lambda x:len(x[0]))[-1][0])
	message = '```#--name{}+-{}-\n'.format('-'*(nameWidth-3), Currency)

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
		database.incBalance(message.author, coins)
		return await send('_tosses you **{:,}** {}!_'.format(coins, Currency))
	else:
		return await send('_spits on you for begging!_')

# Acquire daily coin bonus
async def claimDaily(message, send):
	await clearPreviousCommands(message.author, 'daily')

	lastClaim = database.getDailyTimestamp(message.author)
	remaining = DailyCooldown - (time.time() - lastClaim)
	if remaining > 0:
		waitTime = getDurationString(remaining)
		return await send('{}, your daily bonus refreshes in _{}_.'.format(message.author.mention, waitTime))
	else:
		database.setDailyTimestamp(message.author, time.time())
		database.incBalance(message.author, DailyReward)

		extra = ''
		if random.random() < DailyCookieChance:
			database.incCookies(message.author, 1)
			extra = ', and got a {}'.format(Cookies)
		return await send('{}, you received your **{:,}** daily {}{}!'.format(message.author.mention, DailyReward, Currency, extra))

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

	if args[0] in ['10', '20', '30']:
		bet = int(args[0])
		level = 1 + ['10', '20', '30'].index(args[0])
		if database.getBalance(message.author) >= bet:
			database.incBalance(message.author, - bet)
		else:
			return await send("You don't have enough {}.".format(Currency))
	else:
		return await send("You can bet 10, 20, or 30.")

	price_money, price_cookies, image = runSlotmachine(10, level)
	database.incBalance(message.author, price_money)
	database.incCookies(message.author, price_cookies)
	winText = ''
	if price_money > 0:
		winText = '\n{}, you won **{:,}** {}! You now have **{:,}**.'.format(message.author.mention, price_money, Currency, database.getBalance(message.author))
	if price_cookies > 0:
		winText = '\n{}, you won **{:,}** {}! You now have **{:,}**.'.format(message.author.mention, price_cookies, Cookies, database.getCookies(message.author))
	return await send("You pay **{:,}** {}!\n".format(bet, Currency) + image + winText)

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

	name = pokedex.findPokemonName(content, True)
	pokedata = database.createPokemon()
	pokedex.initPokemon(pokedata, name)
	database.savePokemon(message.author, pokedata)
	m = '@user is now {} @pokemon.'.format(aOrAn(name))
	return await send(m)

# Check what pokemon a user is
async def whatis(message, send):
	content = getContent(message)
	if not content:
		return await send(commandlist[getCommand(message)][1])

	user = findMember(message, content)
	pokemon = database.getPokemonName(user, False)
	m = '{} is {} **{}**!'.format(user.mention, aOrAn(pokemon), pokemon)
	return await send(m)

# Attack user's pokemon with a selected move
async def attack(message, send):
	content = getContent(message)

	# !attack USER with MOVE
	result = re.search('(.*)\swith\s(.*)', content)
	if not result:
		return await send(commandlist[getCommand(message)][1])

	user = findMember(message, result.group(1))
	move = pokedex.getMoveByName(result.group(2))
	pokedataAtk = database.loadPokemon(message.author)
	if message.author != user:
		pokedataDef = database.loadPokemon(user, False)
	else:
		pokedataDef = pokedataAtk # Copies list-id

	if not pokedex.knowsMove(pokedataAtk, move):
		raise UserWarning("Your @pokemon doesn't know that move yet. Use `!learnmove` to learn it!")

	if database.getPokemonHp(message.author) == 0:
		raise UserWarning("Your @pokemon is unable to fight. Use `!heal` first!".format())

	lastStamp = database.getTimestamp(message.author, 'attack')
	remaining = pokedex.setAttackTimer(pokedataAtk) - (time.time() - lastStamp)
	print(time, pokedex.setAttackTimer(pokedataAtk))
	if remaining > 0:
		waitTime = getDurationString(remaining)
		raise UserWarning('@mention Your attack refreshes in _{}_.'.format(waitTime))
	database.setTimestamp(message.author, 'attack', time.time())

	if database.togglePokemonFlinch(message.author):
		raise UserWarning("@pokemon flinched and couldn't move.")

	maxHp = pokedex.getCurrentStats(pokedataDef, 'HP')
	if database.getPokemonHp(user) == 0:
		await send("Your opponent is already unable to fight!")
		msg = "!attack " + content

		m = await client.wait_for_message(timeout=15, author=message.author, content=msg)
		if m:
			await send('Stop it!')
			m = await client.wait_for_message(timeout=15, author=message.author, content=msg)
			if m:
				await send('STOP!')
				m = await client.wait_for_message(timeout=15, author=message.author, content=msg)
				if m:
					database.savePokemon(user, {})
					return await send('You... killed your opponent...')
			else:
				return
		else:
			return

	log = []
	pokedex.attack(pokedataAtk, pokedataDef, log, move)

	a,b = False,False
	if pokedataDef['hp'] == 0:
			won = database.incPokemonBattlesWon(message.author)
			database.incPokemonBattlesLost(user, False)
			log += ["Your opponent fainted!"]
			if won > 0 and won % 10 == 0:
				database.incCaps(message.author)
				log += ["This victory earned you a bottlecap! Use it to `!hypertrain`."]
			a = True
	if pokedataAtk['hp'] == 0:
			won = database.incPokemonBattlesWon(user)
			database.incPokemonBattlesLost(message.author, False)
			log += ["You fainted!"]
			if won > 0 and won % 10 == 0:
				database.incCaps(user)
				log += ["This victory earned your enemy a bottlecap! They can it to `!hypertrain`."]
			b = True
	if a and b:
		log += ["A draw!"]
	database.savePokemon(user, pokedataDef)
	database.savePokemon(message.author, pokedataAtk)

	log = '\n'.join(log)
	log = log.replace('@opponent', '**{}**'.format(database.getPokemonName(user)))
	return await send(log)

async def battles(message, send):
	wins, losses = database.getPokemonBattleStats(message.author)
	raise UserWarning("Your @pokemon has won {} and lost {} battles so far!".format(wins, losses))

# Heal your pokemon to full max health
async def heal(message, send):
	pokedata = database.loadPokemon(message.author)

	pokedex.restorePokemon(pokedata)
	database.savePokemon(message.author, pokedata)
	newHp = database.getPokemonHp(message.author)

	m = '@poss @pokemon was healed to ({0}/{0}) hp!'.format(newHp)
	return await send(m)

# Teach your pokemon a new move, given that it's allowed
async def learnmove(message, send):
	pokedata = database.loadPokemon(message.author)

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

	pokemon = database.getPokemonName(message.author)
	move = pokedex.getMoveByName(movename, pokemon)

	#raise UserWarning("**{}** doesn't know that move yet. Use `!learnmove` to learn it!".format(pokedata['pokemon']))

	oldMove = pokedex.learnMove(pokedata, move, slot)
	database.savePokemon(message.author, pokedata)

	if slot and oldMove != None:
		return await send('1, 2 and... Poof! @poss @pokemon forgot **{}** and... @pokemon learned **{}**!'.format(oldMove, move))
	else:
		return await send('@poss @pokemon learned **{}**!'.format(move))

# Check your Pokemon's stats
async def stats(message, send):
	pokedata = database.loadPokemon(message.author)
	stats = pokedex.getCurrentStats(pokedata)
	table = ['{:>7}: {}'.format(stat, stats[stat]) for stat in stats]
	return await send("@poss @pokemon```Python\n{}```".format('\n'.join(table)))

# Check your Pokemon's stages
async def stages(message, send):
	pokedata = database.loadPokemon(message.author)
	stages = pokedex.getCurrentStages(pokedata)
	table = ['{:>11}: {}'.format(stat, stages[stat]) for stat in stages]
	return await send("@poss @pokemon```Python\n{}```".format('\n'.join(table)))

# Check your Pokemon's moveset
async def moveset(message, send):
	pokedata = database.loadPokemon(message.author)
	moveset = database.getPokemonMoveset(message.author)
	table = ['{}) {}'.format(m+1, moveset[m] if moveset[m] else '-') for m in range(len(moveset))]
	return await send("@poss @pokemon```Python\n{}```".format('\n'.join(table)))

# Train your Pokemon's EV
async def trainev(message, send):
	value, stat = getArgs(message)
	if not value.isdigit():
		return await send(commandlist[getCommand(message)][1])
	value = int(value)
	stat = pokedex.checkStat(stat)

	pokedata = database.loadPokemon(message.author)
	result = pokedex.trainEV(pokedata, value, stat)
	database.savePokemon(message.author, pokedata)
	return await send("@poss @pokemon trained and its {}-EV is now ({})!".format(stat, result))

#Reset your Pokemon's EV
async def resetev(message, send):
	pokedata = database.loadPokemon(message.author)
	pokedex.resetEV(pokedata)
	database.savePokemon(message.author, pokedata)
	return await send("Your Pokemon's EVs have been reset!")

async def hypertrain(message, send):
	caps = database.getCaps(message.author)
	if caps <= 0:
		raise UserWarning("@mention You don't have enough bottlecaps to pay the hypertraining. Win more battles to get some!")

	args = getArgs(message)
	stat = pokedex.checkStat(args[0])
	pokedata = database.loadPokemon(message.author)
	pokedex.maxIV(pokedata, stat)
	database.savePokemon(message.author, pokedata)

	caps = database.incCaps(message.author, -1)
	return await send("@user payed a bottlecap. @pokemon hypertrained its {}!".format(stat))

async def admin(message, send):
	args = getArgs(message)
	try:
		value = int(args[0])
	except:
		raise UserWarning("@mention Invalid stage. It has to be between -6–6!")
	stat = None if len(args) < 2 else args[1]

	pokedata = database.loadPokemon(message.author)
	pokedex.raiseStage(pokedata, value, stat)
	database.savePokemon(message.author, pokedata)

	if stat:
		return await send("Raised {}-stage by {}!".format(stat, value))
	else:
		return await send("Raised all stages by {}!".format(value))


# List of commands
commandlist = {
	'help': [help, '!help [*command*]', 'args'],

	# Pokemon
	'setpoke': [setpoke, '!setpoke *pokemon*', 'content'],
	'whatis': [whatis, '!whatis *username*', 'args'],
	'stats': [stats, '!stats', 'content'],
	'moveset': [moveset, '!moveset', 'content'],
	'attack': [attack, '!attack *username* with *attack*', 'content'],
	'heal': [heal, '!heal', 'args'],
	'learnmove': [learnmove, '!learnmove *move* [*1–4*]', 'content'],
	'trainev': [trainev, '!trainev *1–252* *stat*', 'args'],
	'resetev': [resetev, '!resetev', 'args'],
	'hypertrain': [hypertrain, '!hypertrain *stat*', 'args'],
	'stages': [stages, '!stages', 'content'],
	'admin': [admin, '!admin *stages* [*stat*]', 'args'],
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
}


# Token
with open('token.txt') as f:
	token = f.readlines()[0].strip()
client.run(token)

# To add bot to server, see https://discordapp.com/developers/docs/topics/oauth2
# There is a link to the "add to server" API under "Adding bots to guilds"
