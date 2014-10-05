
def to_hex(s):
	return ''.join(x.encode('hex') for x in s).upper()


def int_to_bytes(value, size=None):

	result = ''
	while value >= 256:
		value, mod = divmod(value, 256)
		result += chr(mod)
	result += chr(value)

	if size:
		size -= len(result)
		for n in xrange(size):
			result += '\0'

	return result[::-1]
