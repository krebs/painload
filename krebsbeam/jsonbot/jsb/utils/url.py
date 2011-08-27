# jsb/utils/url.py
#
# most code taken from maze

""" url related functions. """

## jsb imports

from generic import fromenc, toenc

## basic imports

import logging
import time
import sys
import re
import traceback
import Queue
import urllib
import urllib2
import urlparse
import socket
import random
import os
import sgmllib
import thread
import types
import httplib
import StringIO
import htmlentitydefs
import tempfile
import cgi
import urllib

## defines

re_url_match  = re.compile(u'((?:http|https)://\S+)')

try: import chardet
except ImportError: chardet = None

class istr(str):
    pass

## useragent function

def useragent():
    """ provide useragent string """
    from jsb.version import version
    (name, version) = version.split()[0:2]
    return 'Mozilla/5.0 (compatible; %s %s; http://jsonbot.appspot.com)' % (name, version)

## CBURLopener class

class CBURLopener(urllib.FancyURLopener):
    """ our URLOpener """
    def __init__(self, version, *args):
        if version: self.version = version
        else: self.version = useragent()
        urllib.FancyURLopener.__init__(self, *args)

## geturl function

def geturl(url, version=None):
    """ fetch an url. """
    urllib._urlopener = CBURLopener(version)
    logging.warn('fetching %s' % url)
    result = urllib.urlopen(url)
    tmp = result.read()
    result.close()
    return tmp

## geturl2 function

def geturl2(url, decode=False):
    """ use urllib2 to fetch an url. """
    logging.warn('fetching %s' % url)
    request = urllib2.Request(url)
    request.add_header('User-Agent', useragent())
    opener = urllib2.build_opener()
    result = opener.open(request)
    tmp = result.read()
    info = result.info()
    result.close()
    if decode:
        encoding = get_encoding(tmp)
        logging.info('%s encoding: %s' % (url, encoding))
        res = istr(fromenc(tmp, encoding, url))
    else: res = istr(tmp)
    res.info = info
    return res

## geturl4 function

