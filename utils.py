
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

# Get nick/name from member
def getNick(member):
	if member.nick:
		return member.nick
	return member.name
