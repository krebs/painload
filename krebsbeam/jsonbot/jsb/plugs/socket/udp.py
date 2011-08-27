# jsb/plugs/socket/udp.py
#
#

"""
    the bot has the capability to listen for udp packets which it will use
    to /msg a given nick or channel.

    1) setup

        * do !reload udp to enable the udp plugin
        * call !udp-cfgsave to generate a config file in gozerdata/plugs/udp/config
        * edit this file .. esp. look at the udpallowednicks list
        * run ./bin/jsb-udp -s to generate clientside config file "udp-send"
        * edit this file
        * test with:

        ::

            echo "YOOO" | ./bin/jsb-udp

    2) limiter

        on IRC the bot's /msg to a user/channel are limited to 1 per 3 seconds so the
        bot will not excessflood on the server. you can use partyudp if you need no 
        delay between sent messages, this will use dcc chat to deliver the message.
        on jabber bots there is no delay

"""

## jsb imports

from jsb.lib.fleet import getfleet
from jsb.utils.exception import handle_exception
from jsb.utils.generic import strippedtxt
from jsb.utils.locking import lockdec
from jsb.lib.partyline import partyline
from jsb.lib.threads import start_new_thread
from jsb.contrib.rijndael import rijndael
from jsb.lib.persistconfig import PersistConfig
from jsb.lib.callbacks import first_callbacks

## basic imports

import socket
import re
import time
import Queue
import logging

# defines

udplistener = None

cfg = PersistConfig()
cfg.define('udp', 0) # set to 0 to disnable
cfg.define('udpparty', 0)
cfg.define('udpipv6', 0)
cfg.define('udpmasks', ['192.168*', ])
cfg.define('udphost', "localhost")
cfg.define('udpport', 5500)
cfg.define('udpallow', ["127.0.0.1", ])
cfg.define('udpallowednicks', ["#dunkbots", "#jsb", "dunk_"])
cfg.define('udppassword', "mekker", exposed=False)
cfg.define('udpseed', "blablablablablaz", exposed=False) # needs to be 16 chars wide
cfg.define('udpstrip', 1) # strip all chars < char(32)
cfg.define('udpsleep', 0) # sleep in sendloop .. can be used to delay pack
cfg.define('udpdblog', 0)
cfg.define('udpbots', [cfg['udpbot'] or 'default-irc', ])

## functions

def _inmask(addr):
    """ check if addr matches a mask. """
    if not cfg['udpmasks']:
        return False
    for i in cfg['udpmasks']:
        i = i.replace('*', '.*')
        if re.match(i, addr):
            return True

## Udplistener class

class Udplistener(object):

    """ listen for udp messages and relay them to channel/nick/JID. """

    def __init__(self):
        self.outqueue = Queue.Queue()
        self.queue = Queue.Queue()
        self.stop = 0
        if cfg['udpipv6']: self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else: self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try: self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except: pass
        self.sock.setblocking(1)
        self.sock.settimeout(1)
        self.loggers = []

    def _outloop(self):
        """ loop controling the rate of outputted messages. """
        logging.info('udp - starting outloop')
        while not self.stop:
            (printto, txt) = self.outqueue.get()
            if self.stop: return
            self.dosay(printto, txt)
        logging.info('udp - stopping outloop')

    def _handleloop(self):
        """ handle incoming udp data. """
        while not self.stop:
            (input, addr) = self.queue.get()
            if not input or not addr: continue
            if self.stop: break                
            self.handle(input, addr)
            if cfg['udpsleep']: time.sleep(cfg['udpsleep'] or 0.01)
        logging.info('udp - shutting down udplistener')

    def _listen(self):
        """ listen for udp messages .. /msg via bot"""
        if not cfg['udp']: return
        fleet = getfleet()
        for botname in cfg['udpbots']:
            if not fleet.byname(botname): logging.info("udp - can't find %s bot" % botname)
        try:
            fleet.startok.wait(5)
            logging.warn('udp listening on %s %s' % (cfg['udphost'], cfg['udpport']))
            self.sock.bind((cfg['udphost'], cfg['udpport']))
            self.stop = 0
        except IOError:
            handle_exception()
            self.sock = None
            self.stop = 1
            return
        # loop on listening udp socket
        while not self.stop:
            try: input, addr = self.sock.recvfrom(64000)
            except socket.timeout: continue
            except Exception, ex:
                try: (errno, errstr) = ex
                except ValueError: errno = 0 ; errstr = str(ex)
                if errno == 4: logging.warn("udp - %s - %s" % (self.name, str(ex))) ; break
                if errno == 35: continue
                else: handle_exception() ; break
            if self.stop: break
            self.queue.put((input, addr))
        logging.info('udp - shutting down main loop')

    def handle(self, input, addr):
        """  handle an incoming udp packet. """
        if cfg['udpseed']:
            data = ""
            for i in range(len(input)/16):
                try: data += crypt.decrypt(input[i*16:i*16+16])
                except Exception, ex:
                    logging.warn("udp - can't decrypt: %s" % str(ex))
                    data = input
                    break
        else: data = input
        if cfg['udpstrip']: data = strippedtxt(data)
        # check if udp is enabled and source ip is in udpallow list
        if cfg['udp'] and (addr[0] in cfg['udpallow'] or _inmask(addr[0])):
            # get printto and passwd data
            header = re.search('(\S+) (\S+) (.*)', data)
            if header:
                # check password
                if header.group(1) == cfg['udppassword']:
                    printto = header.group(2)    # is the nick/channel
                    # check if printto is in allowednicks
                    if not printto in cfg['udpallowednicks']:
                        logging.warn("udp - udp denied %s" % printto )
                        return
                    logging.debug('udp - ' + str(addr[0]) +  " - udp allowed")
                    text = header.group(3)    # is the text
                    self.say(printto, text)
                else: logging.warn("udp - can't match udppasswd from " + str(addr))
            else: logging.warn("udp - can't match udp from " + str(addr[0]))
        else: logging.warn('udp - denied udp from ' + str(addr[0]))

    def say(self, printto, txt):
        """ send txt to printto. """
        self.outqueue.put((printto, txt))

    def dosay(self, printto, txt):
        """ send txt to printto .. do some checks. """
        if cfg['udpparty'] and partyline.is_on(printto): partyline.say_nick(printto, txt) ; return
        if not cfg['udpbots']: bots = [cfg['udpbot'], ]
        else: bots = cfg['udpbots']
        for botname in bots:
            bot = getfleet().byname(botname)
            if not bot: logging.warn("udp - can't find %s bot in fleet" % botname) ; continue
            bot.connectok.wait()
            bot.say(printto, txt)
            for i in self.loggers: i.log(printto, txt)

## init

# the udplistener object
if cfg['udp']: udplistener = Udplistener()

# initialize crypt object if udpseed is set in config
if cfg['udp'] and cfg['udpseed']: crypt = rijndael(cfg['udpseed'])

def init():
    """ init the udp plugin. """
    if cfg['udp']:
        global udplistener
        start_new_thread(udplistener._listen, ())
        start_new_thread(udplistener._handleloop, ())
        start_new_thread(udplistener._outloop, ())
    return 1

## shutdown

def shutdown():
    """ shutdown the udp plugin. """
    global udplistener
    if udplistener:
        udplistener.stop = 1
        udplistener.outqueue.put_nowait((None, None))
        udplistener.queue.put_nowait((None, None))
    return 1

## start

def onSTART(bot, event):
    pass

first_callbacks.add("START", onSTART)
