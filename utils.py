import random
from constants import *

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

# Get nick/name from member
def getNick(member):
	if member.nick:
		return member.nick
	return member.name


# Pretty print duration
def getDurationString(duration):
	m,s = divmod(duration, 60)
	h,m = divmod(m, 60)
	h,m,s = int(h), int(m), int(s)
	if h > 0:
		return "{} hours {} minutes".format(h, m)
	elif m > 0:
		return "{} minutes {} seconds".format(m, s)
	else:
		return "{} seconds".format(s)


# Execute a round of slotmachine
def runSlotmachine(bet, level):
	symbols = ['7', '$', '®', 'Ø', '·', '©']
	reward_money = [300, 100, 15, 15, 8, 0]
	reward_cookies = [0, 0, 0, 0, 0, 1]
	spinners = [
		[2,3,0,5,1,4,3,0,5,1,4,2,0,5,2,2,3,0],
		[5,2,0,3,5,4,2,1,5,4,2,5,1,3,4,5,2,0],
		[2,4,0,1,4,3,5,2,4,3,5,2,4,3,5,2,4,0]
	]
	slot = []
	for i in range(3):
		l = len(spinners[i])
		index = random.randint(0, l-1)
		slot.append([
			spinners[i][(index-1)%l],
			spinners[i][(index+0)%l],
			spinners[i][(index+1)%l]
		])
	
	image = "```+=====+\n|{}|{}|{}|  o\n|{}|{}|{}| /\n|{}|{}|{}|/\n+=====+```".format(
		symbols[slot[0][0]], symbols[slot[1][0]], symbols[slot[2][0]],
		symbols[slot[0][1]], symbols[slot[1][1]], symbols[slot[2][1]],
		symbols[slot[0][2]], symbols[slot[1][2]], symbols[slot[2][2]]
	)

	price_money = 0
	price_cookies = 0
	if level >= 1 and slot[0][1] == slot[1][1] == slot[2][1]:
		price_money += bet * reward_money[slot[0][1]]
		price_cookies += reward_cookies[slot[0][1]]
	if level >= 2 and slot[0][0] == slot[1][0] == slot[2][0]:
		price_money += bet * reward_money[slot[0][0]]
		price_cookies += reward_cookies[slot[0][0]]
	if level >= 2 and slot[0][2] == slot[1][2] == slot[2][2]:
		price_money += bet * reward_money[slot[0][2]]
		price_cookies += reward_cookies[slot[0][2]]
	if level >= 3 and slot[0][0] == slot[1][1] == slot[2][2]:
		price_money += bet * reward_money[slot[0][0]]
		price_cookies += reward_cookies[slot[0][0]]
	if level >= 3 and slot[0][2] == slot[1][1] == slot[2][0]:
		price_money += bet * reward_money[slot[0][2]]
		price_cookies += reward_cookies[slot[0][2]]
	
	return price_money, price_cookies, image


if __name__ == "__main__":
	import time
	money = 0
	level = 1
	for level in [1,2,3]:
		stats = {}
		for i in range(100000):
			price,x = runSlotmachine(10, level)
			money += -10*level + price
			if price not in stats:
				stats[price] = 0
			stats[price] += 1
		print(money, money/level)
		for price in sorted(stats.keys()):
			print(price, str(int(10000*stats[price] / float(sum(stats.values())))/100.0 ) + "%")
		print('-'*50)
