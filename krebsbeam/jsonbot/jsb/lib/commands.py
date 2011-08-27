# jsb/commands.py
#
#

""" 
    the commands module provides the infrastructure to dispatch commands. 
    commands are the first word of a line. 

"""

## jsb imports

from threads import start_new_thread, start_bot_command
from jsb.utils.xmpp import stripped
from jsb.utils.trace import calledfrom, whichmodule
from jsb.utils.exception import handle_exception
from jsb.utils.lazydict import LazyDict
from errors import NoSuchCommand, NoSuchUser
from persiststate import UserState
from runner import cmndrunner
from boot import getcmndperms

## basic imports

import logging
import sys
import types
import os
import copy
import time
import re

## defines

cpy = copy.deepcopy

## Command class

class Command(LazyDict):

    """ a command object. """

    def __init__(self, modname, cmnd, func, perms=[], threaded=False, wait=False, orig=None, how=None):
        LazyDict.__init__(self)
        if not modname: raise Exception("modname is not set - %s" % cmnd)
        self.modname = cpy(modname)
        self.plugname = self.modname.split('.')[-1]
        self.cmnd = cpy(cmnd)
        self.orig = cpy(orig)
        self.func = func
        if type(perms) == types.StringType: perms = [perms, ]
        self.perms = cpy(perms)
        self.plugin = self.plugname
        self.threaded = cpy(threaded)
        self.wait = cpy(wait)
        self.enable = True
        self.how = how or "overwrite"
        self.regex = None

