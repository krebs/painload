# jsb/compat/persistconfig.py
#
#

""" allow data to be pickled to disk .. creating the persisted object
    restores data
    
usage:
    !plug-cfg			->	shows list of all config
    !plug-cfg key value		->	sets value to key
    !plug-cfg key		->	shows list of key
    !plug-cfg key add value	->	adds value to list
    !plug-cfg key remove value	->	removes value from list
    !plug-cfg key clear		-> 	clears entire list
    !plug-cfgsave		->	force save configuration to disk
    
todo:
    - plugin api (more work needed?)
    
"""

__copyright__ = 'this file is in the public domain'
__author__ = 'Bas van Oostveen'

## jsb imports

from jsb.utils.trace import calledfrom
from jsb.compat.persist import Persist
from jsb.lib.commands import cmnds, Command
from jsb.lib.datadir import datadir

## basic imports

import sys
import os
import types
import time

## Option class

class Option(object):

    def __init__(self, value, desc, perm, example, name, exposed):
        assert isinstance(name, str), "Option.self.name must be a string"
        self.value = value
        self.desc = desc
        self.perm = perm
        self.example = example
        self.name = name.lower()
        self.exposed = exposed

    def __casattr__(self, name, val):
        # Update option if needed
        if not hasattr(self, name):
            setattr(self, name, val)
            return True
        else:
            #if val and getattr(self, name)!=val: # old style
            if val != None and type(getattr(self, name)) != type(val):
                setattr(self, name, val)
                return True
            return False

    def check(self, key, plugname, value, desc, perm, example, name, exposed):
        upd = False
        # maybe checking value is too much here
        if self.__casattr__("value", value): upd = True
        if self.__casattr__("example", example): upd = True
        if self.__casattr__("name", name): upd = True
        if self.__casattr__("perm", perm): upd = True
        if self.__casattr__("exposed", exposed): upd = True
        if self.name == None:
            self.name = "%s-cfg-%s" % (plugname, str(key))
            upd = True
        return upd

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __gt__(self, other):
        return self.value >= other

    def __ge__(self, other):
        return self.value >= other

## LazyValyeDict class

class LazyValueDict(object):

    """ emulates the normal Persist.data (key, value) dict """

    def __init__(self, cfg):
        self.__cfg = cfg

    def __len__(self):
        return len(self.__persistData)

    def __getitem__(self, key):
        return self.__cfg.data[key].value

    def __setitem__(self, key, value):
        if not self.__cfg.data.has_key(key) or not \
isinstance(self.__cfg.data[key], Option):
            name = "%s-cfg-%s" % (self.__cfg.plugname, str(key))
            self.__cfg.define(value, "", 'OPER', "", name, exposed=False)
        self.__cfg.set(key, value)

    def __delitem__(self, key):
        raise Exception("Direct deletion not supported, use \
persistConfig.undefine()")

    def __iter__(self):
        return self.__cfg.data.__iter__()

    def iterkeys(self):
        return self.__iter__()

    def __contains__(self, item):
        return self.__cfg.data.has_key(item)

## PersistConfigError class

class PersistConfigError(Exception): pass

## PersistConfig clas

