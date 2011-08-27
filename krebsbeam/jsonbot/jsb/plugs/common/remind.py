# jsb/plugs/common/remind.py
#
#

""" remind people .. say txt when somebody gets active """

## jsb imports

from jsb.utils.generic import getwho
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.callbacks import callbacks
from jsb.lib.persist import PlugPersist

## basic imports

import time
import os

## Remind-class

class Remind(PlugPersist):

    """ remind object """

    def __init__(self, name):
        PlugPersist.__init__(self, name)

    def add(self, who, data):
        """ add a remind txt """
        if not self.data.has_key(who):
             self.data[who] = []
        self.data[who].append(data)
        self.save()

    def wouldremind(self, userhost):
        """ check if there is a remind for userhost """
        try:
            reminds = self.data[userhost]
            if reminds == None or reminds == []:
                return False
        except KeyError:
            return False
        return True

    def remind(self, bot, userhost):
        """ send a user all registered reminds """
        reminds = self.data[userhost]
        if not reminds:
            return
        for i in reminds:
            ttime = None
            try:
                (tonick, fromnick, txt, ttime) = i
            except ValueError:
                (tonick, fromnick, txt) = i
            txtformat = '[%s] %s wants to remind you of: %s'
            if ttime:
                timestr = time.ctime(ttime)
            else:
                timestr = None
            bot.saynocb(tonick, txtformat % (timestr, fromnick, txt))
            bot.saynocb(fromnick, '[%s] reminded %s of: %s' % (timestr, tonick, txt))
        try: del self.data[userhost]
        except KeyError: pass
        self.save()

## defines

remind = Remind('remind.data')
assert remind

## callbacks

def preremind(bot, ievent):
    """ remind precondition """
    return remind.wouldremind(ievent.userhost)

def remindcb(bot, ievent):
    """ remind callbacks """
    remind.remind(bot, ievent.userhost)

callbacks.add('PRIVMSG', remindcb, preremind, threaded=True)
callbacks.add('JOIN', remindcb, preremind, threaded=True)
callbacks.add('MESSAGE', remindcb, preremind, threaded=True)
callbacks.add('WEB', remindcb, preremind, threaded=True)
callbacks.add('TORNADO', remindcb, preremind, threaded=True)

## remind command

def handle_remind(bot, ievent):
    """ arguments: <nick> <txt>  - add a remind for a user, as soon as he/she gets online or says something the txt will be send. """
    try: who = ievent.args[0] ; txt = ' '.join(ievent.args[1:])
    except IndexError: ievent.missing('<nick> <txt>') ; return
    if not txt: ievent.missing('<nick> <txt>') ; return
    userhost = getwho(bot, who)
    if not userhost: ievent.reply("can't find userhost for %s" % who) ; return
    else:
        remind.add(userhost, [who, ievent.nick, txt, time.time()])
        ievent.reply("remind for %s added" % who)

cmnds.add('remind', handle_remind, ['OPER', 'USER', 'GUEST'], allowqueue=False)
examples.add('remind', 'remind <nick> <txt>', 'remind dunker check the bot !')
