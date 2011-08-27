# gozerbot/ircevent.py
#
#
# http://www.irchelp.org/irchelp/rfc/rfc2812.txt

""" an ircevent is extracted from the IRC string received from the server. """

## jsb imports

from jsb.utils.generic import toenc, fromenc, strippedtxt, fix_format
from jsb.lib.eventbase import EventBase

## basic imports

import time
import re
import types
import copy
import logging

## defines

cpy = copy.deepcopy

## Ircevent class

class IrcEvent(EventBase):

    """ represents an IRC event. """

    def __deepcopy__(self, bla):
        e = IrcEvent()
        e.copyin(self)
        return e

    def parse(self, bot, rawstr):
        """ parse raw string into ircevent. """
        self.bottype = "irc"
        self.bot = bot
        self.ttl = 2
        rawstr = rawstr.rstrip()
        splitted = re.split('\s+', rawstr)
        if not rawstr[0] == ':':
            assert bot.cfg
            splitted.insert(0, u":%s!%s@%s" % (bot.cfg.nick, bot.cfg.username, bot.cfg.server))
            rawstr = u":%s!%s@%s %s" % (bot.cfg.nick, bot.cfg.username, bot.cfg.server, rawstr)
        self.prefix = splitted[0][1:]
        nickuser = self.prefix.split('!')
        try: 
            self.userhost = nickuser[1]
            self.nick = nickuser[0]
        except IndexError: self.userhost = None ; self.nick = None ; self.isservermsg = True
        self.cmnd = splitted[1]
        self.cbtype = self.cmnd
        if pfc.has_key(self.cmnd):
            self.arguments = splitted[2:pfc[self.cmnd]+2]
            txtsplit = re.split('\s+', rawstr, pfc[self.cmnd]+2)
            self.txt = txtsplit[-1]
        else:
            self.arguments = splitted[2:]
        if self.arguments: self.target = self.arguments[0]
        self.postfix = ' '.join(self.arguments)
        if self.target and self.target.startswith(':'): self.txt = ' '.join(self.arguments)
        if self.txt:
            if self.txt[0] == ":": self.txt = self.txt[1:]
            if self.txt: self.usercmnd = self.txt.split()[0]
        if self.cmnd == 'PING': self.speed = 9
        if self.cmnd == 'PRIVMSG':
            self.channel = self.arguments[0]
            if '\001' in self.txt: self.isctcp = True
        elif self.cmnd == 'JOIN' or self.cmnd == 'PART':
            if self.arguments: self.channel = self.arguments[0]
            else: self.channel = self.txt
        elif self.cmnd == 'MODE': self.channel = self.arguments[0]
        elif self.cmnd == 'TOPIC': self.channel = self.arguments[0]
        elif self.cmnd == 'KICK': self.channel = self.arguments[0]
        elif self.cmnd == '353': self.channel = self.arguments[2]
        elif self.cmnd == '324': self.channel = self.arguments[1]
        if self.userhost:
            self.ruserhost = self.userhost
            self.stripped = self.userhost
            self.auth = self.userhost
            try: self.hostname = self.userhost.split("@")[1]
            except: self.hostname = None
        self.origtxt = self.txt
        if self.channel:
            self.channel = self.channel.strip()
            self.origchannel = self.channel
            if self.channel == self.bot.cfg.nick:
                logging.warn("irc - msg detected - setting channel to %s" % self.userhost)
                self.msg = True
                self.channel = self.userhost
        if not self.channel:
            for c in self.arguments:
                if c.startswith("#"): self.channel = c
        try:
            nr = int(self.cmnd)
            if nr > 399 and not nr == 422: logging.error('%s - %s - %s - %s' % (self.bot.cfg.name, self.cmnd, self.arguments, self.txt))
        except ValueError: pass
        return self

    def reply(self, txt, result=[], event=None, origin="", dot=u", ", nr=375, extend=0, *args, **kwargs):
        """ reply to this event """
        if self.checkqueues(result): return
        if self.isdcc: self.bot.say(self.sock, txt, result, 'msg', self, nr, extend, dot, *args, **kwargs)
        elif self.msg: self.bot.say(self.nick, txt, result, 'msg', self, nr, extend, dot, *args, **kwargs)
        elif self.silent or (self.chan and self.chan.data and self.chan.data.silent): self.bot.say(self.nick, txt, result, 'msg', self, nr, extend, dot, *args, **kwargs)
        else: self.bot.say(self.channel, txt, result, 'msg', self, nr, extend, dot, *args, **kwargs)
        return self

