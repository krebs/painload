# jsb/boot.py
#
#

""" admin related data and functions. """

## jsb imports

from jsb.utils.generic import checkpermissions, isdebian, botuser
from jsb.lib.persist import Persist
from jsb.utils.exception import handle_exception
from jsb.lib.datadir import makedirs, getdatadir
from jsb.lib.config import Config, getmainconfig
from jsb.lib.jsbimport import _import
from jsb.utils.lazydict import LazyDict
from jsb.memcached import startmcdaemon

## basic imports

import logging
import os
import sys
import types
import copy

## paths

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.getcwd() + os.sep + '..')
#try: sys.path.append(os.path.expanduser("~") + os.sep + '.jsb')
#except: pass

## defines

ongae = False
try:
    import waveapi
    plugin_packages = ['myplugs.common', 'myplugs.gae','jsb.plugs.core', 'jsb.plugs.gae', 'jsb.plugs.common', 'jsb.plugs.wave', 'jsb.plugs.myplugs.common', 'jsb.plugs.myplugs.gae']
    ongae = True
except ImportError: plugin_packages = ['myplugs.common', 'myplugs.socket', 'jsb.plugs.core', 'jsb.plugs.common', 'jsb.plugs.socket', 'jsb.plugs.myplugs.common', 'jsb.plugs.myplugs.socket']

default_plugins = ['jsb.plugs.core.admin', 'jsb.plugs.core.dispatch', 'jsb.plugs.core.plug']

logging.info("boot - default plugins are %s" % str(default_plugins))

loaded = False
cmndtable = None 
pluginlist = None
callbacktable = None
cmndperms = None
timestamps = None
plugwhitelist = None
plugblacklist = None
cpy = copy.deepcopy

## boot function

def boot(ddir=None, force=False, encoding="utf-8", umask=None, saveperms=True, fast=False, clear=False):
    """ initialize the bot. """
    try:
        if os.getuid() == 0:
            print "don't run the bot as root"
            os._exit(1)
    except AttributeError: pass
    logging.info("booting ..")
    from jsb.lib.datadir import getdatadir, setdatadir
    if ddir: setdatadir(ddir)
    origdir = ddir 
    ddir = ddir or getdatadir()
    if not ddir: logging.error("can't determine datadir to boot from") ; os._exit(1)
    if not ddir in sys.path: sys.path.append(ddir)
    makedirs(ddir)
    if os.path.isdir("/var/run/jsb") and botuser() == "jsb": rundir = "/var/run/jsb"
    else: rundir = ddir + os.sep + "run"
    try:
        k = open(rundir + os.sep + 'jsb.pid','w')
        k.write(str(os.getpid()))
        k.close()
    except IOError: pass
    try:
        if not ongae:
            reload(sys)
            sys.setdefaultencoding(encoding)
    except (AttributeError, IOError): pass
    try:
        if not umask: checkpermissions(getdatadir(), 0700) 
        else: checkpermissions(getdatadir(), umask)  
    except: handle_exception()
    global loaded
    global cmndtable
    global pluginlist
    global callbacktable
    global cmndperms
    global plugcommands
    global timestamps
    global plugwhitelist
    global plugblacklist
    if not cmndtable: cmndtable = Persist(rundir + os.sep + 'cmndtable')
    if clear: cmndtable.data = {}
    if not pluginlist: pluginlist = Persist(rundir + os.sep + 'pluginlist')
    if clear: pluginlist.data = []
    if not callbacktable: callbacktable = Persist(rundir + os.sep + 'callbacktable')
    if clear: callbacktable.data = {}
    if not timestamps: timestamps = Persist(rundir + os.sep + 'timestamps')
    if clear: timestamps.data = {}
    if not plugwhitelist: plugwhitelist = Persist(rundir + os.sep + 'plugwhitelist')
    if not plugwhitelist.data or clear: plugwhitelist.data = []
    if not plugblacklist: plugblacklist = Persist(rundir + os.sep + 'plugblacklist')
    if not plugblacklist.data or clear: plugblacklist.data = []
    if not cmndperms: cmndperms = Config('cmndperms', ddir=ddir)
    from jsb.lib.plugins import plugs
    if not cmndtable.data or force:
        plugs.loadall(plugin_packages, force=True)
        loaded = True
        savecmndtable(saveperms=saveperms)
    if not pluginlist.data or force:
        if not loaded:
            plugs.loadall(plugin_packages, force=True)
            loaded = True
        savepluginlist()
    if not callbacktable.data or force:
        if not loaded:
            plugs.loadall(plugin_packages, force=True)
            loaded = True
        savecallbacktable()
    if not loaded:
        logging.info("boot - plugins not loaded .. loading defaults")
        for plug in default_plugins:
            plugs.reload(plug, showerror=True, force=True)
        if not fast:
            if ongae: plugs.loadall(["myplugs.common", "myplugs.gae", "jsb.plugs.myplugs.gae", "jsb.plugs.myplugs.common"], force=True)
            else: plugs.loadall(["myplugs.common", "myplugs.socket", "jsb.plugs.myplugs.socket", "jsb.plugs.myplugs.common"], force=True)
        else: logging.error("skipped loading of myplugs")
    try:
        changed = checktimestamps()
        if changed:
            logging.warn("boot - files changed %s" % str(changed))
            for plugfile in changed: plugs.reloadfile(plugfile, force=True)
    except Exception, ex: logging.error("boot - can't read myplugs dir.")
    logging.warn("boot - done")

