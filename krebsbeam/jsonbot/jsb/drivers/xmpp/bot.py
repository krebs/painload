# jsb/socklib/xmpp/bot.py
#
#

""" jabber bot definition """

## jsb imports

from jsb.lib.errors import CannotAuth
from jsb.lib.users import users
from jsb.utils.exception import handle_exception
from jsb.utils.trace import whichmodule
from jsb.utils.locking import lockdec
from jsb.utils.pdod import Pdod
from jsb.utils.dol import Dol
from jsb.utils.generic import stripcolor, toenc, fromenc, stripped
from jsb.lib.less import Less
from jsb.lib.callbacks import callbacks, remote_callbacks
from jsb.lib.threads import start_new_thread
from jsb.lib.botbase import BotBase
from jsb.lib.exit import globalshutdown
from jsb.lib.channelbase import ChannelBase
from jsb.lib.fleet import getfleet
from jsb.contrib.digestmd5 import makeresp

## jsb.socket imports

from jsb.utils.generic import waitforqueue, jabberstrip, getrandomnick, toenc, fromenc

## xmpp imports

from jsb.contrib.xmlstream import XMLescape, XMLunescape
from presence import Presence
from message import Message
from iq import Iq
from core import XMLStream
from jid import JID, InvalidJID
from errors import xmpperrors

## basic imports

import copy
import time
import Queue
import os
import threading
import thread
import types
import xml
import re
import hashlib
import logging
import cgi
import base64
import random
from hashlib import md5

## defines

cpy = copy.deepcopy


## locks

outlock = thread.allocate_lock()
inlock = thread.allocate_lock()
connectlock = thread.allocate_lock()
outlocked = lockdec(outlock)
inlocked = lockdec(inlock)
connectlocked = lockdec(connectlock)

## SXMPPBot class