def geturl4(url, myheaders={}, postdata={}, keyfile="", certfile="", port=80):
    """ use httplib to fetch an url. """
    headers = {'Content-Type': 'text/html', 'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
    headers.update(myheaders)
    urlparts = urlparse.urlparse(url)
    try:
       port = int(urlparts[1].split(':')[1])
       host = urlparts[1].split(':')[0]
    except: host = urlparts[1]
    if keyfile: connection = httplib.HTTPSConnection(host, port, keyfile, certfile)
    elif 'https' in urlparts[0]: connection = httplib.HTTPSConnection(host, port)
    else: connection = httplib.HTTPConnection(host, port)
    if type(postdata) == types.DictType: postdata = urllib.urlencode(postdata)
    logging.warn('fetching %s' % url)
    connection.request('GET', urlparts[2])
    return connection.getresponse()


## posturl function

def posturl(url, myheaders, postdata, keyfile=None, certfile="",port=80):
    """ very basic HTTP POST url retriever. """
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
    headers.update(myheaders)
    urlparts = urlparse.urlparse(url)
    if keyfile: connection = httplib.HTTPSConnection(urlparts[1], port, keyfile, certfile)
    else: connection = httplib.HTTPConnection(urlparts[1])
    if type(postdata) == types.DictType: postdata = urllib.urlencode(postdata)
    logging.warn('post %s' % url)
    connection.request('POST', urlparts[2], postdata, headers)
    return connection.getresponse()

## delete url function

def deleteurl(url, myheaders={}, postdata={}, keyfile="", certfile="", port=80):
    """ very basic HTTP DELETE. """
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
    headers.update(myheaders)
    urlparts = urlparse.urlparse(url)
    if keyfile and certfile: connection = httplib.HTTPSConnection(urlparts[1], port, keyfile, certfile)
    else: connection = httplib.HTTPConnection(urlparts[1])
    if type(postdata) == types.DictType: postdata = urllib.urlencode(postdata)
    logging.info('delete %s' % url)
    connection.request('DELETE', urlparts[2], postdata, headers)
    return connection.getresponse()

## put url function

def puturl(url, myheaders={}, postdata={}, keyfile="", certfile="", port=80):
    """ very basic HTTP PUT. """
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
    headers.update(myheaders)
    urlparts = urlparse.urlparse(url)
    if keyfile: connection = httplib.HTTPSConnection(urlparts[1], port, keyfile, certfile)
    else: connection = httplib.HTTPConnection(urlparts[1])
    if type(postdata) == types.DictType: postdata = urllib.urlencode(postdata)
    logging.info('put %s' % url)
    connection.request('PUT', urlparts[2], postdata, headers)
    return connection.getresponse()

## getpostdata function

def getpostdata(event):
    """ retrive post data from url data. """
    try:
        ctype, pdict = cgi.parse_header(event.headers.getheader('content-type'))
    except AttributeError: ctype, pdict = cgi.parse_header(event.headers.get('content-type'))
    body = cgi.FieldStorage(fp=event.rfile, headers=event.headers, environ = {'REQUEST_METHOD':'POST'}, keep_blank_values = 1)
    result = {}
    for name in dict(body): result[name] = body.getfirst(name)
    return result

## getpostdata function

def getpostdata_gae(request):
    """ retrive post data from url data. """
    #try:
    #    ctype, pdict = cgi.parse_header(request.headers.getheader('content-type'))
    #except AttributeError: ctype, pdict = cgi.parse_header(request.headers.get('content-type'))
    #body = cgi.FieldStorage(headers=request.headers, environ = {'REQUEST_METHOD':'POST'}, keep_blank_values = 1)
    return urllib.unquote_plus(request.body[:-1].strip())
    #result = {}
    #for name in dict(body): result[name] = body.getfirst(name)
    #return result

## decode_html_entities function

def decode_html_entities(s):
    """ smart decoding of html entities to utf-8 """
    re_ent_match = re.compile(u'&([^;]+);')
    re_entn_match = re.compile(u'&#([^;]+);')
    s = s.decode('utf-8', 'replace')

    def to_entn(match):
        """ convert to entities """
        if htmlentitydefs.entitydefs.has_key(match.group(1)):
            return htmlentitydefs.entitydefs[match.group(1)].decode('latin1', 'replace')
        return match.group(0)

    def to_utf8(match):
        """ convert to utf-8 """
        return unichr(long(match.group(1)))

    s = re_ent_match.sub(to_entn, s)
    s = re_entn_match.sub(to_utf8, s)
    return s

## get_encoding function

def get_encoding(data):
    """ get encoding from web data """
    if hasattr(data, 'info') and data.info.has_key('content-type') and 'charset' in data.info['content-type'].lower():
        charset = data.info['content-type'].lower().split('charset', 1)[1].strip()
        if charset[0] == '=':
            charset = charset[1:].strip()
            if ';' in charset: return charset.split(';')[0].strip()
            return charset
    if '<meta' in data.lower():
        metas = re.findall(u'<meta[^>]+>', data, re.I | re.M)
        if metas:
            for meta in metas:
                test_http_equiv = re.search('http-equiv\s*=\s*[\'"]([^\'"]+)[\'"]', meta, re.I)
                if test_http_equiv and test_http_equiv.group(1).lower() == 'content-type':
                    test_content = re.search('content\s*=\s*[\'"]([^\'"]+)[\'"]', meta, re.I)
                    if test_content:
                        test_charset = re.search('charset\s*=\s*([^\s\'"]+)', meta, re.I)
                        if test_charset: return test_charset.group(1)
    if chardet:
        test = chardet.detect(data)
        if test.has_key('encoding'): return test['encoding']
    return sys.getdefaultencoding()

## Stripper class

class Stripper(sgmllib.SGMLParser):

    """ html stripper. """

    def __init__(self):
        sgmllib.SGMLParser.__init__(self)

    def strip(self, some_html):
        """ strip html. """
        self.theString = u""
        self.feed(fromenc(some_html, "ascii"))
        self.close()
        return self.theString

    def handle_data(self, data):
        """ data handler. """
        self.theString += data

## striphtml function

def striphtml(txt):
    """ strip html from txt. """
    stripper = Stripper()
    txt = stripper.strip(txt)
    return txt