## filestamps stuff

def checktimestamps(d=None):
    changed = []
    if not d: d = getdatadir() + os.sep + "myplugs"
    for f in os.listdir(d):
        if os.path.isdir(d + os.sep + f): changed.extend(checktimestamps(d + os.sep + f))
        if not f.endswith(".py"): continue 
        m = d + os.sep + f
        global timestamps
        try:
            t = os.path.getmtime(m)
            if t > timestamps.data[m]: changed.append(m) ; timestamps.data[m] = t
        except KeyError: timestamps.data[m] = os.path.getmtime(m) ; changed.append(m)
    if changed: timestamps.save()
    return changed 

## commands related commands

def savecmndtable(modname=None, saveperms=True):
    """ save command -> plugin list to db backend. """
    global cmndtable
    if not cmndtable.data: cmndtable.data = {}
    if modname: target = LazyDict(cmndtable.data)
    else: target = LazyDict()
    global cmndperms
    #if not cmndperms.data: cmndperms.data = {}
    from jsb.lib.commands import cmnds
    assert cmnds
    if cmnds.subs:
        for name, clist in cmnds.subs.iteritems():
            if name:
                if name in cmnds: continue
                if clist and len(clist) == 1: target[name] = clist[0].modname
    for cmndname, c in cmnds.iteritems():
        if modname and c.modname != modname or cmndname == "subs": continue
        if cmndname and c:
            target[cmndname] = c.modname  
            cmndperms[cmndname] = c.perms
    logging.warn("saving command table")
    assert cmndtable
    assert target
    cmndtable.data = target
    cmndtable.save()
    if saveperms:
        logging.warn("saving command perms")
        cmndperms.save()

def removecmnds(modname):
    """ remove commands belonging to modname form cmndtable. """
    global cmndtable
    assert cmndtable
    from jsb.lib.commands import cmnds
    assert cmnds
    for cmndname, c in cmnds.iteritems():
        if c.modname == modname: del cmndtable.data[cmndname]
    cmndtable.save()

def getcmndtable():
    """ save command -> plugin list to db backend. """
    global cmndtable
    if not cmndtable: boot()
    return cmndtable.data

## callbacks related commands

