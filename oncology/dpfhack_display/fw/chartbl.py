import struct
import sys

rgbformat = "BBB"
CHAR_WIDTH = 4
CHAR_HEIGHT = 8

context = {
	'nrows' : 0,
	'ncols' : 0,
	'width' : 0,
	'height' : 0,
}


def rgbto565(r, g, b):
	return (( (r & 0xf8) ) | ((g & 0xe0) >> 5),
		( (g & 0x1c) << 3 ) | ((b & 0xf8) >> 3))


def gentbl():
	c = 0
	a = ""
	for i in range(32, 127):
		a += "%c" % chr(i)
		c += 1
		if c == 16:
			c = 0
			a = ""


def output_chr(context, out, data, offset):
	width = context['width']
	for i in range(CHAR_HEIGHT):
		off = offset + i * width
		for j in range(CHAR_WIDTH):
			o = 3 * (off + j)
			r, g, b = struct.unpack(rgbformat, data[o:o + 3])
			rgb565 = rgbto565(r, g, b)
			out += chr(rgb565[0])
			out += chr(rgb565[1])
	return out

def convert2table(context, data):
	out = ""
	width = context['width']
	for i in xrange(context['nrows']):
		off = i * CHAR_HEIGHT * width
		for j in xrange(context['ncols']):
			o = off + j * CHAR_WIDTH
			out = output_chr(context, out, data, o)
	return out

def readpnm(context, prefix):
	pnm = open(prefix + ".pnm", "r")

	d = pnm.readline()
	d = pnm.readline()
	l = pnm.readline()
	a, b = l.split()
	x, y = int(a), int(b)
	a = pnm.readline()

	l = x * y
	context['width'] = x
	context['height'] = y
	context['ncols'] = x / CHAR_WIDTH
	context['nrows'] = y / CHAR_HEIGHT

	data = pnm.read()
	pnm.close()

	return data
	
def convert2raw(context, data):

	out = ""

	for i in xrange(l):
		off = 3 * i
		r, g, b = struct.unpack(rgbformat, data[off:off + 3])
		rgb565 = rgbto565(r, g, b)
		out += chr(rgb565[0])
		out += chr(rgb565[1])

	return out

# gentbl()
c = {}

out = readpnm(c, sys.argv[1])
out = convert2table(c, out)

f = open(sys.argv[1] + ".bin", "w")
f.write(out)
f.close()
