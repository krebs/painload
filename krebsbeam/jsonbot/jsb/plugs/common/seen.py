# jsb/plugs/common/seen.py
#
#
# Description: tracks when a nick is last seen
# Author: Wijnand 'tehmaze' Modderman
# Website: http://tehmaze.com
# License: BSD

""" nick tracking. """

from jsb.lib.callbacks import callbacks
from jsb.lib.commands import cmnds
from jsb.lib.datadir import getdatadir
from jsb.utils.pdod import Pdod
from jsb.lib.persistconfig import PersistConfig
from jsb.lib.examples import examples

## basic imports

import os
import time

## defines

cfg = PersistConfig()
cfg.define('tz', '+0100')

## Seen-class

class Seen(Pdod):

    """ maintain last seen information. """

    def __init__(self):
        self.datadir = getdatadir() + os.sep + 'plugs' + os.sep + 'jsb.plugs.common.seen'
        Pdod.__init__(self, os.path.join(self.datadir, 'seen.data'))

    def privmsgcb(self, bot, ievent):
        self.data[ievent.nick.lower()] = {
            'time':    time.time(),
            'text':    ievent.origtxt,
            'bot':     bot.cfg.name,
            'server':  bot.cfg.server,
            'channel': ievent.channel,
            'what':    'saying',
            }

    def joincb(self, bot, ievent):
        self.data[ievent.nick.lower()] = {
            'time':    time.time(),
            'text':    '',
            'bot':     bot.cfg.name,
            'server':  bot.cfg.server,
            'channel': ievent.channel,
            'what':    'joining %s' % ievent.channel,
            }
    
    def partcb(self, bot, ievent):
        self.data[ievent.nick.lower()] = {
            'time':    time.time(),
            'text':    ievent.txt,
            'bot':     bot.cfg.name,
            'server':  bot.cfg.server,
            'channel': ievent.channel,
            'what':    'parting %s' % ievent.channel,
            }
    
    def quitcb(self, bot, ievent):
        self.data[ievent.nick.lower()] = {
            'time':    time.time(),
            'text':    ievent.txt,
            'bot':     bot.cfg.name,
            'server':  bot.cfg.server,
            'channel': ievent.channel,
            'what':    'quitting',
            }
   
    def xmppcb(self, bot, ievent):
        if ievent.type == 'unavailable':
           self.data[ievent.nick.lower()] = {
               'time':    time.time(),
               'text':    ievent.userhost,
               'bot':     bot.cfg.name,
               'server':  bot.cfg.server,
               'channel': ievent.channel,
               'what':    'saindo da sala %s' % ievent.channel,
               }
        else:
           self.data[ievent.nick.lower()] = {
               'time':    time.time(),
               'text':    ievent.userhost,
               'bot':     bot.cfg.name,
               'server':  bot.cfg.server,
               'channel': ievent.channel,
               'what':    'entrando na sala %s' % ievent.channel,
               }

  
    def size(self):
        return len(self.data.keys())

## init

seen = Seen()

## callbacks and commands register

callbacks.add('PRIVMSG', seen.privmsgcb)
callbacks.add('JOIN', seen.joincb)
callbacks.add('PART', seen.partcb)
callbacks.add('QUIT', seen.quitcb)

## seen command

def handle_seen(bot, ievent):
    """ arguments: <nick> - lookup last seen information. """
    if not ievent.args: ievent.missing('<nick>') ; return
    if True:
        nick = ievent.args[0].lower()
        if not seen.data.has_key(nick):
            alts = [x for x in seen.data.keys() if nick in x]
            if alts:
                alts.sort()
                if len(alts) > 10:
                    nums = len(alts) - 10
                    alts = ', '.join(alts[:10]) + ' + %d others' % nums
                else:
                    alts = ', '.join(alts)
                ievent.reply('no logs for %s, however, I remember seeing: %s' % (nick, alts))
            else:
                ievent.reply('no logs for %s' % nick)
        else:
            text = seen.data[nick]['text'] and ': %s' % seen.data[nick]['text'] or ''
            try:
                ievent.reply('%s was last seen on %s (%s) at %s, %s%s' % (nick, seen.data[nick]['channel'], seen.data[nick]['server'], 
                    time.strftime('%a, %d %b %Y %H:%M:%S '+ str(cfg.get('tz')), time.localtime(seen.data[nick]['time'])),
                    seen.data[nick]['what'], text))
            except KeyError:
                ievent.reply('%s was last seen at %s, %s%s' % (nick, 
                    time.strftime('%a, %d %b %Y %H:%M:%S '+ str(cfg.get('tz')), time.localtime(seen.data[nick]['time'])),
                    seen.data[nick]['what'], text))

cmnds.add('seen', handle_seen, ['OPER', 'USER', 'GUEST'])
examples.add('seen', 'show last spoken txt of a user', 'seen dunker')

## shutdown

def shutdown(): seen.save()

## size

def size(): return seen.size()
