# jsb/jsbimport.py
#
#

""" use the imp module to import modules. """

## basic imports

import time
import sys
import imp
import os
import thread
import logging

## _import function

def _import(name):
    """ do a import (full). """
    mods = []
    mm = ""
    for m in name.split('.'):
        mm += m
        mods.append(mm)
        mm += "."
    for mod in mods: imp = __import__(mod)
    logging.debug("jsbimport - got module %s" % sys.modules[name])
    return sys.modules[name]

## force_import function

def force_import(name):
    """ force import of module <name> by replacing it in sys.modules. """
    try: del sys.modules[name]
    except KeyError: pass
    plug = _import(name)
    return plug

def _import_byfile(modname, filename):
    try: return imp.load_source(modname, filename)
    except NotImplementedError: return _import(filename[:-3].replace(os.sep, "."))