class SXMPPBot(XMLStream, BotBase):

    """
        xmpp bot class.

    """

    def __init__(self, cfg=None, usersin=None, plugs=None, jid=None, *args, **kwargs):
        BotBase.__init__(self, cfg, usersin, plugs, jid, *args, **kwargs)
        if not self.cfg: raise Exception("sxmpp - config is not set.")
        if not self.cfg.user: raise Exception("sxmpp - user is not set.")
        try: self.cfg.username, self.cfg.host = self.cfg.user.split('@')
        except (ValueError, TypeError): raise Exception("%s - user not set - %s" % (self.cfg.name, str(self.cfg)))
        XMLStream.__init__(self, self.cfg.name)   
        self.type = 'sxmpp'
        self.sock = None
        self.lastin = None
        self.test = 0
        self.connecttime = 0
        self.connection = None
        self.jabber = True
        self.jids = {}
        self.topics = {}
        self.timejoined = {}
        self.channels409 = []
        if self.state and not self.state.data.ratelimit: self.state.data.ratelimit = 0.02
        try: self.cfg.port = int(self.cfg.port)
        except (ValueError, TypeError): self.cfg.port = 5222
        logging.warn("%s - user is %s" % (self.cfg.name, self.cfg.user))
        
    def _resumedata(self):
        """ return data needed for resuming. """
        return {self.cfg.name: {
            'name': self.cfg.name,
            'type': self.type,
            'nick': self.cfg.nick,
            'server': self.cfg.server,
            'port': self.cfg.port,
            'password': self.cfg.password,
            'ipv6': self.cfg.ipv6,
            'user': self.cfg.user
            }}

    def _keepalive(self):
        """ keepalive method .. send empty string to self every 3 minutes. """
        nrsec = 0
        self.sendpresence()
        while not self.stopped:
            time.sleep(1)
            nrsec += 1
            if nrsec < 180: continue
            else: nrsec = 0
            self.sendpresence()

    def sendpresence(self):
        """ send presence based on status and status text set by user. """
        if self.state:
            if self.state.has_key('status') and self.state['status']: status = self.state['status']
            else: status = ""
            if self.state.has_key('show') and self.state['show']: show = self.state['show']
            else: show = ""
        else:
            status = ""
            show = ""
        logging.debug('%s - keepalive - %s - %s' % (self.cfg.name, show, status))
        if show and status: p = Presence({'to': self.cfg.user, 'show': show, 'status': status})
        elif show: p = Presence({'to': self.cfg.user, 'show': show })
        elif status: p = Presence({'to': self.cfg.user, 'status': status})
        else: p = Presence({'to': self.cfg.user })
        self.send(p)

    def _keepchannelsalive(self):
        """ channels keep alive method. """
        nrsec = 0
        p = Presence({'to': self.cfg.user, 'txt': '' })
        while not self.stopped:
            time.sleep(1)
            nrsec += 1
            if nrsec < 600: continue
            else: nrsec = 0
            for chan in self.state['joinedchannels']:
                if chan not in self.channels409:
                    p = Presence({'to': chan})
                    self.send(p)

    def connect(self, reconnect=False):
        """ connect the xmpp server. """
        if not XMLStream.doconnect(self): return False
        iq = self.makeready()
        if not iq:
            logging.error('%s - connect to %s:%s (%s) failed' % (self.cfg.name, self.cfg.host, self.cfg.port, self.cfg.server))
            return
        self.logon(self.cfg.user, self.cfg.password, iq)
        self._raw("<presence/>")
        start_new_thread(self._keepalive, ())
        if self.cfg.keepchannelsalive: start_new_thread(self._keepchannelsalive, ())
        if self.cfg.doroster: self.requestroster()
        self.connectok.set()
        self.sock.settimeout(None)
        return True

    def logon(self, user, password, iq):
        """ logon on the xmpp server. """
        try: self.auth(user, password, iq)
        except CannotAuth:
            logging.warn("%s - sleeping 20 seconds before register" % self.cfg.name)
            time.sleep(20)
            self.failure = ""
            self.stopped = False
            try: self.register(user, password)
            except Exception, ex: self.exit() ; raise
            time.sleep(5)
            iq = self.auth_sasl(user, password, iq, False)
            #self.auth(user, password, iq)
        XMLStream.logon(self)
 
    def register(self, jid, password):
        """ register the jid to the server. """
        try: resource = jid.split("/")[1]
        except IndexError: resource = "jsb"
        logging.warn('%s - registering %s' % (self.cfg.name, jid))
        iq = self.waiter("""<iq type='get'><query xmlns='jabber:iq:register'/></iq>""")
        if not iq:
            logging.error("%s - unable to register" % self.cfg.name)
            return
        iq = self.waiter("""<iq type='set'><query xmlns='jabber:iq:register'><username>%s</username><resource>%s</resource><password>%s</password></query></iq>""" % (jid.split('@')[0], resource, password))
        if iq.error:
            logging.warn('%s - register FAILED - %s' % (self.cfg.name, iq.error))
            if not iq.error.code: logging.error("%s - can't determine error code" % self.cfg.name) ; return False
            if iq.error.code == "405": logging.error("%s - this server doesn't allow registration by the bot, you need to create an account for it yourself" % self.cfg.name)
            elif iq.error.code == "500": logging.error("%s - %s - %s" % (self.cfg.name, iq.error.code, iq.error.text))
            else: logging.error("%s - %s" % (self.cfg.name, xmpperrors[iq.error.code]))
            self.error = iq.error
            raise Exception(iq.error)
        logging.warn('%s - register ok' % self.cfg.name)
        return True

    def requestroster(self):
        """ request roster from xmpp server. """
        self._raw("<iq type='get'><query xmlns='jabber:iq:roster'/></iq>")

    def disconnectHandler(self, ex):
        """ disconnect handler. """
        self.reconnect()

    def outnocb(self, printto, txt, how=None, event=None, html=False, isrelayed=False, *args, **kwargs):
        """ output txt to bot. """
        if printto and printto in self.state['joinedchannels']: outtype = 'groupchat'
        else: outtype = "chat"
        target = printto
        if not html: 
            txt = self.normalize(txt)
        repl = Message(event)
        repl.to = target
        repl.type = outtype
        repl.txt = txt
        if html:
            repl.html = txt
        logging.debug("%s - reply is %s" % (self.cfg.name, repl.dump()))
        if not repl.type: repl.type = 'normal'
        logging.debug("%s - sxmpp - out - %s - %s" % (self.cfg.name, printto, unicode(txt)))
        self.send(repl)

    def broadcast(self, txt):
        """ broadcast txt to all joined channels. """
        for i in self.state['joinedchannels']:
            self.say(i, txt)

    def handle_iq(self, data):
        """ iq handler .. overload this when needed. """
        pass

    def handle_message(self, data):
        """ message handler. """
        m = Message(data)
        m.parse(self)
        if data.type == 'groupchat' and data.subject:
            logging.debug("%s - checking topic" % self.cfg.name)
            self.topiccheck(m)
            nm = Message(m)
            callbacks.check(self, nm)
            return
        if data.get('x').xmlns == 'jabber:x:delay':
            logging.debug("%s - ignoring delayed message" % self.cfg.name)
            return
        if m.isresponse:
            logging.debug("%s - message is a response" % self.cfg.name)
            return
        jid = None
        m.origjid = m.jid
        for node in m.subelements:
            try: m.jid = node.x.item.jid 
            except (AttributeError, TypeError): continue
        if self.cfg.user in m.fromm or (m.groupchat and self.cfg.nick == m.nick):
            logging.debug("%s - message to self .. ignoring" % self.cfg.name)
            return 0
        if self.cfg.fulljids:
            utarget = self.userhosts.get(m.nick) 
            if utarget: m.userhost = m.jid = m.auth = stripped(utarget)
            else: m.userhost = m.jid
        logging.warn("using %s as userhost" % m.userhost)
        try:
            if m.type == 'error':
                if m.code:
                    logging.error('%s - error - %s' % (self.cfg.name, str(m)))
                self.errorHandler(m)
        except Exception, ex:
            handle_exception()
        self.put(m)

    def errorHandler(self, event):
        """ error handler .. calls the errorhandler set in the event. """
        try:
            logging.error("%s - error occured in %s - %s" % (self.cfg.name, event.txt, event.userhost))
            event.errorHandler()
        except AttributeError: logging.error('%s - unhandled error - %s' % (self.cfg.name, event.dump()))

    def handle_presence(self, data):
        """ presence handler. """
        p = Presence(data)
        p.parse()
        frm = p.fromm
        nickk = ""
        nick = p.nick
        if self.cfg.user in p.userhost: return 0
        if nick: 
            self.userhosts[nick] = stripped(frm)
            nickk = nick
        jid = None
        for node in p.subelements:
            try:
                jid = node.x.item.jid 
            except (AttributeError, TypeError):
                continue
        if nickk and jid and self.cfg.fulljids:
            channel = p.channel
            if not self.jids.has_key(channel):
                self.jids[channel] = {}
            self.jids[channel][nickk] = jid
            self.userhosts[nickk] = stripped(jid)
            logging.warn('%s - setting jid of %s (%s) to %s' % (self.cfg.name, nickk, channel, self.userhosts[nickk]))
        if p.type == 'subscribe':
            pres = Presence({'to': p.fromm, 'type': 'subscribed'})
            self.send(pres)
            pres = Presence({'to': p.fromm, 'type': 'subscribe'})
            self.send(pres)
        nick = p.resource
        if p.type != 'unavailable':
            p.joined = True
            p.type = 'available'
        elif self.cfg.user in p.userhost:
            try:
                del self.jids[p.channel]
                logging.debug('%s - removed %s channel jids' % (self.cfg.name, p.channel))
            except KeyError:
                pass
        else:
            try:
                del self.jids[p.channel][p.nick]
                logging.debug('%s - removed %s jid' % (self.cfg.name, p.nick))
            except KeyError:
                pass
        if p.type == 'error':
            for node in p.subelements:
                try:
                    err = node.error.code
                except (AttributeError, TypeError):
                    err = 'no error set'
                try:
                    txt = node.text.data
                except (AttributeError, TypeError):
                    txt = ""
            if err:
                logging.error('%s - error - %s - %s'  % (self.cfg.name, err, txt))
            try:
                method = getattr(self,'handle_' + err)
                try:
                    method(p)
                except:
                    handle_exception()
            except AttributeError:
                pass
        self.doevent(p)

    def invite(self, jid):
        pres = Presence({'to': jid, 'type': 'subscribe'})
        self.send(pres)
        time.sleep(2)
        pres = Presence({'to': jid})
        self.send(pres)

    def send(self, what):
        """ send stanza to the server. """
        if not what:
            logging.debug("%s - can't send empty message" % self.cfg.name)
            return
        try:
            to = what['to']
        except (KeyError, TypeError):
            logging.error("%s - can't determine where to send %s to" % (self.cfg.name, str(what)))
            return
        try:
            jid = JID(to)
        except (InvalidJID, AttributeError):
            logging.error("%s - invalid jid - %s - %s" % (self.cfg.name, str(to), whichmodule(2)))
            return
        try: del what['from']
        except KeyError: pass
        try:
            xml = what.tojabber()
            if not xml:
                raise Exception("can't convert %s to xml .. bot.send()" % what) 
        except (AttributeError, TypeError):
            handle_exception()
            return
        if not self.checkifvalid(xml): logging.error("%s - NOT PROPER XML - %s" % (self.cfg.name, xml))
        else: self._raw(xml)
           
    def action(self, printto, txt, fromm=None, groupchat=True, event=None, *args, **kwargs):
        """ send an action. """
        txt = "/me " + txt
        if self.google:
            fromm = self.cfg.user
        if printto in self.state['joinedchannels'] and groupchat:
            message = Message({'to': printto, 'txt': txt, 'type': 'groupchat'})
        else: message = Message({'to': printto, 'txt': txt})
        if fromm: message.fromm = fromm
        self.send(message)
        
    def save(self):
        """ save bot's state. """
        if self.state:
            self.state.save()

    def quit(self):
        """ send unavailable presence. """
        if self.error: return
        presence = Presence({'type': 'unavailable' ,'to': self.cfg.user})
        if self.state:
            for i in self.state.data.joinedchannels:
                presence.to = i
                self.send(presence)
        presence = Presence({'type': 'unavailable', 'to': self.cfg.user})
        presence['from'] = self.cfg.user
        self.send(presence)

    def setstatus(self, status, show=""):
        """ send status presence. """
        if self.error: return
        if self.state:
            self.state['status'] = status
            self.state['show'] = show
            self.state.save()
        presence = Presence({'status': status, 'show': show ,'to': self.cfg.user})
        self.send(presence)

    def shutdown(self):
        self.outqueue.put_nowait(None)

    def join(self, channel, password=None, nick=None):
        """ join conference. """
        if channel.startswith("#"): return
        try:
            if not nick: nick = channel.split('/')[1]
        except IndexError: nick = self.cfg.nick or "jsonbot"
        channel = channel.split('/')[0]
        q = Queue.Queue()
        presence = Presence({'to': channel + '/' + nick})
        if password:
             presence.x.password = password             
        self.send(presence)
        self.timejoined[channel] = time.time()
        chan = ChannelBase(channel, self.botname)
        chan.data['nick'] = nick
        if password:
            chan.data['key'] = password
        if not chan.data.has_key('cc'):
            chan.data['cc'] = self.cfg['defaultcc'] or '!'
        if channel not in self.state['joinedchannels']:
            self.state['joinedchannels'].append(channel)
            self.state.save()
        if channel in self.channels409:
            self.channels409.remove(channel)
        chan.save()
        return 1

    def part(self, channel):
        """ leave conference. """
        if channel.startswith("#"): return
        presence = Presence({'to': channel})
        presence.type = 'unavailable'
        self.send(presence)
        if channel in self.state['joinedchannels']: self.state['joinedchannels'].remove(channel)
        self.state.save()
        return 1

    def outputnolog(self, printto, what, how, who=None, fromm=None):
        """ do output but don't log it. """
        if fromm: return
        self.saynocb(printto, what)

    def topiccheck(self, msg):
        """ check if topic is set. """
        if msg.groupchat:
            try:
                topic = msg.subject
                if not topic: return None
                self.topics[msg.channel] = (topic, msg.userhost, time.time())
                logging.debug('%s - topic of %s set to %s' % (self.cfg.name, msg.channel, topic))
            except AttributeError: return None

    def settopic(self, channel, txt):
        """ set topic. """
        pres = Message({'to': channel, 'subject': txt})
        pres.type = 'groupchat'
        self.send(pres)

    def gettopic(self, channel):
        """ get topic. """
        try:
            topic = self.topics[channel]
            return topic
        except KeyError: return None

    def domsg(self, msg):
        """ dispatch an msg on the bot. """
        self.put(msg)

    def normalize(self, what):
        #what = cgi.escape(what)
        what = stripcolor(what)
        what = what.replace("\002", "")
        what = what.replace("\003", "")
        what = what.replace("<br>", "\n")
        what = what.replace("<li>", "*")
        what = what.replace("</li>", "")
        what = what.replace("<b>", "")
        what = what.replace("</b>", "")
        what = what.replace("&lt;b&gt;", "")
        what = what.replace("&lt;/b&gt;", "")
        what = what.replace("<i>", "")
        what = what.replace("</i>", "")
        what = what.replace("&lt;i&gt;", "")
        what = what.replace("&lt;/i&gt;", "")
        return what

    def doreconnect(self):
        """ reconnect to the server. """
        cfg = cpy(self.cfg)
        botjid = cfg.user
        newbot = getfleet().makebot('sxmpp', cfg.name, config=cfg, showerror=True)
        if not newbot: raise Exception("can't make bot %s with config %s" % (self.cfg.name, self.cfg.tojson()))
        newbot.reconnectcount = self.reconnectcount
        newbot.start()
        newbot.joinchannels()
        getfleet().replace(botjid, newbot)
        return True

