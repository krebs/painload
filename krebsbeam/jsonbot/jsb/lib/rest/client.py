# jsb/rest/client.py
#
#

""" Rest Client class """

## jsb imports

from jsb.utils.url import geturl4, posturl, deleteurl, useragent
from jsb.utils.generic import toenc
from jsb.utils.exception import handle_exception, exceptionmsg
from jsb.utils.locking import lockdec
from jsb.utils.lazydict import LazyDict
from jsb.imports import getjson
json = getjson()

## basic imports

from urllib2 import HTTPError, URLError
from httplib import InvalidURL
from urlparse import urlparse
import socket
import asynchat
import urllib
import sys
import thread
import re
import asyncore
import time
import logging

## defines

restlock = thread.allocate_lock()
locked = lockdec(restlock)

## RestResult class

class RestResult(LazyDict):

    def __init__(self, url="", name=""):
        LazyDict.__init__(self)
        self.url = url
        self.name = name
        self.data = None
        self.error = None
        self.status = None
        self.reason = ""

## RestClient class

class RestClient(object):

    """ Provide a REST client that works in sync mode. """

    def __init__(self, url, keyfile=None, certfile=None, port=None):
        if not url.endswith('/'): url += '/'
        try:
            u = urlparse(url)
            splitted = u[1].split(':')
            if len(splitted) == 2: host, port = splitted
            else:
                host = splitted[0]
                port = port or 9999
            path = u[2]
        except Exception, ex: raise
        self.host = host 
        try: self.ip = socket.gethostbyname(self.host)
        except Exception, ex: handle_exception()
        self.path = path
        self.port = port
        self.url = url
        self.keyfile = keyfile
        self.certfile = certfile
        self.callbacks = []

    def addcb(self, callback): 
        """ add a callback. """
        if not callback: return
        self.callbacks.append(callback)
        logging.debug('rest.client - added callback %s' % str(callback))
        return self

    def delcb(self, callback):
        """ delete callback. """
        try:
            del self.callbacks[callback]
            logging.debug('rest.client - deleted callback %s' % str(callback))
        except ValueError: pass
        
    def do(self, func, url, *args, **kwargs):
        """ perform a rest request. """
        result = RestResult(url)
        try:
            logging.info("rest.client - %s - calling %s" % (url, str(func)))
            res = func(url, {}, kwargs, self.keyfile, self.certfile, self.port)
            result.status = res.status
            result.reason = res.reason
            if result.status >= 400: result.error = result.status
            else: result.error = None
            if result.status == 200:
                r = res.read()
                result.data = json.loads(r)
            else: result.data = None
            logging.info("rest.client - %s - result: %s" % (url, str(result))) 
        except Exception, ex:
            result.error = str(ex)
            result.data = None
        for cb in self.callbacks:
            try:
                cb(self, result)
                logging.info('rest.client - %s - called callback %s' % (url, str(cb)))
            except Exception, ex:
                handle_exception()
        return result

    def post(self, *args, **kwargs):
        """ do a POST request. """
        return self.do(posturl, self.url, *args, **kwargs)

    def add(self, *args, **kwargs):
        """ add an REST item. """
        return self.do(posturl, self.url, *args, **kwargs)

    def delete(self, nr=None):
        """ delete a REST item. """
        if nr: return self.do(deleteurl, self.url + '/' + str(nr))
        else: return self.do(deleteurl, self.url)

    def get(self, nr=None):
        """ get a REST item. """
        if not nr: return self.do(geturl4, self.url)
        else: return self.do(geturl4, self.url + '/' + str(nr))

## RestClientAsync class

