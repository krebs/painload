# Copyright (c) 2009 Noa Resare (noa@resare.com) - In the public domain
# 
# Implements the SASL mechanism DIGEST-MD5 as defined in RFC2831 without
# any quality of protection (qop) above 'auth'. The challenge input as
# well as the output is Base64-encoded.

# TODO: handle UTF-8 chars in username, realm and password. For now, stick
# to ascii

import sys
import base64
import random
import logging
from binascii import hexlify

def rand_str():
	s = ""
	for i in range(12):
		s = s + chr(random.randint(0,0xff))
	return base64.encodestring(s)[0:-1]

def md5(indata):
	try:
		import hashlib
		md5 = hashlib.md5(indata)
	except ImportError:
		import md5
		md5 = md5.new(indata)
	return md5.digest()

def resp(username, realm, password, nonce, cnonce, digest_uri):
	"constructs a response string as defined in 2.1.2.1"
	urp = md5("%s:%s:%s" % (username,realm,password))
	a1 = "%s:%s:%s" % (urp, nonce, cnonce)
	a2 = "AUTHENTICATE:%s" % digest_uri
	return hexlify(md5("%s:%s:00000001:%s:auth:%s"
		 % (hexlify(md5(a1)), nonce, cnonce, hexlify(md5(a2)))))

def decode_challenge(challenge):
        s = base64.decodestring(challenge)
        elements = s.split(',')
        result = {}
        for e in elements:
                off = e.index('=')
                v = e[off + 1:].strip()
                if v[0] == '"':
                        v = v[1:-1]
                result[e[:off].strip()] = v
        return result

def generate_response(digest_uri, realm, username, password, challenge):
    c = decode_challenge(challenge)
    realmPair = ',realm="%s"' % realm
    cnonce = rand_str()
    nonce = c['nonce']
    s = resp(username, realm, password, nonce, cnonce, digest_uri)
    res = 'username="%s"%s,nonce="%s",cnonce="%s",''nc=00000001,qop=auth,digest-uri="%s",response=%s' % \
    (username, realmPair, nonce, cnonce, digest_uri, s)
    logging.info(res)
    return base64.encodestring(res)[:-1]

def makeresp(uri, realm, user, password, challenge):
    return generate_response(uri, realm, user, password, challenge)
