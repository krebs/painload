# jsb/lib/waiter.py
#
#

""" wait for events. """

## jsb imports

from jsb.lib.runner import waitrunner
from jsb.utils.trace import whichmodule
from jsb.utils.exception import handle_exception

## basic imports

import logging
import copy
import types
import time
import uuid

## defines

cpy = copy.deepcopy

## Wait class

class Wait(object):

    """ 
        wait object contains a list of types to match and a list of callbacks to 
        call, optional list of userhosts to match the event with can be given. 
    """ 

    def __init__(self, cbtypes, cbs=None, userhosts=None, modname=None, event=None, queue=None):
        self.created = time.time()
        if type(cbtypes) != types.ListType: cbtypes = [cbtypes, ]
        self.cbtypes = cbtypes
        self.userhosts = userhosts
        if cbs and type(cbs) != types.ListType: cbs = [cbs, ]
        self.cbs = cbs
        self.modname = modname
        self.origevent = event
        self.queue = queue

    def check(self, bot, event):
        """ check whether event matches this wait object. if so call callbacks. """
        target = event.cmnd or event.cbtype
        logging.debug("waiter - checking for %s - %s" % (target, self.cbtypes))
        if target not in self.cbtypes: return 
        if event.channel and self.origevent and not event.channel == self.origevent.channel:
            logging.warn("waiter - %s and %s dont match" % (event.channel, self.origevent.channel))
            return
        if self.userhosts and event.userhost and event.userhost not in self.userhosts:
            logging.warn("waiter - no userhost matched")
            return
        if self.queue: self.queue.put_nowait(event)
        self.docbs(bot, event)
        return event

    def docbs(self, bot, event):
        """ do the actual callback .. put callback on the waitrunner for execution. """
        if not self.cbs: return
        logging.warn("%s - found wait match: %s" % (bot.cfg.name, event.dump()))
        for cb in self.cbs:
            try: waitrunner.put(self.modname, cb, bot, event)
            except Exception, ex: handle_exception()

## Waiter class

class Waiter(object):

    """ list of wait object to match. """

    def __init__(self):
        self.waiters = {}

    def register(self, cbtypes, cbs=None, userhosts=None, event=None, queue=None):
        """ add a wait object to the waiters dict. """
        logging.warn("waiter - registering wait object: %s - %s" % (str(cbtypes), str(userhosts)))
        key = str(uuid.uuid4())
        self.waiters[key] = Wait(cbtypes, cbs, userhosts, modname=whichmodule(), event=event, queue=queue)
        return key

    def ready(self, key):
        try: del self.waiters[key]
        except KeyError: logging.warn("wait - %s key is not in waiters" % key)

    def check(self, bot, event):
        """ scan waiters for possible wait object that match. """
        matches = []
        for wait in self.waiters.values():
            result = wait.check(bot, event)
            if not wait.cbtypes: matches.append(wait)
        if matches: self.delete(matches)
        return matches

    def delete(self, removed):
        """ delete a list of wait items from the waiters dict. """
        logging.debug("waiter - removing from waiters: %s" % str(removed)) 
        for w in removed:
            try: del self.waiters[w]
            except KeyError: pass

    def remove(self, modname):
        """ remove all waiter registered by modname. """
        removed = []
        for wait in self.waiters.values():
            if wait.modname == modname: removed.append(wait)
        if removed: self.delete(removed)

## the global waiter object

waiter = Waiter()