class Commands(LazyDict):

    """
        the commands object holds all commands of the bot.
 
    """

    regex = []

    def add(self, cmnd, func, perms, threaded=False, wait=False, orig=None, how=None, *args, **kwargs):
        """ add a command. """
        modname = calledfrom(sys._getframe())
        try: prev = self[cmnd]
        except KeyError: prev = None
        target = Command(modname, cmnd, func, perms, threaded, wait, orig, how)
        if how == "regex":
            logging.info("regex command detected - %s" % cmnd)
            self.regex.append(target)
            target.regex = cmnd 
            return self
        self[cmnd] = target
        try:
            c = cmnd.split('-')[1]
            if not self.subs: self.subs = LazyDict()
            if self.subs.has_key(c):
                if not self.subs[c]: self.subs[c] = []
                if prev in self.subs[c]: self.subs[c].remove(prev) 
                if target not in self.subs[c]: self.subs[c].append(target)
            else: self.subs[c] = [target, ]
        except IndexError: pass
        try:
            p = cmnd.split('-')[0]
            if not self.pre: self.pre = LazyDict()
            if self.pre.has_key(p):
                if not self.pre[p]: self.pre[p] = []
                if prev in self.pre[p]: self.pre[p].remove(prev) 
                if target not in self.pre[p]: self.pre[p].append(target)
            else: self.pre[p] = [target, ]
        except IndexError: pass
        return self

    def checkre(self, bot, event):
        for r in self.regex:
            s = re.search(r.cmnd, event.stripcc())
            if s:
                logging.warn("regex matches %s" % r.cmnd)
                event.groups = list(s.groups())
                return r

    def woulddispatch(self, bot, event, cmnd=""):
        """ 
            dispatch an event if cmnd exists and user is allowed to exec this 
            command.

        """
        cmnd = cmnd or event.usercmnd.lower()
        if not cmnd: return
        try:
            cmnd = event.chan.data.aliases[cmnd]
        except (KeyError, TypeError):
            try: cmnd = bot.aliases.data[cmnd]
            except (KeyError, TypeError): pass
        try:
            if cmnd:
                event.txt = cmnd +  ' ' + ' '.join(event.txt.split()[1:])
                event.usercmnd = cmnd.split()[0]
                event.prepare()
        except (TypeError, KeyError, AttributeError): pass
        logging.debug("%s" % cmnd)
        bot.plugs.reloadcheck(bot, event)
        result = None
        cmnd = event.usercmnd
        try:
            result = self[cmnd]
        except KeyError:
            if self.subs and self.subs.has_key(cmnd):
                cmndlist = self.subs[cmnd]
                if len(cmndlist) == 1: result = cmndlist[0]
                else: event.reply("try one of: %s" % ", ".join([x.cmnd for x in cmndlist])) ; return
            else:
                if self.pre and self.pre.has_key(cmnd):
                    cmndlist = self.pre[cmnd]
                    if len(cmndlist) == 1: result = cmndlist[0]
                    else: event.reply("try one of: %s" % ", ".join([x.cmnd for x in cmndlist])) ; return
        logging.debug("woulddispatch result: %s" % result)
        return result

    def dispatch(self, bot, event, wait=0):
        """ 
            dispatch an event if cmnd exists and user is allowed to exec this 
            command.

        """
        if event.groupchat and bot.cfg.fulljids: id = event.auth
        elif event.groupchat: id = event.auth = event.userhost
        else: id = event.auth
        if not event.user: raise NoSuchUser(event.auth)
        c = self.checkre(bot, event)
        if not c: c = self.woulddispatch(bot, event)
        if not c: raise NoSuchCommand()
        if bot.cmndperms and bot.cmndperms[c.cmnd]: perms = bot.cmndperms[c.cmnd]
        else: perms = c.perms
        if bot.allowall: return self.doit(bot, event, c, wait=wait)
        elif event.chan and event.chan.data.allowcommands and event.usercmnd in event.chan.data.allowcommands: 
            if not 'OPER' in perms:  return self.doit(bot, event, c, wait=wait)
            else: logging.warn("%s is not in allowlist" % c)
        elif not bot.users or bot.users.allowed(id, perms, bot=bot): return self.doit(bot, event, c, wait=wait)
        elif bot.users.allowed(id, perms, bot=bot): return self.doit(bot, event, c, wait=wait)
        return event

    def doit(self, bot, event, target, wait=0):
        """ do the dispatching. """
        if not target.enable: return
        if target.modname in event.chan.data.denyplug:
             logging.warn("%s is denied in channel %s - %s" % (target.plugname, event.channel, event.userhost))
             return
        id = event.auth or event.userhost
        event.iscommand = True
        event.how = event.how or target.how or "overwrite"
        event.thecommand = target
        time.sleep(0.01)
        logging.warning('dispatching %s for %s' % (event.usercmnd, id))
        try:
            #if bot.type == "tornado": target.func(bot, event) ; event.ready() ; return event
            if bot.isgae:
                if not event.notask and (target.threaded or event.threaded) and not event.nothreads:
                    logging.warn("LAUNCHING AS TASK")
                    from jsb.drivers.gae.tasks import start_botevent
                    event.txt = event.origtxt
                    start_botevent(bot, event, event.speed)
                    event.reply("task started for %s" % event.auth)
                else: target.func(bot, event) ; event.ready() ; return event
            else:
                if target.threaded and not event.nothreads:
                    logging.warning("launching thread for %s" % event.usercmnd)
                    t = start_bot_command(target.func, (bot, event))
                    event.threads.append(t)
                else: event.dontclose = False; cmndrunner.put(target.modname, target.func, bot, event)
        except Exception, ex:
            logging.error('%s - error executing %s' % (whichmodule(), str(target.func)))
            raise
        return event

    def unload(self, modname):
        """ remove modname registered commands from store. """
        delete = []
        for name, cmnd in self.iteritems():
            if not cmnd: continue
            if cmnd.modname == modname: delete.append(cmnd)
        for cmnd in delete: cmnd.enable = False
        return self

    def apropos(self, search):
        """ search existing commands for search term. """
        result = []
        for name, cmnd in self.iteritems():
            if search in name: result.append(name)
        return result

    def perms(self, cmnd):
        """ show what permissions are needed to execute cmnd. """
        try: return self[cmnd].perms
        except KeyError: return []

    def whereis(self, cmnd):
        """ return plugin name in which command is implemented. """
        try: return self[cmnd].plugname
        except KeyError: return ""

    def gethelp(self, cmnd):
        """ get the docstring of a command. used for help. """
        try: return self[cmnd].func.__doc__
        except KeyError: pass

## global commands

cmnds = Commands()
