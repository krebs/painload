# jsb/plugs/core/nickserv.py
#
# 

""" authenticate to NickServ. """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ ='BSD'

## jsb imports

from jsb.lib.examples import examples
from jsb.lib.callbacks import callbacks
from jsb.lib.commands import cmnds
from jsb.lib.datadir import getdatadir
from jsb.lib.fleet import getfleet
from jsb.utils.pdod import Pdod

## basic imports

import os
import time
import logging

## NSAuth class

class NSAuth(Pdod):

    """ nickserve auth. """

    def __init__(self):
        self.registered = False
        Pdod.__init__(self, getdatadir() + os.sep + 'plugs' + os.sep + 'jsb.plugs.nickserv' + os.sep + 'nickserv')

    def add(self, bot, **kwargs):
        """ add a nickserv entry. """
        options = {
            'nickserv': 'NickServ',
            'identify': 'identify',
        }
        options.update(kwargs)
        assert options.has_key('password'), 'A password must be set'
        for key in options.keys(): Pdod.set(self, bot.cfg.name, key, options[key])
        self.save()

    def remove(self, bot):
        """ remove a nickserv entry. """
        if self.has_key(bot.cfg.name):
            del self[bot.cfg.name]
            self.save()

    def has(self, bot):
        """ check if a bot is in the nickserv list. """
        return self.has_key(bot.cfg.name)

    def register(self, bot, passwd):
        """ register a bot to nickserv. """
        if self.has_key(bot.cfg.name) and self.has_key2(bot.cfg.name, 'nickserv'):
            bot.sendraw('PRIVMSG %s :%s %s' % (self.get(bot.cfg.name, 'nickserv'),  'REGISTER', passwd))
            logging.warn('nickserv - register sent on %s' % bot.cfg.server)

    def identify(self, bot):
        """ identify a bot to nickserv. """
        if self.has_key(bot.cfg.name):
            logging.warn('nickserv - identify sent on %s' % bot.cfg.server)
            bot.outnocb(self.get(bot.cfg.name, 'nickserv'), '%s %s' % (self.get(bot.cfg.name, 'identify'), self.get(bot.cfg.name, 'password')), how="msg")

    def listbots(self):
        """ list all bots know. """
        all = []
        for bot in self.data.keys(): all.append((bot, self.data[bot]['nickserv']))
        return all

    def sendstring(self, bot, txt):
        """ send string to nickserver. """
        nickservnick = self.get(bot.cfg.name, 'nickserv')
        logging.warn('nickserv - sent %s to %s' % (txt, nickservnick))
        bot.outnocb(nickservnick, txt, how="msg")

    def handle_001(self, bot, ievent):
        self.identify(bot)
        try:
            for i in self.data[bot.cfg.name]['nickservtxt']:
                self.sendstring(bot, i)
                logging.warn('nickserv - sent %s' % i)
        except: pass

## init stuff

nsauth = NSAuth()
if not nsauth.data:
    nsauth = NSAuth()

## register callback

callbacks.add('001', nsauth.handle_001, threaded=True)

## ns-add command

def handle_nsadd(bot, ievent):
    """ arguments: <password> [<nickserv nick>] [<identify command>] - add a bot to the nickserv. """
    if bot.jabber: return
    if len(ievent.args) < 1:
        ievent.missing('<password> [<nickserv nick>] [<identify command>]')
        return
    if nsauth.has(bot): ievent.reply('replacing previous configuration')
    options = {}
    if len(ievent.args) >= 1: options.update({'password': ievent.args[0]})
    if len(ievent.args) >= 2: options.update({'nickserv': ievent.args[1]})
    if len(ievent.args) >= 3: options.update({'identify': ' '.join(ievent.args[2:])})
    nsauth.add(bot, **options)
    ievent.reply('ok')

cmnds.add('ns-add', handle_nsadd, 'OPER', threaded=True)
examples.add('ns-add', 'ns-add <password> [<nickserv nick>] [<identify command>] .. add nickserv', 'ns-add mekker')

## ns-del command

def handle_nsdel(bot, ievent):
    """ arguments: <botname> - remove a bot from nickserv. """
    if bot.jabber: return
    if len(ievent.args) != 1:
        ievent.missing('<botname>')
        return
    botname = ievent.args[0]
    fbot = getfleet().byname(botname)
    if not fbot:
        ievent.reply('fleet bot %s not found' % botname)
        return
    if not nsauth.has(fbot):
        ievent.reply('nickserv not configured on %s' % fbot.cfg.name)
        return
    nsauth.remove(fbot)
    ievent.reply('ok')

cmnds.add('ns-del', handle_nsdel, 'OPER', threaded=True)
examples.add('ns-del', 'ns-del <fleetbot name>', 'ns-del test')

## ns-send command

def handle_nssend(bot, ievent):
    """ arguments: <txt> - send string to the nickserv. """
    if bot.jabber: return
    if not ievent.rest:
        ievent.missing('<txt>')
        return
    nsauth.sendstring(bot, ievent.rest)    
    ievent.reply('send')

cmnds.add('ns-send', handle_nssend, 'OPER', threaded=True)
examples.add('ns-send', 'ns-send <txt> .. send txt to nickserv', 'ns-send identify bla')

## ns-auth command

def handle_nsauth(bot, ievent):
    """ arguments: [<botname>] - perform an auth request. """
    if bot.jabber: return
    if len(ievent.args) != 1: name = bot.cfg.name
    else: name = ievent.args[0]
    fbot = getfleet().byname(name)
    if not fbot:
        ievent.reply('fleet bot %s not found' % name)
        return
    if not nsauth.has(fbot):
        ievent.reply('nickserv not configured on %s' % fbot.cfg.name)
        return
    nsauth.identify(fbot)
    ievent.reply('ok')

cmnds.add('ns-auth', handle_nsauth, 'OPER', threaded=True)
examples.add('ns-auth','ns-auth [<botname>]', '1) ns-auth 2) ns-auth test')

## ns-list command

def handle_nslist(bot, ievent):
    """ no arguments - show a list of all bots know with nickserv. """
    if bot.jabber: return
    all = dict(nsauth.listbots())
    rpl = []
    for bot in all.keys(): rpl.append('%s: authenticating through %s' % (bot, all[bot]))
    rpl.sort()
    ievent.reply(' .. '.join(rpl))

cmnds.add('ns-list', handle_nslist, 'OPER')
examples.add('ns-list', 'list all nickserv entries', 'ns-list')
