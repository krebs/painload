# jsb/lib/fleet.py
#
#

""" fleet is a list of bots. """

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.utils.generic import waitforqueue
from config import Config, getmainconfig
from users import users
from plugins import plugs
from persist import Persist
from errors import NoSuchBotType, BotNotEnabled
from threads import start_new_thread
from eventhandler import mainhandler
from jsb.utils.name import stripname
from jsb.lib.factory import BotFactory
from jsb.utils.lazydict import LazyDict

## simplejson imports

from jsb.imports import getjson
json = getjson()

## basic imports

import Queue
import os
import types
import time
import glob
import logging
import threading
import thread
import copy

## defines

cpy = copy.deepcopy

## classes

class FleetBotAlreadyExists(Exception):
    pass

## locks

from jsb.utils.locking import lockdec
lock = thread.allocate_lock()
locked = lockdec(lock)

## Fleet class

class Fleet(Persist):

    """
        a fleet contains multiple bots (list of bots).

    """

    def __init__(self, datadir):
        Persist.__init__(self, datadir + os.sep + 'fleet' + os.sep + 'fleet.main')
        if not self.data.has_key('names'): self.data['names'] = []
        if not self.data.has_key('types'): self.data['types'] = {}
        self.startok = threading.Event()
        self.bots = []

    def addnametype(self, name, type):
        if name not in self.data['names']:
            self.data['names'].append(name)
            self.data['types'][name] = type
            self.save()
        return True

    def loadall(self, names=[]):
        """ load all bots. """ 
        target = names or self.data.names
        if not target: logging.error("no bots in fleet") ; return
        else: logging.warn("loading %s" % ", ".join(target))
        threads = []
        bots = []
        for name in target:
            if not name: logging.debug(" name is not set") ; continue
            try:
                #if self.data.types[name] == "console": logging.warn("fleet- skipping console bot %s" % name) ; continue
                bot = self.makebot(self.data.types[name], name)
                if bot: bots.append(bot)
            except KeyError: continue
            except BotNotEnabled: pass
            except KeyError: logging.error("no type know for %s bot" % name)
            except Exception, ex: handle_exception()
        return bots

    def avail(self):
        """ return available bots. """
        return self.data['names']

    def getfirstbot(self, type="irc"):
        """ return the first bot in the fleet. """
        for bot in self.bots:
            if type in bot.type: return bot

    def getfirstjabber(self, isgae=False):
        """ return the first jabber bot of the fleet. """
        return self.getfirstbot("xmpp")
        
    def size(self):
        """ return number of bots in fleet. """
        return len(self.bots)

    def settype(self, name, type):
        """ set the type of a bot. """
        cfg = Config('fleet' + os.sep + stripname(name) + os.sep + 'config')
        cfg['name'] = name
        logging.debug("%s - setting type to %s" % (self.cfile, type))
        cfg.type = type
        cfg.save()

    def makebot(self, type, name, config={}, domain="", showerror=False):
        """ create a bot .. use configuration if provided. """
        if not name: logging.error(" name is not correct: %s" % name) ; return
        if not type: type = self.data.types.get(name)
        if not type: logging.error("no type found for %s bot" % name) ; return 
        if config: logging.info('making %s (%s) bot - %s' % (type, name, config.tojson()))
        bot = None
        cfg = Config('fleet' + os.sep + stripname(name) + os.sep + 'config')
        if config: cfg.merge(config) 
        if not cfg.name: cfg['name'] = name
        cfg['botname'] = cfg['name']
        if cfg.disable:
            logging.error("%s bot is disabled. see %s" % (name, cfg.cfile))
            if showerror: raise BotNotEnabled(name)
            return
        if not cfg.type and type:
            logging.debug("%s - setting type to %s" % (cfg.cfile, type))
            cfg.type = type
        if not cfg['type']:
            try:
                self.data['names'].remove(name)
                self.save()
            except ValueError: pass
            raise Exception("no bot type specified")
        if not cfg.owner:
            logging.info("%s - owner not set .. using global config." % cfg.name) 
            cfg.owner = getmainconfig().owner
        if not cfg.domain and domain: cfg.domain = domain
        if not cfg: raise Exception("can't make config for %s" % name)
        cfg.save()
        bot = BotFactory().create(type, cfg)
        if bot: self.addbot(bot)
        return bot

    def save(self):
        """ save fleet data and call save on all the bots. """
        Persist.save(self)
        for i in self.bots:
            try: i.save()
            except Exception, ex: handle_exception()

    def list(self):
        """ return list of bot names. """
        result = []
        for i in self.bots: result.append(i.cfg.name)
        return result

    def stopall(self):
        """ call stop() on all fleet bots. """
        for i in self.bots:
            try: i.stop()
            except: handle_exception()

    def byname(self, name):
        """ return bot by name. """
        for i in self.bots:
            if name == i.cfg.name: return i

    def replace(self, name, bot):
        """ replace bot with a new bot. """
        for i in range(len(self.bots)):
            if name == self.bots[i].cfg.name:
                self.bots[i] = bot
                return True

    def enable(self, cfg):
        """ enable a bot baed of provided config. """
        if cfg.name and cfg.name not in self.data['names']:
            self.data['names'].append(cfg.name)
            self.data['types'][cfg.name] = cfg.type
            self.save()
        return True

    def addbot(self, bot):
        """
            add a bot to the fleet .. remove all existing bots with the 
            same name.
        """
        assert bot
        for i in range(len(self.bots)-1, -1, -1):
            if self.bots[i] == bot: logging.info("bot %s already in fleet" % str(bot)) ; continue
            if self.bots[i].cfg.name == bot.cfg.name:
                logging.debug('removing %s from fleet' % bot.botname)
                del self.bots[i]
        self.bots.append(bot)
        logging.info('adding %s' % bot.cfg.name)
        if bot.cfg.name not in self.data['names']:
            self.data['names'].append(bot.cfg.name)
            self.data['types'][bot.cfg.name] = bot.type
            self.save()
        return True

    def delete(self, name):
        """ delete bot with name from fleet. """
        for bot in self.bots:
            if bot.cfg.name == name:
                bot.exit()
                self.remove(bot)
                bot.cfg['disable'] = 1
                bot.cfg.save()
                logging.debug('%s disabled' % bot.cfg.name)
                return True
        return False

    def remove(self, bot):
        """ delete bot by object. """
        try:
            self.bots.remove(bot)
            return True
        except ValueError:
            return False

    def exit(self, name=None, jabber=False):
        """ call exit on all bots. """
        if not name:
            threads = []
            for bot in self.bots:
                if jabber and bot.type != 'sxmpp' and bot.type != 'jabber': continue
                threads.append(start_new_thread(bot.exit, ()))
            for thread in threads: thread.join()
            return
        for bot in self.bots:
            if bot.cfg.name == name:
                if jabber and bot.type != 'sxmpp' and bot.type != 'jabber': continue
                try: bot.exit()
                except: handle_exception()
                self.remove(bot)
                return True
        return False

    def cmnd(self, event, name, cmnd):
        """ do command on a bot. """
        bot = self.byname(name)
        if not bot: return 0
        j = cpy(event)
        j.onlyqueues = True
        j.txt = cmnd
        j.displayname = bot.cfg.name
        bot.put(j)
        #result = waitforqueue(j.resqueue, 3000)
        #if not result: return []
        #time.sleep(0.2)  
        #res = ["[%s]" % bot.cfg.name, ]
        #res += result
        #return res

    def cmndall(self, event, cmnd):
        """ do a command on all bots. """
        for bot in self.bots: self.cmnd(event, bot.cfg.name, cmnd)

    def broadcast(self, txt):
        """ broadcast txt to all bots. """
        for bot in self.bots: bot.broadcast(txt)

    def startall(self, bots=None, usethreads=True):
        target = bots or self.bots
        for bot in target:
            logging.info('starting %s bot (%s)' % (bot.cfg.name, bot.type))
            if bot.type == "console": continue
            if usethreads: start_new_thread(bot.reconnect, (True,)) ; continue
            try: bot.reconnect(True)
            except Excepton, ex: handle_exception()
            time.sleep(3)

    def resume(self, sessionfile, exclude=[]):
        """ resume bot from session file. """
        session = json.load(open(sessionfile))
        chan = session.get("channel")
        for name in session['bots'].keys():
            dont = False
            for ex in exclude:
                if ex in name: dont = True
            if dont: continue
            cfg = LazyDict(session['bots'][name])
            try: 
                if not cfg.disable:
                    logging.info("resuming %s" % cfg)
                    start_new_thread(self.resumebot, (cfg, chan))
            except: handle_exception() ; return
        time.sleep(10)
        self.startok.set()

    def resumebot(self, botcfg, chan=None):
        """ resume single bot. """
        botname = botcfg.name
        logging.warn("resuming %s bot" % botname)
        if botcfg['type'] == "console": logging.warn("not resuming console bot %s" % botname) ; return
        oldbot = self.byname(botname)
        if oldbot and botcfg['type'] in ["sxmpp", "convore"]: oldbot.exit()
        cfg = Config('fleet' + os.sep + stripname(botname) + os.sep + 'config')
        if cfg.disable: logging.warn("%s - bot is disabled .. not resuming it" % botname) ; return
        bot = self.makebot(botcfg.type, botname)
        if oldbot: self.replace(oldbot, bot)
        bot._resume(botcfg, botname)
        bot.start(False)
        if chan and chan in bot.state["joinedchannels"]: bot.say(chan, "done!")

## global fleet object

fleet = None

def getfleet(datadir=None, new=False):
    if not datadir:
         from jsb.lib.datadir import getdatadir 
         datadir = getdatadir()
    global fleet
    if not fleet or new: fleet = Fleet(datadir)
    return fleet
