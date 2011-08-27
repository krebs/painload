# jsb/plugs/common/alarm.py
#
#

""" 
    the alarm plugin allows for alarms that message the user giving the
    command at a certain time or number of seconds from now

"""

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.utils.timeutils import strtotime, striptime
from jsb.utils.generic import jsonstring
from jsb.utils.lazydict import LazyDict
from jsb.lib.persist import Persist
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.utils.locking import lockdec
from jsb.lib.fleet import getfleet
from jsb.lib.datadir import datadir
from jsb.lib.periodical import periodical
from jsb.lib.nextid import nextid

## basic imports

import time
import os
import shutil
import thread
import logging

## defines

alarms = None

## locks

alarmlock = thread.allocate_lock()
alarmlocked = lockdec(alarmlock)

class Alarmitem(LazyDict):

    """ item holding alarm data """

    def __init__(self, botname='default', i=0, nick="", ttime=time.time(), txt="", printto=None, d={}):
        if not d: LazyDict.__init__(self)
        else: LazyDict.__init__(self, d)
        self.botname = self.botname or botname
        self.idnr = self.idnr or i
        self.nick = self.nick or nick
        self.time = self.ttime or ttime
        self.txt = self.txt or txt
        self.printto = self.printto or printto or nick or ""

    def __str__(self):
        result = "%s %s %s %s %s" % (self.botname, self.idnr, self.nick, self.time, self.txt)
        return result

class Alarms(Persist):

    """ class that holds the alarms """

    def __init__(self, fname):
        Persist.__init__(self, fname)
        if not self.data: self.data = []
        for i in self.data:
            z = Alarmitem(d=i)
            periodical.addjob(z.time - time.time(), 1, self.alarmsay, z.nick, z)

    def size(self):
        """ return number of alarms """
        return len(self.data)

    def bynick(self, nick):
        """ get alarms by nick """
        nick = nick.lower()
        result = []
        for i in self.data:
            z = Alarmitem(d=i)
            if z.nick == nick: result.append(z)
        return result

    def alarmsay(self, item):
        """ say alarm txt """
        logging.warn("trying to deliver on %s" % str(item))
        bot = getfleet().byname(item.botname)
        if not bot: bot = getfleet().makebot(None, item.botname)
        if bot:
            if item.printto: bot.say(item.printto, "[%s] %s" % (item.nick, item.txt), speed=1)
            else: bot.say(item.nick, item.txt, speed=1)
        else: logging.warn("can't find %s bot in fleet" % item.botname)
        self.delete(item.idnr)

    def add(self, botname, nick, ttime, txt, printto=None):
        """ add alarm """
        nick = nick.lower()
        nrid = nextid.next('alarms')
        item = Alarmitem(botname, nrid, nick, ttime, txt, printto=printto)
        pid = periodical.addjob(ttime - time.time(), 1, self.alarmsay, nick, item)
        item.idnr = pid
        self.data.append(item)
        self.save()
        return pid

    def delete(self, idnr):
        """ delete alarmnr """
        for i in range(len(self.data)-1, -1, -1):
            if Alarmitem(d=self.data[i]).idnr == idnr:
                del self.data[i]
                periodical.killjob(idnr)
                self.save()
                return 1

alarms = Alarms(datadir + os.sep + 'plugs' + os.sep + 'jsb.plugs.common.alarm' + os.sep + 'alarms')
   
def shutdown():
    periodical.kill()

def size():
    """ return number of alarms """
    return alarms.size()

