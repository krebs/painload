# jsb/plugins.py
#
#

""" holds all the plugins. plugins are imported modules. """

## jsb imports

from commands import cmnds
from callbacks import callbacks, remote_callbacks, first_callbacks, last_callbacks
from eventbase import EventBase
from persist import Persist
from jsb.utils.lazydict import LazyDict
from jsb.utils.exception import handle_exception
from boot import cmndtable, plugin_packages, default_plugins
from errors import NoSuchPlugin
from jsb.utils.locking import lockdec
from jsbimport import force_import, _import
from morphs import outputmorphs, inputmorphs
from wait import waiter
from boot import plugblacklist

## basic imports

import os
import logging
import Queue
import copy
import sys
import thread
import types

## defines

cpy = copy.deepcopy

## locks

loadlock = thread.allocate_lock()
locked = lockdec(loadlock)

## Plugins class

class Plugins(LazyDict):

    """ the plugins object contains all the plugins. """

    def exit(self):
        for plugname in self:
            self.unload(plugname)         

    def reloadfile(self, filename, force=True):
        logging.warn("plugs - reloading file %s" % filename)
        mlist = filename.split(os.sep)
        mod = []
        for m in mlist[::-1]:
            mod.insert(0, m)
            if m == "myplugs": break 
        modname = ".".join(mod)[:-3]
        logging.warn("plugs - using %s" % modname)
        self.reload(modname, force)
          
    def loadall(self, paths=[], force=True):
        """
            load all plugins from given paths, if force is true .. 
            otherwise load all plugins for default_plugins list.

        """
        from boot import plugblacklist
        if not paths: paths = plugin_packages
        imp = None
        for module in paths:
            try: imp = _import(module)
            except ImportError, ex:
                #handle_exception()
                logging.warn("no %s plugin package found - %s" % (module, str(ex)))
                continue
            except Exception, ex: handle_exception()
            logging.debug("got plugin package %s" % module)
            try:
                for plug in imp.__plugs__:
                    mod = "%s.%s" % (module, plug)
                    if mod in plugblacklist.data: logging.warn("%s is in blacklist .. not loading." % mod) ; continue
                    try: self.reload(mod, force=force, showerror=True)
                    except KeyError: logging.debug("failed to load plugin package %s" % module)
                    except Exception, ex: handle_exception()
            except AttributeError: logging.error("no plugins in %s .. define __plugs__ in __init__.py" % module)

    def unload(self, modname):
        """ unload plugin .. remove related commands from cmnds object. """
        logging.debug("plugins - unloading %s" % modname)
        try:
            self[modname].shutdown()
            logging.debug('called %s shutdown' % modname)
        except KeyError:
            logging.debug("no %s module found" % modname) 
            return False
        except AttributeError: pass
        try: cmnds.unload(modname)
        except KeyError: pass
        try: first_callbacks.unload(modname)
        except KeyError: pass
        try: callbacks.unload(modname)
        except KeyError: pass
        try: last_callbacks.unload(modname)
        except KeyError: pass
        try: remote_callbacks.unload(modname)
        except KeyError: pass
        try: outputmorphs.unload(modname)
        except: handle_exception()
        try: inputmorphs.unload(modname)
        except: handle_exception()
        try: waiter.remove(modname)
        except: handle_exception()
        return True

    def load(self, modname, force=False, showerror=True, loaded=[]):
        """ load a plugin. """
        if not modname: raise NoSuchPlugin(modname)
        if not force and modname in loaded: logging.warn("skipping %s" % modname) ; return loaded
        if self.has_key(modname):
            try:
                logging.debug("%s already loaded" % modname)                
                if not force: return self[modname]
                self[modname] = reload(self[modname])
            except Exception, ex: raise
        else:
            logging.debug("trying %s" % modname)
            mod = _import(modname)
            if not mod: return None
            try: self[modname] = mod
            except KeyError:
                logging.info("failed to load %s" % modname)
                raise NoSuchPlugin(modname)
        try: init = getattr(self[modname], 'init')
        except AttributeError:
            logging.warn("%s loaded" % modname)
            return self[modname]
        try:
            init()
            logging.debug('%s init called' % modname)
        except Exception, ex: raise
        logging.warn("%s loaded" % modname)
        return self[modname]

    def loaddeps(self, modname, force=False, showerror=False, loaded=[]):
        try:
            deps = self[modname].__depending__
            if deps: logging.warn("dependcies detected: %s" % deps)
        except (KeyError, AttributeError): deps = []
        deps.insert(0, modname)
        for dep in deps:
            if dep not in loaded:
                if self.has_key(dep): self.unload(dep)
                try:
                    self.load(dep, force, showerror, loaded)
                    loaded.append(dep)
                except Exception, ex: raise
        return loaded

    def reload(self, modname, force=False, showerror=False):
        """ reload a plugin. just load for now. """ 
        if type(modname) == types.ListType: loadlist = modname
        else: loadlist = [modname, ]
        loaded = []
        for modname in loadlist:
            modname = modname.replace("..", ".")
            if self.has_key(modname): self.unload(modname)
            loaded.append(self.loaddeps(modname, force, showerror, []))
        return loaded

    def dispatch(self, bot, event, wait=0, *args, **kwargs):
        """ dispatch event onto the cmnds object. check for pipelines first. """
        result = []
        if not event.pipelined and ' ! ' in event.txt: return self.pipelined(bot, event, wait=wait, *args, **kwargs)
        self.reloadcheck(bot, event)
        return cmnds.dispatch(bot, event, wait=wait, *args, **kwargs)
        

    def pipelined(self, bot, event, wait=0, *args, **kwargs):
        """ split cmnds, create events for them, chain the queues and dispatch.  """
        origqueues = event.queues
        origout = event.outqueue
        event.queues = []
        event.allowqueue = True
        event.closequeue = True
        event.pipelined = True 
        events = []
        splitted = event.txt.split(" ! ")
        for item in splitted:
            e = cpy(event)
            e.queues = []
            e.onlyqueues = True
            e.dontclose = True
            e.txt = item.strip()
            e.usercmnd = e.txt.split()[0].lower()
            if not cmnds.woulddispatch(bot, e): events.append(event) ; break
            logging.debug('creating event for %s' % e.txt)
            e.bot = bot
            e.makeargs()
            events.append(e)
        prevq = None
        for e in events[:-1]:
            q = Queue.Queue()
            e.queues.append(q)
            if prevq:
                e.inqueue = prevq
            prevq = q
        lq = events[-1]
        lq.inqueue = prevq
        lq.outqueue = origout
        lq.closequeue = True
        lq.dontclose = False
        if origqueues: lq.queues = origqueues
        for e in events: self.dispatch(bot, e, wait=wait)
        return lq

    def reloadcheck(self, bot, event, target=None):
        """
            check if event requires a plugin to be reloaded. if so 
            reload the plugin.

        """
        from boot import plugblacklist
        logging.debug("checking for reload of %s (%s)" % (event.usercmnd, event.userhost))
        plugloaded = None
        try:
            from boot import getcmndtable
            plugin = getcmndtable()[target or event.usercmnd.lower()]
        except KeyError:
            logging.debug("can't find plugin to reload for %s" % event.usercmnd)
            return
        if plugin in self: logging.debug(" %s already loaded" % plugin) ; return plugloaded
        if plugin in default_plugins: pass
        elif plugin in plugblacklist.data: return plugloaded
        elif bot.cfg.loadlist and plugin not in bot.cfg.loadlist: return plugloaded
        logging.debug("loaded %s on demand (%s)" % (plugin, event.usercmnd))
        plugloaded = self.reload(plugin)
        return plugloaded

    def getmodule(self, plugname):
        for module in plugin_packages:
            try: imp = _import(module)
            except ImportError, ex:
                if "No module" in str(ex):
                    logging.info("no %s plugin package found" % module)
                    continue
                raise
            except Exception, ex: handle_exception() ; continue
            if plugname in imp.__plugs__: return "%s.%s" % (module, plugname)

## global plugins object

plugs = Plugins()
