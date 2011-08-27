# gozerbot/persistconfig.py
#
#

""" plugin related config file with commands added to the bot to config a plugin.
    
usage:
    !plug-cfg			->	shows list of all config
    !plug-cfg key value		->	sets value to key
    !plug-cfg key		->	shows list of key
    !plug-cfg key add value	->	adds value to list
    !plug-cfg key remove value	->	removes value from list
    !plug-cfg key clear		-> 	clears entire list
    !plug-cfgsave		->	force save configuration to disk
    
"""

__copyright__ = 'this file is in the public domain'
__author__ = 'Bas van Oostveen'

## jsb imports

from jsb.utils.lazydict import LazyDict
from jsb.utils.trace import calledfrom, whichplugin
from jsb.lib.examples import examples
from jsb.lib.persist import Persist
from jsb.lib.config import Config
from jsb.imports import getjson

## basic imports

import sys
import os
import types
import time
import logging

## PersistConfigError exception

class PersistConfigError(Exception): pass

## class Option .. is for gozerbot compat

class Option(object): pass


## PersistConfig class

class PersistConfig(Config):

    """ persist plugin configuration and create default handlers. """

    def __init__(self):
        self.hide = []
        modname = whichplugin()
        logging.debug("persistconfig - module name is %s" % modname)
        self.plugname = modname.split('.')[-1]
        Config.__init__(self, 'plugs' + os.sep + modname, "config")
        self.modname = modname
        cmndname = "%s-cfg" % self.plugname
        logging.debug('persistconfig - added command %s (%s)' % (cmndname, self.plugname))
        from jsb.lib.commands import cmnds, Command
        cmnds[cmndname] = Command(self.modname, cmndname, self.cmnd_cfg, ['OPER', ])
        examples.add(cmndname, "%s configuration" % self.plugname, cmndname)
        cmndnamesave = cmndname + "save"
        cmnds[cmndnamesave] = Command(self.modname, cmndname, self.cmnd_cfgsave, ['OPER',])
        examples.add(cmndnamesave, "save %s configuration" % self.plugname, cmndnamesave)

    ## cmnds

    def show_cfg(self, bot, ievent):
        """ show config options. """
        s = []
        dumpstr = self.tojson()
        logging.warn(dumpstr)
        for key, optionvalue in sorted(getjson().loads(dumpstr).iteritems()):
            if key in self.hide: continue
            v = optionvalue
            if type(v) in [str, unicode]: v = '"'+v+'"'
            v = str(v)
            s.append("%s=%s" % (key, v))
        ievent.reply("options: " + ' .. '.join(s))

    def cmnd_cfgsave(self, bot, ievent):
        """ save config. """
        self.save()
        ievent.reply("config saved")
	
    def cmnd_cfg_edit(self, bot, ievent, args, key, optionvalue):
        """ edit config values. """
        if not self.has_key(key):
            ievent.reply('option %s is not defined' % key)
            return
        if key in self.hide: return
        if type(optionvalue) == types.ListType:
	    if args[0].startswith("[") and args[-1].endswith("]"):
		values = []
		for v in ' '.join(args)[1:-1].replace(", ", ",").split(","):
		    if v[0]=='"' and v[-1]=='"': v = v.replace('"', '')
		    elif v[0]=="'" and v[-1]=="'": v = v.replace("'", "")
		    elif '.' in v:
			try: v = float(v)
			except ValueError:
			    ievent.reply("invalid long literal: %s" % v)
			    return
		    else:
			try: v = int(v)
			except ValueError:
			    ievent.reply("invalid int literal: %s" % v)
			    return
		    values.append(v)
                self.set(key, values)
                self.save()
                ievent.reply("%s set %s" % (key, values))
		return
            command = args[0]
            value = ' '.join(args[1:])
            if command == "clear":
                self.clear(key)
                self.save()
                ievent.reply("list empty")
            elif command == "add":
                self.append(key, value)
                self.save()
                ievent.reply("%s added %s" % (key, value))
            elif command == "remove" or command == "del":
                try:
                    self.remove(key, value)
                    self.save()
                    ievent.reply("%s removed" % str(value))
                except ValueError: ievent.reply("%s is not in list" % str(value))
            else: ievent.reply("invalid command")
            return

        else:
            value = ' '.join(args)
            try: value = type(optionvalue)(value)
            except: pass
            if type(value) == type(optionvalue):
                self.set(key, value)
                self.save()
                ievent.reply("%s set" % key)
            elif type(value) == types.LongType and type(option.value) == types.IntType:
                self.set(key, value)
                self.save()
                ievent.reply("%s set" % key)
            else:
                ievent.reply("value %s (%s) is not of the same type as %s (%s)" % (value, type(value), optionvalue, type(optionvalue)))
    
    def cmnd_cfg(self, bot, ievent):
        """ the config (cfg) command. """
        if not ievent.args:
            self.show_cfg(bot, ievent)
            return
        argc = len(ievent.args)
        key = ievent.args[0]
        try: optionvalue = self[key]
        except KeyError:
            ievent.reply("%s option %s not found" % (self.plugname, key))
            return
        if key in self.hide: return
        if argc == 1:
            ievent.reply(str(optionvalue))
            return
        self.cmnd_cfg_edit(bot, ievent, ievent.args[1:], key, optionvalue)

    def generic_cmnd(self, key):
        """ command for editing config values. """
        def func(bot, ievent):
            try: optionvalue = self[key]
            except KeyError:
                ievent.reply("%s not found" % key)
                return
            if not isinstance(option, Option):
                logging.warn('persistconfig - option %s is not a valid option' % key)
                return
            if ievent.args:
                value = ' '.join(ievent.args)
                try: value = type(optionvalue)(value)
                except: pass
                self.cmnd_cfg_edit(bot, ievent, ievent.args, key, optionvalue)
            else: ievent.reply(str(optionvalue))
        return func

    ### plugin api

    def define(self, key, value=None, desc="plugin option", perm='OPER', example="", name=None, exposed=True):
        """ define initial value. """
        if name: name = name.lower()
        if not exposed and not key in self.hide: self.hide.append(key)
        if not self.has_key(key):
            if name == None: name = "%s-cfg-%s" % (self.plugname, str(key))
            self[key] = value
	
    def undefine(self, key, throw=False):
        """ remove a key. """
        try:
            del self[key]
            return True
        except KeyError, e:
            if throw: raise
        self.save()
        return False

    def set(self, key, value, throw=False):
        """ set a key's value. """
        self[key] = value

    def append(self, key, value):
        """ append a value. """
        self[key].append(value)

    def remove(self, key, value):
        """ remove a value. """
        self[key].remove(value)

    def clear(self, key):
        """ clear a value. """
        self[key] = []

    def get(self, key, default=None):
        """ get value of key. """
        try: return self[key]
        except KeyError: return default
