# gozerbot/socket/xmpp/presence.py
#
#

""" Iq. """

## jsb imports

from jsb.lib.eventbase import EventBase
from jsb.utils.trace import whichmodule
from jsb.lib.gozerevent import GozerEvent

## basic imports

import logging
import time

## Iq class
 
class Iq(GozerEvent):

    def __init__(self, nodedict={}):
        GozerEvent.__init__(self, nodedict)
        self.element = "iq"
        self.jabber = True
        self.cmnd = "IQ"
        self.cbtype = "IQ"
        self.bottype = "xmpp"
 
    def parse(self):
        """ set ircevent compatible attributes """
        self.cmnd = 'Iq'
        self.conn = None
        self.arguments = []
        try: self.nick = self.fromm.split('/')[1]
        except (AttributeError, IndexError): pass
        self.jid = self.jid or self.fromm
        self.ruserhost = self.jid
        self.userhost = str(self.jid)
        self.resource = self.nick
        self.stripped = self.jid.split('/')[0]
        self.channel = self.fromm.split('/')[0]
        self.printto = self.channel
        self.origtxt = self.txt
        self.time = time.time()
        self.msg = None
        self.rest = ' '.join(self.args)
        self.sock = None
        self.speed = 5
        if self.type == 'groupchat': self.groupchat = True
        else: self.groupchat = False
        if self.txt:makeargrest(self)
        self.joined = False
        self.denied = False
