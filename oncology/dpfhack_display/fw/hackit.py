#!/usr/bin/python
import struct
import sys
sys.path.append("./Debug")
import dpf
import time
import binascii

# DPF profiles
import profiles

# If you are an expert, set this to 0 to avoid the warnings
paranoia_mode = 1

JUMPTABLE_OFFSET = 0x80
HEXDIR = "hexfiles/"

instructions = [
	"""Press and hold MENU while USB is plugged in.
If successful, you will get the 'USB connect' message and the device
will appear as non-USB storage device"""
]

ins_common = """To put the device back into (almost) original state working
as USB storage, press the RESET button."""

############################################################################

bswap = lambda x: ( (x >> 8) & 0xff ) | ((x << 8) & 0xff00)

def dump_flash(d, fname, offset, size):
	data = d.readFlash(offset, size)
	f = open(fname, "wb")
	f.write(data)
	f.close()

def find_dpf(version):
	for i in profiles.KNOWN_DPFS:
		v = i[0]
		if v[0] == str(version[0]) and v[1] == str(version[1]) and v[2] == str(version[2]):
			print "Found matching version info"
			return i
	return None

def get_module(buf, n):
	n *= 8
	start, end, flashaddr = struct.unpack("<HHI", buf[n:n+8])

	start = bswap(start)
	end = bswap(end)

	return start, end, flashaddr

def patch_module(d, record, buf):
	n = record[0]
	if n == profiles.BINARY: # Write full binary into sector
		start, flashaddr = record[1]
		f = open(record[2])
		d.eraseFlash(flashaddr)
		buf = f.read()
		f.close()
		d.writeFlash(flashaddr, buf)
	elif n == profiles.PATCH: # We make a copy of a full sector
		start, flashaddr = record[1]
		print "Patching sector addr %06x with %s" % (flashaddr, record[2])
		d.patchSector(start, flashaddr, HEXDIR + record[2])
	elif n == profiles.COPY: # We make a copy of a full sector
		src, dest = record[1]
		print "Copying sector from 0x%06x to 0x%06x..." %(src, dest)
		data = d.readFlash(src, 0x10000)
		d.eraseFlash(dest)
		d.writeFlash(dest, data)
	else:
		print "Analyzing module %d..." % n
		start, end, flashaddr = get_module(buf, n)
		l = end - start
		start += 0x800
		data = d.readFlash(flashaddr, l)
		c = binascii.crc32(data) & 0xffffffff
		checksums = record[1]
		i = 0
		try:
			i = checksums.index(c)
		except ValueError:
			print "CRC32 does not match: 0x%08lx" % c
			return False

		n = len(checksums) - 1
			
		if i == n:
			print "Seems up to date. Do you still wish to patch?"
			a = raw_input("Type 'yes' to continue > ")
			if a != "yes":
				return True
			print "Updating module.."
		else:
			print "Patching from version %d to %d" % (i, n)

		d.patchSector(start, flashaddr, HEXDIR + record[2])

	return True

def recognize(d):
	print "Reading flash..."
	buf = d.readFlash(0x0, 0x280)

	print "done"
	b = buf[:7]
	xmem, code, dummy, offset = struct.unpack(">HHBH", b)
	version = (buf[0x50:0x58], buf[0x60: 0x70], buf[0x80:0x88])

	dpf = find_dpf(version)
	if not dpf:
		print "No DPF found. Create a record or look for one"
		print version
	else:
		print "Identifier:", dpf[1]
		di = dpf[3]
		di['offset'] = offset

	return dpf

def patch(d, dpf):
	if (paranoia_mode):
		print """Now patching. There is no 100% guarantee that your device will
	work after doing this. You must never unplug the device from USB while
	it is being updated.
	Are you sure you take all risks and that you want to continue?"""
		a = raw_input("Type 'yes' to continue > ")
		if a != "yes":
			print "Aborting."
			return False

	p = dpf[4]

	buf = d.readFlash(JUMPTABLE_OFFSET, dpf[3]['offset'])
	for i in p[2]:
		if not patch_module(d, i, buf):
			return False
	
	return True
#
#
# MAIN

if len(sys.argv) != 2:
	print "Usage: %s [<generic scsi device> | usb0]" % sys.argv[0]
	print "You may have to run this as root when accessing generic scsi devices"
	sys.exit(-1)

d = dpf.open(sys.argv[1])

dpf = recognize(d)
if dpf:
	r = dpf[4]
	ret = patch(d, dpf)
	if ret:
		print
		print "Now disconnect the DPF from USB."
		print "To activate the 'developer mode':"
		print
		print instructions[r[0]]
		print
		print ins_common
	else:
		print "DPF might not be completely patched."
d.close()
