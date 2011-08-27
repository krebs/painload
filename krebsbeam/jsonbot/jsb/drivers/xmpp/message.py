# jsb/socklib/xmpp/message.py
#
#

""" jabber message definition .. types can be normal, chat, groupchat, 
    headline or  error
"""

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.utils.trace import whichmodule
from jsb.utils.generic import toenc, fromenc, jabberstrip
from jsb.utils.locking import lockdec
from jsb.lib.eventbase import EventBase
from jsb.lib.errors import BotNotSetInEvent
from jsb.lib.gozerevent import GozerEvent

## xmpp import

from jsb.contrib.xmlstream import NodeBuilder, XMLescape, XMLunescape

## basic imports

import types
import time
import thread
import logging
import re

## locks

replylock = thread.allocate_lock()
replylocked = lockdec(replylock)

## classes

class Message(GozerEvent):

    """ jabber message object. """

    def __init__(self, nodedict={}):
        self.element = "message"
        self.jabber = True
        self.cmnd = "MESSAGE"
        self.cbtype = "MESSAGE"
        self.bottype = "xmpp"
        self.type = "normal"
        GozerEvent.__init__(self, nodedict)
  
    def __copy__(self):
        return Message(self)

    def __deepcopy__(self, bla):
        m = Message()
        m.copyin(self)
        return m

    def parse(self, bot=None):
        """ set ircevent compat attributes. """
        self.bot = bot
        self.jidchange = False
        #self.cmnd = 'MESSAGE'
        try: self.resource = self.fromm.split('/')[1]
        except IndexError: pass
        self.channel = self['fromm'].split('/')[0]
        self.origchannel = self.channel
        self.nick = self.resource
        self.jid = self.fromm
        self.ruserhost = self.jid
        self.userhost = self.jid
        self.stripped = self.jid.split('/')[0]
        self.printto = self.channel
        for node in self.subelements:
            try:
                self.txt = node.body.data
                break
            except (AttributeError, ValueError):
                continue
        if self.txt: self.usercmnd = self.txt.split()[0]
        else: self.usercmnd = ""
        self.origtxt = self.txt
        self.time = time.time()
        if self.type == 'groupchat':
            self.groupchat = True
            self.auth = self.userhost
        else:
            self.groupchat = False
            self.auth = self.stripped
            self.nick = self.jid.split("@")[0]
        self.msg = not self.groupchat
        self.makeargs()

    def errorHandler(self):
        """ dispatch errors to their handlers. """
        try:
            code = self.get('error').code
        except Exception, ex:
            handle_exception()
        try:
            method = getattr(self, "handle_%s" % code)
            if method:
                logging.error('sxmpp.core - dispatching error to handler %s' % str(method))
                method(self)
        except AttributeError, ex: logging.error('sxmpp.core - unhandled error %s' % code)
        except: handle_exception()

    def normalize(self, what):
        return self.bot.normalize(what)
