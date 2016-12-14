import discord, asyncio, json, random, re
import speech
import cards, re
#import commands

client = discord.Client()
colors = True
RED = colors * "\033[31;5m"
GRE = colors * "\033[32;5m"
BLU = colors * "\033[34;5m"
CYA = "\033[36;5m"
WHI = colors * "\033[0m"

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
	if message.author == client.user:
		print('{}: {}'.format(message.author, CYA + message.content + WHI))
		return
	else:
		print('{}: {}'.format(message.author, GRE + message.content + WHI))

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
		if not response:
			print(RED + 'Warning: Function did not return sent message!' + WHI)
		response_history.append((message, response))
		response_history = response_history[-10:]

@client.event
async def on_message_edit(oldMessage, newMessage):
	if newMessage.author == client.user:
		print('{}: {} {}'.format(newMessage.author, RED+'(edit)'+WHI, CYA + newMessage.content + WHI))
		return
	else:
		print('{}: {} {}'.format(newMessage.author, RED+'(edit)'+WHI, GRE + newMessage.content + WHI))

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
				response_history[i] = (newMessage, response)

@client.event
async def on_member_join(member):
	server = member.server
	fmt = 'Welcome {0.mention} to {1.name}!'
	await client.send_message(server, fmt.format(member, server))

# Discord send_message
async def SEND(message, content):
	return await client.send_message(message.channel, content)

# Discord edit_message
async def EDIT(message, content):
	return await client.edit_message(message, content)

# Collect command call
def getCommand(message):
	if message.content.startswith('!'):
		return message.content.split(' ')[0][1:].lower()
	return ''

# Collect command args content
def getContent(message):
	if len(message.content.split(' ', 1)) > 1:
		return message.content.split(' ', 1)[1]
	return ''
	
# Collect command args
def getArgs(message):
	return message.content.split(' ')[1:]

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

# Save whatis to database
def saveDatabase(database):
	with open('database.json', 'w') as f:
		json.dump(database, f)

# Load whatis from database
def loadDatabase():
	f = open('database.json')
	database = json.load(f)
	f.close()
	return database


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

# I am
async def iam(message, send):
	content = getContent(message)
	database = loadDatabase()
	database[message.author.name] = content
	saveDatabase(database)
	m = '{} is now {}'.format(message.author.mention, content)
	return await send(m)

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
	await send(m)

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

# Test
async def test(message, send):
	await send('Yes, hello!')

# List of commands
commandlist = {
	'help': [help, '!help [*command*]', 'args'],
	'iam': [iam, '!iam *description*', 'content'],
	'whatis': [whatis, '!whatis *username*', 'args'],
	'sleep': [sleep, '!sleep', 'args'],
	'count': [count, '!count', 'args'],
	'hello': [hello, '!hello', 'args'],
	'guess': [guess, '!guess', 'args'],
	'choose': [choose, '!choose *item* [, *item* ...] [or *item*]', 'content'],
	'tcah': [tcah, '!tcah [*phrase* ...]', 'content'],
	'test': [test, '!test', 'args'],
}


# Token
client.run('MjEwMDM0Mjc4NDI2MzQ1NDcy.CoI5Ng.yK0wqGGVlJryjkzX-hl6BYWl_q4')

# To add bot to server, see https://discordapp.com/developers/docs/topics/oauth2
# There is a link to the "add to server" API under "Adding bots to guilds"