## postfix count - how many arguments

pfc = {}
pfc['NICK'] = 0
pfc['QUIT'] = 0
pfc['SQUIT'] = 1
pfc['JOIN'] = 0
pfc['PART'] = 1
pfc['TOPIC'] = 1
pfc['KICK'] = 2
pfc['PRIVMSG'] = 1
pfc['NOTICE'] = 1
pfc['SQUERY'] = 1
pfc['PING'] = 0
pfc['ERROR'] = 0
pfc['AWAY'] = 0
pfc['WALLOPS'] = 0
pfc['INVITE'] = 1
pfc['001'] = 1
pfc['002'] = 1
pfc['003'] = 1
pfc['004'] = 4
pfc['005'] = 15
pfc['302'] = 1
pfc['303'] = 1
pfc['301'] = 2
pfc['305'] = 1
pfc['306'] = 1
pfc['311'] = 5
pfc['312'] = 3
pfc['313'] = 2
pfc['317'] = 3
pfc['318'] = 2
pfc['319'] = 2
pfc['314'] = 5
pfc['369'] = 2
pfc['322'] = 3
pfc['323'] = 1
pfc['325'] = 3
pfc['324'] = 4
pfc['331'] = 2
pfc['332'] = 2
pfc['341'] = 3
pfc['342'] = 2
pfc['346'] = 3
pfc['347'] = 2
pfc['348'] = 3
pfc['349'] = 2
pfc['351'] = 3
pfc['352'] = 7
pfc['315'] = 2
pfc['353'] = 3
pfc['366'] = 2
pfc['364'] = 3
pfc['365'] = 2
pfc['367'] = 2
pfc['368'] = 2
pfc['371'] = 1
pfc['374'] = 1
pfc['375'] = 1
pfc['372'] = 1
pfc['376'] = 1
pfc['381'] = 1
pfc['382'] = 2
pfc['383'] = 5
pfc['391'] = 2
pfc['392'] = 1
pfc['393'] = 1
pfc['394'] = 1
pfc['395'] = 1
pfc['262'] = 3
pfc['242'] = 1
pfc['235'] = 3
pfc['250'] = 1
pfc['251'] = 1
pfc['252'] = 2
pfc['253'] = 2
pfc['254'] = 2
pfc['255'] = 1
pfc['256'] = 2
pfc['257'] = 1
pfc['258'] = 1
pfc['259'] = 1
pfc['263'] = 2
pfc['265'] = 1
pfc['266'] = 1
pfc['401'] = 2
pfc['402'] = 2
pfc['403'] = 2
pfc['404'] = 2
pfc['405'] = 2
pfc['406'] = 2
pfc['407'] = 2
pfc['408'] = 2
pfc['409'] = 1
pfc['411'] = 1
pfc['412'] = 1
pfc['413'] = 2
pfc['414'] = 2
pfc['415'] = 2
pfc['421'] = 2
pfc['422'] = 1
pfc['423'] = 2
pfc['424'] = 1
pfc['431'] = 1
pfc['432'] = 2
pfc['433'] = 2
pfc['436'] = 2
pfc['437'] = 2
pfc['441'] = 3
pfc['442'] = 2
pfc['443'] = 3
pfc['444'] = 2
pfc['445'] = 1
pfc['446'] = 1
pfc['451'] = 1
pfc['461'] = 2
pfc['462'] = 1
pfc['463'] = 1
pfc['464'] = 1
pfc['465'] = 1
pfc['467'] = 2
pfc['471'] = 2
pfc['472'] = 2
pfc['473'] = 2
pfc['474'] = 2
pfc['475'] = 2
pfc['476'] = 2
pfc['477'] = 2
pfc['478'] = 3
pfc['481'] = 1
pfc['482'] = 2
pfc['483'] = 1
pfc['484'] = 1
pfc['485'] = 1
pfc['491'] = 1
pfc['501'] = 1
pfc['502'] = 1
pfc['700'] = 2