class PersistConfig(Persist):

    """ persist plugin configuration and create default handlers """

    def __init__(self):
        self.__basename__ = self.__class__.__name__
        self.plugname = calledfrom(sys._getframe())
        Persist.__init__(self, os.path.join(datadir, "%s-config" % self.plugname), {})
        self.__callbacks = {}
        cmndname = "%s-cfg" % self.plugname
        logging.info('added command %s (%s)' % (cmndname, self.plugname))
        cmnds[cmndname] = Command(self.cmnd_cfg, 'OPER', self.plugname, threaded=True)	
        examples.add(cmndname, "plugin configuration", cmndname)
        cmndnamesave = cmndname + "save"
        cmnds[cmndnamesave] = Command(self.cmnd_cfgsave, 'OPER', self.plugname, threaded=True)	
        examples.add(cmndnamesave, "save plugin configuration", cmndnamesave)

    def __getattribute__(self, name):
        # make sure the attribute data is not called from Persist or 
        # PersistConfig returning a persist compatible (key, value) dict 
        # instead of the rich persistconfig
        cf = calledfrom(sys._getframe())
        ## (key, option(value, ...)) is only for persistconfig internal usage.
        if name == "data" and cf != "persistconfig" and cf != "persist" and cf != self.__basename__:
            # intercept data block, return a clean dict with lazy binding 
            # to option.value
            return LazyValueDict(self)
        return super(PersistConfig, self).__getattribute__(name)

    def handle_callback(self, event, key, value=None):
        if self.__callbacks.has_key((key, event)):
            cb, extra_data = self.__callbacks[(key, event)]
            if callable(cb):
                cb(key, value, event, extra_data)
            else:
                logging.warn('invalid callback for %s %s' % (key, event))
                del self.__callbacks[(key, event)]

    ### cmnds

    def show_cfg(self, bot, ievent):
        s = []
        for key, option in sorted(self.data.items()):
            if not isinstance(option, Option):
                logging.warn('Option %s is not a valid option' % key)
                continue
            if not option.exposed:
                continue
            v = option.value
            if type(v) in [str, unicode]:
                v = '"'+v+'"'
            v = str(v)
            s.append("%s=%s" % (key, v))
        ievent.reply("options: " + ' .. '.join(s))

    def cmnd_cfgsave(self, bot, ievent):
        self.save()
        ievent.reply("config saved")
	
    def cmnd_cfg_edit(self, bot, ievent, args, key, option):
        if type(option.value) == types.ListType:
	    if args[0].startswith("[") and args[-1].endswith("]"):
		values = []
		for v in ' '.join(args)[1:-1].replace(", ", ",").split(","):
		    if v[0]=='"' and v[-1]=='"':
			# string
			v = v.replace('"', '')
		    elif v[0]=="'" and v[-1]=="'":
			# string
			v = v.replace("'", "")
		    elif '.' in v:
			# float
			try:
			    v = float(v)
			except ValueError:
			    ievent.reply("invalid long literal: %s" % v)
			    return
		    else:
			# int
			try:
			    v = int(v)
			except ValueError:
			    ievent.reply("invalid int literal: %s" % v)
			    return
		    values.append(v)
                self.set(key, values)
                ievent.reply("%s set %s" % (key, values))
		return
            command = args[0]
            value = ' '.join(args[1:])
            if command == "clear":
                self.clear(key)
                ievent.reply("list empty")
            elif command == "add":
                self.append(key, value)
                ievent.reply("%s added %s" % (key, value))
            elif command == "remove" or command == "del":
                try:
                    self.remove(key, value)
                    ievent.reply("%s removed" % str(value))
                except ValueError:
                    ievent.reply("%s is not in list" % str(value))
            else:
                ievent.reply("invalid command")
            return
        else:
            value = ' '.join(args)
            try:
                value = type(option.value)(value)
            except:
                pass
            if type(value) == type(option.value):
                self.set(key, value)
                ievent.reply("%s set" % key)
            elif type(value) == types.LongType and \
