# jsb/callbacks.py
#
#

""" 
    bot callbacks .. callbacks take place on registered events. a precondition 
    function can optionaly be provided to see if the callback should fire. 

"""

## jsb imports

from threads import getname, start_new_thread
from jsb.utils.locking import lockdec
from jsb.utils.exception import handle_exception
from jsb.utils.trace import calledfrom, whichplugin, callstack
from jsb.utils.dol import Dol

## basic imports

import sys
import copy
import thread
import logging
import time

## locks

lock = thread.allocate_lock()
locked = lockdec(lock)

## Callback class

class Callback(object):

    """ class representing a callback. """

    def __init__(self, modname, func, prereq, kwargs, threaded=False, speed=5):
        self.modname = modname
        self.plugname = self.modname.split('.')[-1]
        self.func = func # the callback function
        self.prereq = prereq # pre condition function
        self.kwargs = kwargs # kwargs to pass on to function
        self.threaded = copy.deepcopy(threaded) # run callback in thread
        self.speed = copy.deepcopy(speed) # speed to execute callback with
        self.activate = False
        self.enable = True

## Callbacks class (holds multiple callbacks)

class Callbacks(object):

    """ 
        dict of lists containing callbacks.  Callbacks object take care of 
        dispatching the callbacks based on incoming events. see Callbacks.check()

    """

    def __init__(self):
        self.cbs = Dol()

    def size(self):
        """ return number of callbacks. """
        return len(self.cbs)

    def add(self, what, func, prereq=None, kwargs=None, threaded=False, nr=False, speed=5):
        """  add a callback. """
        what = what.upper()
        modname = calledfrom(sys._getframe())
        if not kwargs: kwargs = {}
        if nr != False: self.cbs.insert(nr, what, Callback(modname, func, prereq, kwargs, threaded, speed))
        else: self.cbs.add(what, Callback(modname, func, prereq, kwargs, threaded, speed))
        logging.debug('added %s (%s)' % (what, modname))
        return self

    def unload(self, modname):
        """ unload all callbacks registered in a plugin. """
        unload = []
        for name, cblist in self.cbs.iteritems():
            index = 0
            for item in cblist:
                if item.modname == modname: unload.append((name, index))
                index += 1
        for callback in unload[::-1]:
            self.cbs.delete(callback[0], callback[1])
            logging.debug(' unloaded %s (%s)' % (callback[0], modname))

    def disable(self, plugname):
        """ disable all callbacks registered in a plugin. """
        unload = []
        for name, cblist in self.cbs.iteritems():
            index = 0
            for item in cblist:
                if item.plugname == plugname: item.activate = False

    def activate(self, plugname):
        """ activate all callbacks registered in a plugin. """
        unload = []
        for name, cblist in self.cbs.iteritems():
            index = 0
            for item in cblist:
                if item.plugname == plugname: item.activate = True

    def whereis(self, cmnd):
        """ show where ircevent.CMND callbacks are registered """
        result = []
        cmnd = cmnd.upper()
        for c, callback in self.cbs.iteritems():
            if c == cmnd:
                for item in callback:
                    if not item.plugname in result: result.append(item.plugname)
        return result

    def list(self):
        """ show all callbacks. """
        result = []
        for cmnd, callbacks in self.cbs.iteritems():
            for cb in callbacks:
                result.append(getname(cb.func))

        return result

    def check(self, bot, event):

        """ check for callbacks to be fired. """
        type = event.cbtype or event.cmnd
        if self.cbs.has_key('ALL'):
            for cb in self.cbs['ALL']: self.callback(cb, bot, event)
        if self.cbs.has_key(type):
            target = self.cbs[type]
            for cb in target: self.callback(cb, bot, event)

    def callback(self, cb, bot, event):
        """  do the actual callback with provided bot and event as arguments. """
        #if event.stop: logging.info("callbacks -  event is stopped.") ; return
        event.calledfrom = cb.modname
        if not event.bonded: event.bind(bot)
        try:
            if event.status == "done":
                logging.debug("callback - event is done .. ignoring")
                return
            if event.chan and cb.plugname in event.chan.data.denyplug:
                logging.debug("%s denied in %s - %s" % (cb.modname, event.channel, event.auth))
                return
            if cb.prereq:
                logging.debug('executing in loop %s' % str(cb.prereq))
                if not cb.prereq(bot, event): return
            if not cb.func: return
            if event.isremote(): logging.info('%s - executing REMOTE %s - %s' % (bot.cfg.name, getname(cb.func), event.cbtype))
            elif event.cbtype == "TICK": logging.debug('%s - executing %s - %s' % (bot.cfg.name, getname(cb.func), event.cbtype))
            else: logging.info('%s - executing %s - %s' % (bot.cfg.name, getname(cb.func), event.cbtype))
            event.iscallback = True
            logging.debug("%s - %s - trail - %s" % (bot.cfg.name, getname(cb.func), callstack(sys._getframe())[::-1]))
            #if not event.direct and cb.threaded and not bot.isgae: start_new_thread(cb.func, (bot, event))
            #time.sleep(0.001)
            if cb.threaded and not bot.isgae: start_new_thread(cb.func, (bot, event))
            else:
                if bot.isgae or event.direct: cb.func(bot, event) 
                else:
                    from runner import callbackrunner
                    callbackrunner.put(cb.modname, cb.func, bot, event)
            return True
        except Exception, ex:
            handle_exception()

## global callbacks

first_callbacks = Callbacks() 
callbacks = Callbacks()
last_callbacks = Callbacks()
remote_callbacks = Callbacks()
