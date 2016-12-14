# Discord send_message
@client.event
async def SEND(message, content):
    return await client.send_message(message.channel, content)

# Discord edit_message
@client.event
async def EDIT(message, content):
    return await client.edit_message(message, content)

# Collect command call
def getCommand(message):
    if message.content.startswith('!'):
        return message.content.split(' ')[0][1:]
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
def checkArgs(message):
    args = getArgs(message)
    req = commandlist[getCommand(message)][1].split()
    opt = [arg for arg in req if arg.startswith('[')]
    if len(req) - len(opt) <= len(args)+1 <= len(req):
        return True
    SEND(message, commandlist[getCommand(message)][1])
    return False

# Help
def help(message):
    args = getArgs(message)
    if len(args) == 0:
        m = ', '.join(['!'+c for c in sorted(commandlist.keys())])
        SEND(message, m)
    elif len(args) == 1:
        m = args[0][1:] if args[0].startswith('!') else args[0]
        if m in commandlist:
            commandlist[m][1]()
        else:
            help(message, [])
    else:
        return helphelp(message)

# I am
def iam(message):
    args = getArgs(message)
    if len(args) != 1:
        return helpiam(message)
    
    database = loadDatabase()
    database[message.author.name] = args[0]
    saveDatabase(database)
    m = '{} is now {}'.format(message.author.mention, args[0])
    SEND(message, m)

# What is
def whatis(message):
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
    SEND(message, m)

# Sleep
@client.event
async def sleep(message):
    temp = SEND(message, 'Sleeping...')
    await asyncio.sleep(10)
    EDIT(temp, 'Done sleeping')
    

# List of commands
commandlist = {
    'help': [help, '!help [*command*]'],
    'iam': [iam, '!iam *description*'],
    'whatis': [whatis, '!whatis *username*'],
    'sleep': [sleep, '!sleep']
}