type(option.value) == types.IntType:
                # allow upscaling from int to long
                self.set(key, value)
                ievent.reply("%s set" % key)
            else:
                ievent.reply("value %s (%s) is not of the same type as %s \
(%s)" % (value, type(value), option.value, type(option.value)))
    
    def cmnd_cfg(self, bot, ievent):
        if not ievent.args:
            self.show_cfg(bot, ievent)
            return
        argc = len(ievent.args)
        key = ievent.args[0]
        try:
            option = self.data[key]
        except KeyError:
            ievent.reply("%s option %s not found" % (self.plugname, key))
            return
        if not isinstance(option, Option):
            logging.warn('Option %s is not a valid option' % key)
            return
        if not option.exposed:
            return
        if argc == 1:
            ievent.reply(str(option.value))
            return
        self.cmnd_cfg_edit(bot, ievent, ievent.args[1:], key, option)

    def generic_cmnd(self, key):
        def func(bot, ievent):
            try:
                option = self.data[key]
            except KeyError:
                ievent.reply("%s not found" % key)
                # need return ?
            if not isinstance(option, Option):
                logging.warn('Option %s is not a valid option' % key)
                return
            if ievent.args:
                value = ' '.join(ievent.args)
                try:
                    value = type(option.value)(value)
                except:
                    pass
                self.cmnd_cfg_edit(bot, ievent, ievent.args, key, option)
            else:
                ievent.reply(str(option.value))
        return func

    ### plugin api

    def define(self, key, value=None, desc="plugin option", perm='OPER', \
example="", name=None, exposed=True):
        if name:
            name = name.lower()
        if not self.data.has_key(key):
            if name == None:
                name = "%s-cfg-%s" % (self.plugname, str(key))
            option = Option(value, desc, perm, example, name, exposed)
            self.data[key] = option
            self.save()
        else:
            option = self.data[key]
            # if unpickled option is not of class Option recreate the option
            # also if the type of value has changed recreate the option
            # exception if value got upgraded from int to long, then nothing 
            # has to be changed
            if not isinstance(option, Option):
                if name == None:
                    name = "%s-cfg-%s" % (self.plugname, str(key))
                if type(value) == type(option):
                    value = option
                option = Option(value, desc, perm, example, name, exposed)
                self.data[key] = option
                self.save()
            else:
                if type(option.value) == types.LongType and \
type(value) == types.IntType:
                    value = long(value)
                if option.check(key, self.plugname, value, desc, perm, \
example, name, exposed):
                    self.data[key] = option
                    self.save()
	
    def undefine(self, key, throw=False):
        try:
            option = self.data[key]
            if option.exposed:
                if cmnds.has_key(option.name):
                    del cmnds[option.name]
                if examples.has_key(option.name):
                    del examples[option.name]
            del self.data[key]
            self.save()
            return True
        except KeyError, e:
            if throw:
                raise
        return False

    def checkoption(self, key):
        if not isinstance(self.data[key], Option):
            raise PersistConfigError("Option %s is not a valid option" % key)
        return True

    def set(self, key, value, throw=False):
        if type(value)==unicode:
            value = str(value)
        try:
            self.checkoption(key)
        except (KeyError, PersistConfigError):
            if throw:
                raise
            self.define(key, value)
            self.handle_callback('change', key, value)
        else:
            self.data[key].value = value
            self.handle_callback('change', key, value)
            self.save()

    def append(self, key, value):
        self.checkoption(key)
        self.data[key].value.append(value)
        self.save()
        self.handle_callback('change', key, value)
        self.handle_callback('add', key, value)

    def remove(self, key, value):
        self.checkoption(key)
        self.data[key].value.remove(value)
        self.save()
        self.handle_callback('change', key, value)
        self.handle_callback('remove', key, value)

    def clear(self, key):
        self.checkoption(key)
        self.data[key].value = []
        self.save()
        self.handle_callback('change', key, [])
        self.handle_callback('clear', key)

    def get(self, key, default=None):
        try:
            return self.data[key].value
        except KeyError:
            return default

    def has_key(self, key):
        return self.data.has_key(key)

    def callback(self, key, event, callback, extra_data=None):
        callbacks = ["change", "add", "remove", "clear"]
        if not event in callbacks:
            raise PersistConfigError("Unsupported callback event %s" % event)
        self.__callbacks[(key, event)] = (callback, extra_data)
    
    def syncold(self, filename, remove=False):
        """ sync with old config data """
        if os.path.isfile(filename):
            synckey = "persistconfig-syncold"
            oldconfig = Persist(filename)
            if not oldconfig.data.has_key(synckey):
                logging.warn("syncing old config %s with persistconfig" % filename)
                for i, j in oldconfig.data.iteritems():
                    if i == synckey:
                        continue
                    if j and not self.get(i):
                        self.set(i, oldconfig.data[i])
                oldconfig.data[synckey] = time.localtime()
                oldconfig.save()
            del oldconfig
            if remove:
                os.unlink(filename)

