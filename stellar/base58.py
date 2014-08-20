
__b58chars = 'gsphnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCr65jkm8oFqi1tuvAxyz'
__b58base = len(__b58chars)

__b58inv = {}
for i, c in enumerate(__b58chars):
	__b58inv[c] = i


def encode(v):

	long_value = int(v.encode("hex_codec"), 16)

	result = ''
	while long_value >= __b58base:
		div, mod = divmod(long_value, __b58base)
		result += __b58chars[mod]
		long_value = div
	result += __b58chars[long_value]

	if v[1] == chr(0):
		result += __b58chars[0]

	return result[::-1]


def decode(v):

	padding = '' if v[0] != __b58chars[0] else '\0'

	long_value = 0
	for c in v:
		long_value *= __b58base
		long_value += __b58inv[c]

	result = ''
	while long_value >= 256:
		div, mod = divmod(long_value, 256)
		long_value = div
		result += chr(mod)
	result += chr(long_value)
	result += padding

	return result[::-1]
