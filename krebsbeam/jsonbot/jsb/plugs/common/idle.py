# jsb/plugs/common/idle.py
#
#

""" show how long someone has been idle. """

## jsb imports

from jsb.utils.timeutils import elapsedstring
from jsb.utils.generic import getwho
from jsb.lib.commands import cmnds
from jsb.lib.callbacks import callbacks
from jsb.lib.examples import examples
from jsb.lib.persist import PlugPersist

## basic imports

import time
import os
import logging

## defines

idle = PlugPersist('idle.data')
if not idle.data:
    idle.data = {}

## save on shutdown

def shutdown():
    global idle
    idle.save()

## callbacks

def preidle(bot, event):
    """ idle precondition aka check if it is not a command """
    if not event.iscmnd(): return True
    if bot.isgae and event.userhost in bot.cfg.followlist: return True
        
def idlecb(bot, event):
    """ idle PRIVMSG callback .. set time for channel and nick """
    ttime = time.time()
    idle.data[event.userhost] = ttime
    idle.data[event.channel] = ttime
    idle.sync()

callbacks.add('PRIVMSG', idlecb, preidle)
callbacks.add('MESSAGE', idlecb, preidle)
callbacks.add('WEB', idlecb, preidle)
callbacks.add('CONSOLE', idlecb, preidle)
callbacks.add('DISPATCH', idlecb, preidle)

## idle command

def handle_idle(bot, ievent):
    """ arguments: [<nick>] .. show how idle an channel/user has been """
    try:
        who = ievent.args[0]
    except IndexError:
        handle_idle2(bot, ievent)
        return
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("can't get userhost of %s" % who)
        return
    logging.warn("idle - userhost is %s" % userhost)
    try:
        elapsed = elapsedstring(time.time() - idle.data[userhost])
    except KeyError:
        ievent.reply("i haven't seen %s" % who)
        return
    if elapsed:
        ievent.reply("%s is idle for %s" % (who, elapsed))
        return
    else:
        ievent.reply("%s is not idle" % who)
        return   

def handle_idle2(bot, ievent):
    """ show how idle a channel has been """
    chan = ievent.channel
    try:
        elapsed = elapsedstring(time.time()-idle.data[chan])
    except KeyError:
        ievent.reply("nobody said anything on channel %s yet" % chan)
        return
    if elapsed:
        ievent.reply("channel %s is idle for %s" % (chan, elapsed))
    else:
        ievent.reply("channel %s is not idle" % chan)

cmnds.add('idle', handle_idle, ['OPER', 'USER', 'GUEST'])
examples.add('idle', 'show how idle the channel is or show how idle <nick> is', '1) idle 2) idle test')