def handle_alarmadd(bot, ievent):
    """ alarm <txt-with-time> | <+delta> <txt> .. add an alarm """
    if not ievent.rest: ievent.reply('alarm <txt-with-time> or alarm <+delta> <txt>') ; return
    else: alarmtxt = ievent.rest
    if alarmtxt[0] == '+':
        try: sec = int(ievent.args[0][1:]) 
        except ValueError: ievent.reply('use +nrofsecondstosleep') ; return
        if len(ievent.args) < 2: ievent.reply('i need txt to remind you') ; return
        try:
            ttime = time.time() + sec
            if ttime > 2**31: ievent.reply("time overflow") ; return
            if bot.type == "xmpp":
                if ievent.groupchat: nrid = alarms.add(bot.cfg.name, ievent.nick, ttime, ' '.join(ievent.args[1:]), ievent.channel)
                else: nrid = alarms.add(bot.cfg.name, ievent.stripped, ttime, ' '.join(ievent.args[1:]))
            elif bot.type == "irc":
                if ievent.msg:  nrid = alarms.add(bot.cfg.name, ievent.nick, ttime, ' '.join(ievent.args[1:]), ievent.nick)
                else:  nrid = alarms.add(bot.cfg.name, ievent.nick, ttime, ' '.join(ievent.args[1:]), ievent.channel)
            else: nrid = alarms.add(bot.cfg.name, ievent.nick, ttime, ' '.join(ievent.args[1:]), ievent.channel)
            ievent.reply("alarm %s set at %s" % (nrid, time.ctime(ttime)))
            return
        except Exception, ex: handle_exception(ievent) ; return
    alarmtime = strtotime(alarmtxt)
    if not alarmtime: ievent.reply("can't detect time") ; return
    txt = striptime(alarmtxt).strip()
    if not txt: ievent.reply('i need txt to remind you') ; return
    if time.time() > alarmtime: ievent.reply("we are already past %s" % time.ctime(alarmtime)) ; return
    if bot.jabber: nrid = alarms.add(bot.cfg.name, ievent.nick, alarmtime, txt, ievent.channel)
    else: nrid = alarms.add(bot.cfg.name, ievent.nick, alarmtime, txt, ievent.channel)
    ievent.reply("alarm %s set at %s" % (nrid, time.ctime(alarmtime)))

cmnds.add('alarm', handle_alarmadd, 'USER', allowqueue=False)
examples.add('alarm', 'say txt at a specific time or time diff', '1) alarm 12:00 lunchtime 2) alarm 3-11-2008 0:01 birthday ! 3) alarm +180 egg ready')

def handle_alarmlist(bot, ievent):
    """ alarm-list .. list all alarms """
    result = []
    for alarmdata in alarms.data:
        i = Alarmitem(d=alarmdata)
        result.append("%s) %s: %s - %s " % (i.idnr, i.nick, time.ctime(i.time), i.txt))
    if result: ievent.reply("alarmlist: ", result)
    else: ievent.reply('no alarms')

cmnds.add('alarm-list', handle_alarmlist, 'OPER')
examples.add('alarm-list', 'list current alarms', 'alarm-list')

def handle_myalarmslist(bot, ievent):
    """ alarm-mylist .. show alarms of user giving the command """
    result = []
    if bot.jabber: nick = ievent.stripped.lower()
    else: nick = ievent.nick.lower()
    for alarmdata in alarms.data:
        i = Alarmitem(d=alarmdata)
        if i.nick == nick: result.append("%s) %s - %s " % (i.idnr, time.ctime(i.time), i.txt))
    if result: ievent.reply("your alarms: ", result)
    else: ievent.reply('no alarms')

cmnds.add('alarm-mylist', handle_myalarmslist, 'USER')
examples.add('alarm-mylist', 'list alarms of user giving the commands', 'alarm-mylist')

def handle_alarmdel(bot, ievent):
    """ alarm-del <nr> .. delete alarm """
    try: alarmnr = int(ievent.args[0])
    except IndexError: ievent.missing('<nr>') ; return
    except ValueError: ievent.reply('argument needs to be an integer') ; return
    if alarms.delete(alarmnr): ievent.reply('alarm with id %s deleted' % alarmnr)
    else: ievent.reply('failed to delete alarm with id %s' % alarmnr)

cmnds.add('alarm-del', handle_alarmdel, 'OPER')
examples.add('alarm-del', 'delete alarm with id <nr>', 'alarm-del 7')

