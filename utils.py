def list_unique(seq): # Dave Kirby
	# Order preserving
	seen = set()
	return [x for x in seq if x not in seen and not seen.add(x)]


def upperfirst(x):
	if len(x) == 0:
		return x
	return x[0].upper() + x[1:]

def lowerfirst(x):
	if len(x) == 0:
		return x
	return x[0].lower() + x[1:]