class RestClientAsync(RestClient, asynchat.async_chat):

    """ Async REST client. """

    def __init__(self, url, name=""):
        RestClient.__init__(self, url)
        asynchat.async_chat.__init__(self)
        self.set_terminator("\r\n\r\n")
        self.reading_headers = True
        self.error = None
        self.buffer = ''
        self.name = name or self.url
        self.headers = {}
        self.status = None

    def handle_error(self):
        """ take care of errors. """
        exctype, excvalue, tb = sys.exc_info()
        if exctype == socket.error:
            try:
                errno, errtxt = excvalue
                if errno in [11, 35, 9]:
                    logging.error("res.client - %s - %s %s" % (self.url, errno, errtxt))
                    return
            except ValueError: pass
            self.error = str(excvalue)
        else:
            logging.error("%s - %s" % (self.name, exceptionmsg()))
            self.error = exceptionmsg()
        self.buffer = ''
        result = RestResult(self.url, self.name)
        result.error = self.error
        result.data = None
        for cb in self.callbacks:
            try:
                cb(self, result)
                logging.info('rest.client - %s - called callback %s' % (url, str(cb)))
            except Exception, ex: handle_exception()
        self.close()

    def handle_expt(self):
        """ handle an exception. """
        handle_exception()

    def handle_connect(self):
        """ called after succesfull connect. """
        logging.info('rest.client - %s - connected %s' % (self.url, str(self)))
         
    def start(self):
        """ start the client loop. """
        assert(self.host)
        assert(int(self.port))
        try:
            logging.info('rest.client - %s - starting client' % self.url)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect((self.ip, int(self.port)))
        except socket.error, ex:
            self.error = str(ex)
            try:
                self.connect((self.ip, int(self.port)))
            except socket.error, ex: self.error = str(ex)
        except Exception, ex: self.error = str(ex)
        if self.error: self.warn("rest.client - %s - can't start %s" % (self.url, self.error))
        else: return True

    @locked
    def found_terminator(self):
        """ called when terminator is found. """
        logging.info('rest.client - %s - found terminator' % self.url)
        if self.reading_headers:
            self.reading_headers = False
            try:
                self.headers = self.buffer.split('\r\n')
                self.status = int(self.headers[0].split()[1])
            except (ValueError, IndexError):
                logging.warn("rest.client - %s - can't parse headers %s" % (self.url, self.headers))
                return
            self.set_terminator(None)
            self.buffer = ''
            logging.info('rest.client - %s - headers: %s' % (self.url, self.headers))

    def collect_incoming_data(self, data):
        """ aggregate seperate data chunks. """
        self.buffer = self.buffer + data

    def handle_close(self):
        """ called on connection close. """
        self.reading_headers = False
        self.handle_incoming()
        logging.info('rest.client - %s - closed' % self.url)
        self.close()
      
    def handle_incoming(self): 
        """ handle incoming data. """
        logging.info("rest.client - %s - incoming: %s" % (self.url, self.buffer))
        if not self.reading_headers:
            result = RestResult(self.url, self.name)
            if self.status >= 400:
                logging.warn('rest.client - %s - error status: %s' % (self.url, self.status))
                result.error = self.status
                result.data = None
            elif self.error:
                result.error = self.error
                result.data = None
            elif self.buffer == "":
                result.data = ""
                result.error = None
            else:
                try:
                    res = json.loads(self.buffer)
                    if not res:
                        self.buffer = ''
                        return
                    result.data = res
                    result.error = None
                except ValueError, ex:
                    logging.info("rest.client - %s - can't decode %s" % (self.url, self.buffer))
                    result.error = str(ex)
                except Exception, ex:
                    logging.error("rest.client - %s - %s" % (self.url, exceptionmsg()))
                    result.error = exceptionmsg()                
                    result.data = None
            for cb in self.callbacks:
                try:
                    cb(self, result)
                    logging.info('rest.client - %s - called callback %s' % (self.url, str(cb)))
                except Exception, ex: handle_exception()
            self.buffer = ''

    @locked
    def dorequest(self, method, path, postdata={}, headers={}):
        if postdata: postdata = urllib.urlencode(postdata)
        if headers:
            if not headers.has_key('Content-Length'): headers['Content-Length'] = len(postdata)
            headerstxt = ""
            for i,j in headers.iteritems(): headerstxt += "%s: %s\r\n" % (i.lower(), j)
        else: headerstxt = ""
        if method == 'POST': s = toenc("%s %s HTTP/1.0\r\n%s\r\n%s\r\n\r\n" % (method, path, headerstxt, postdata), 'ascii')
        else: s = toenc("%s %s HTTP/1.0\r\n\r\n" % (method, path), 'ascii')
        if self.start():
            logging.info('rest.client - %s - sending %s' % (self.url, s))
            self.push(s)

    def sendpost(self, postdata):
        headers = {'Content-Type': 'application/x-www-form-urlencoded', \
'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
        self.dorequest('POST', self.path, postdata, headers)

    def sendget(self):
        """ send a GET request. """
        self.dorequest('GET', self.path)

    def post(self, *args, **kwargs):
        """ do a POST request. """
        self.sendpost(kwargs)

    def get(self):
        """ call GET request. """
        self.sendget()
