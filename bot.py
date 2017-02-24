import discord, asyncio, random, re, time
import speech
import cards
from utils import *
import databaseManager as database

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
		send = lambda content : SEND(message, content)
		response = await checkArgs(message, send)
		if not response:
			response = await commandlist[command][0](message, send)
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
				send = lambda content : EDIT(myMessage, content)
				await send(random.choice(stuttering))
				response = await checkArgs(newMessage, send)
				if not response:
					response = await commandlist[command][0](newMessage, send)
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

"""
# I am
async def iam(message, send):
	content = getContent(message)
	database = loadDatabase()
	database[message.author.name] = content
	saveDatabase(database)
	m = '{} is now {}'.format(message.author.mention, content)
	return await send(m)
"""
"""
# What is
async def whatis(message, send):
	content = getContent(message)
	if not content:
		return helpwhatis()

	name = content
	mention = content
	if message.mentions:
		name = message.mentions[0].nick
		mention = message.mentions[0].mention
	else:
		for m in client.get_all_members():
			if content.lower() in [m.nick.lower() if m.nick else '', m.name.lower()]:
				name = m.name
				mention = m.mention
				break
			
	database = loadDatabase()
	if name in database:
		m = '{} is {}'.format(mention, database[name])
	else:
		m = 'There is no description for {}.'.format(mention)
	return await send(m)
"""

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
	
	toplist = database.getTopList()[:5]
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
	response = await send('I will delete these in five seconds.')
	await asyncio.sleep(5)
	try:
		await DELETE(message)
		await DELETE(response)
	except discord.Forbidden:
		await EDIT(response, "I don't have the permission to delete messages.")
	return 'delete'


# List of commands
commandlist = {
	'help': [help, '!help [*command*]', 'args'],
	#'iam': [iam, '!iam *description*', 'content'],
	#'whatis': [whatis, '!whatis *username*', 'args'],
	'sleep': [sleep, '!sleep', 'args'],
	'count': [count, '!count', 'args'],
	'hello': [hello, '!hello', 'args'],
	'guess': [guess, '!guess', 'args'],
	'choose': [choose, '!choose *item* [, *item* ...] [or *item*]', 'content'],
	'tcah': [tcah, '!tcah [*phrase* ...]', 'content'],
	
	'test': [test, '!test', 'args'],
	'balance': [checkBalance, '!balance', 'args'],
	'top': [checkTop, '!top', 'args'],
	'beg': [beg, '!beg', 'args'],
	'daily': [claimDaily, '!daily', 'args'],
	'slot': [slotmachine, '!slot *10*|*20*|*30*', 'args'],
}


# Token
client.run('MjEwMDM0Mjc4NDI2MzQ1NDcy.CoI5Ng.yK0wqGGVlJryjkzX-hl6BYWl_q4')

# To add bot to server, see https://discordapp.com/developers/docs/topics/oauth2
# There is a link to the "add to server" API under "Adding bots to guilds"

"""+========================
|   | A | B | C | D | E |
|___|___|___|___|___|___|
| 1 |???|???|???|???|???| 03
|___|___|___|___|___|___| ⚪2
| 2 |???|???|???|???|???| 07
|___|___|___|___|___|___| ⚪0
| 3 |???|???|???|???|???| 04
|___|___|___|___|___|___| ⚪1
| 4 |???|???|???|???|???| 04
|___|___|___|___|___|___| ⚪2
| 5 |???|???|???|???|???| 07
|___|___|___|___|___|___| ⚪1
     07  05  03  06  04
     ⚪0  ⚪0  ⚪2  ⚪3  ⚪1"""