def savecallbacktable(modname=None):
    """ save command -> plugin list to db backend. """
    if modname: logging.warn("boot - module name is %s" % modname)
    global callbacktable
    assert callbacktable
    if not callbacktable.data: callbacktable.data = {}
    if modname: target = LazyDict(callbacktable.data)
    else: target = LazyDict()
    from jsb.lib.callbacks import first_callbacks, callbacks, last_callbacks, remote_callbacks
    for cb in [first_callbacks, callbacks, last_callbacks, remote_callbacks]:
        for type, cbs in cb.cbs.iteritems():
            for c in cbs:
                if modname and c.modname != modname: continue
                if not target.has_key(type): target[type] = []
                if not c.modname in target[type]: target[type].append(c.modname)
    logging.warn("saving callback table")
    assert callbacktable
    assert target
    callbacktable.data = target
    callbacktable.save()

def removecallbacks(modname):
    """ remove callbacks belonging to modname form cmndtable. """
    global callbacktable
    assert callbacktable
    from jsb.lib.callbacks import first_callbacks, callbacks, last_callbacks, remote_callbacks
    for cb in [first_callbacks, callbacks, last_callbacks, remote_callbacks]:
        for type, cbs in cb.cbs.iteritems():
            for c in cbs:
                if not c.modname == modname: continue
                if not callbacktable.data.has_key(type): callbacktable.data[type] = []
                if c.modname in callbacktable.data[type]: callbacktable.data[type].remove(c.modname)
    logging.warn("saving callback table")
    assert callbacktable
    callbacktable.save()

def getcallbacktable():
    """ save command -> plugin list to db backend. """
    global callbacktable
    if not callbacktable: boot()
    return callbacktable.data

## plugin list related commands

def savepluginlist(modname=None):
    """ save a list of available plugins to db backend. """
    global pluginlist
    if not pluginlist.data: pluginlist.data = []
    if modname: target = cpy(pluginlist.data)
    else: target = []
    from jsb.lib.commands import cmnds
    assert cmnds
    for cmndname, c in cmnds.iteritems():
        if modname and c.modname != modname: continue
        if c and not c.plugname: logging.info("boot - not adding %s to pluginlist" % cmndname) ; continue
        if c and c.plugname not in target: target.append(c.plugname)
    assert target
    target.sort()
    logging.warn("saving plugin list")
    assert pluginlist
    pluginlist.data = target
    pluginlist.save()

def remove_plugin(modname):
    removecmnds(modname)
    removecallbacks(modname)
    global pluginlist
    try: pluginlist.data.remove(modname.split(".")[-1]) ; pluginlist.save()
    except: pass

def clear_tables():
    global cmndtable
    global callbacktable
    global pluginlist
    cmndtable.data = {} ; cmndtable.save()
    callbacktable.data = {} ; callbacktable.save()
    pluginlist.data = [] ; pluginlist.save()

def getpluginlist():
    """ get the plugin list. """
    global pluginlist
    if not pluginlist: boot()
    l = plugwhitelist.data or pluginlist.data
    result = []
    denied = []
    for plug in plugblacklist.data:
        denied.append(plug.split(".")[-1])
    for plug in l:
        if plug not in denied: result.append(plug)
    return result

## update_mod command

def update_mod(modname):
    """ update the tables with new module. """
    savecallbacktable(modname)
    savecmndtable(modname, saveperms=False)
    savepluginlist(modname)

def whatcommands(plug):
    tbl = getcmndtable()
    result = []
    for cmnd, mod in tbl.iteritems():
        if not mod: continue
        if plug in mod:
            result.append(cmnd)
    return result

def getcmndperms():
    return cmndperms

def plugenable(mod):
    if plugwhitelist.data and not mod in plugwhitelist.data: plugwhitelist.data.append(mod) ; plugwhtelist.save() ; return
    if mod in plugblacklist.data: plugblacklist.data.remove(mod) ; plugblacklist.save()

def plugdisable(mod):
    if plugwhitelist.data and mod in plugwhitelist.data: plugwhitelist.data.remove(mod) ; plugwhtelist.save() ; return
    if not mod in plugblacklist.data: plugblacklist.data.append(mod) ; plugblacklist.save()

    