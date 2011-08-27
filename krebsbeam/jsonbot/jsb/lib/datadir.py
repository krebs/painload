# jsb/datadir.py
#
#

""" the data directory of the bot. """

## jsb imports

from jsb.utils.source import getsource

## basic imports

import re
import os
import shutil
import logging
import os.path
import getpass

## the global datadir

try: homedir = os.path.abspath(os.path.expanduser("~"))
except: homedir = os.getcwd()

isgae = False

try: getattr(os, "mkdir") ; logging.info("datadir - shell detected") ; datadir = homedir + os.sep + ".jsb"
except AttributeError: logging.info("datadir - skipping makedirs") ; datadir = "data" ; isgae = True

## helper functions

def touch(fname):
    """ touch a file. """
    fd = os.open(fname, os.O_WRONLY | os.O_CREAT)
    os.close(fd)

def doit(ddir, mod, target=None):
    source = getsource(mod)
    if not source: raise Exception("can't find %s package" % mod)
    shutil.copytree(source, ddir + os.sep + (target or mod.replace(".", os.sep)))


## makedir function

def makedirs(ddir=None):
    """ make subdirs in datadir. """
    #if os.path.exists("/home/jsb/.jsb") and getpass.getuser() == 'jsb': ddir = "/home/jsb/.jsb"
    global datadir
    datadir = ddir or getdatadir()
    logging.warn("datadir - set to %s" % datadir)
    if isgae: return
    if not os.path.isdir(ddir):
        try: os.mkdir(ddir)
        except: logging.warn("can't make %s dir" % ddir) ; os._exit(1)
        logging.info("making dirs in %s" % ddir)
    try: os.chmod(ddir, 0700)
    except: pass
    if ddir: setdatadir(ddir)
    last = datadir.split(os.sep)[-1]
    #if not os.path.isdir(ddir): doit(ddir, "jsb.data")
    try: doit(ddir, "jsb.plugs.myplugs")
    except: pass
    try: doit(ddir, "jsb.data.examples")
    except: pass
    try: doit(ddir, "jsb.data.static", "static")
    except: pass
    try: doit(ddir, "jsb.data.templates", "templates")
    except: pass
    try: touch(ddir + os.sep + "__init__.py")
    except: pass
    if not os.path.isdir(ddir + os.sep + "config"): os.mkdir(ddir + os.sep + "config")
    if not os.path.isfile(ddir + os.sep + 'config' + os.sep + "mainconfig"):
        source = getsource("jsb.data.examples")
        if not source: raise Exception("can't find jsb.data.examples package")
        try: shutil.copy(source + os.sep + 'mainconfig.example', ddir + os.sep + 'config' + os.sep + 'mainconfig')
        except (OSError, IOError), ex: logging.error("datadir - failed to copy jsb.data.config.mainconfig: %s" % str(ex))
    if not os.path.isfile(ddir + os.sep + 'config' + os.sep + "credentials.py"):
        source = getsource("jsb.data.examples")
        if not source: raise Exception("can't find jsb.data.examples package")
        try: shutil.copy(source + os.sep + 'credentials.py.example', ddir + os.sep + 'config' + os.sep + 'credentials.py')
        except (OSError, IOError), ex: logging.error("datadir - failed to copy jsb.data.config: %s" % str(ex))
    try: touch(ddir + os.sep + "config" + os.sep + "__init__.py")
    except: pass
    # myplugs
    initsource = getsource("jsb.plugs.myplugs")
    if not initsource: raise Exception("can't find jsb.plugs.myplugs package")
    initsource = initsource + os.sep + "__init__.py"
    if not os.path.isdir(ddir + os.sep + 'myplugs'): os.mkdir(ddir + os.sep + 'myplugs')
    if not os.path.isfile(ddir + os.sep + 'myplugs' + os.sep + "__init__.py"):
        try:
            shutil.copy(initsource, os.path.join(ddir, 'myplugs', '__init__.py'))
        except (OSError, IOError), ex: logging.error("datadir - failed to copy myplugs/__init__.py: %s" % str(ex))
    # myplugs.common
    if not os.path.isdir(os.path.join(ddir, 'myplugs', 'common')): os.mkdir(os.path.join(ddir, 'myplugs', 'common'))
    if not os.path.isfile(os.path.join(ddir, 'myplugs', "common", "__init__.py")):
        try:
            shutil.copy(initsource, os.path.join(ddir, 'myplugs', 'common', '__init__.py'))
        except (OSError, IOError), ex: logging.error("datadir - failed to copy myplugs/common/__init__.py: %s" % str(ex))
    # myplugs.gae
    if not os.path.isdir(os.path.join(ddir, 'myplugs', 'gae')): os.mkdir(os.path.join(ddir, 'myplugs', 'gae'))
    if not os.path.isfile(os.path.join(ddir, 'myplugs', "gae", "__init__.py")):
        try:
            shutil.copy(initsource, os.path.join(ddir, 'myplugs', 'gae', '__init__.py'))
        except (OSError, IOError), ex: logging.error("datadir - failed to copy myplugs/gae/__init__.py: %s" % str(ex))
    # myplugs.socket
    if not os.path.isdir(os.path.join(ddir, 'myplugs', 'socket')): os.mkdir(os.path.join(ddir, 'myplugs', 'socket'))
    if not os.path.isfile(os.path.join(ddir, 'myplugs', 'socket', "__init__.py")):
        try:
            shutil.copy(initsource, os.path.join(ddir, 'myplugs', 'socket', '__init__.py'))
        except (OSError, IOError), ex: logging.error("datadir - failed to copy myplugs/socket/__init__.py: %s" % str(ex))
    if not os.path.isdir(ddir + os.sep +'botlogs'): os.mkdir(ddir + os.sep + 'botlogs')
    if not os.path.isdir(ddir + '/run/'): os.mkdir(ddir + '/run/')
    if not os.path.isdir(ddir + '/users/'): os.mkdir(ddir + '/users/')
    if not os.path.isdir(ddir + '/channels/'): os.mkdir(ddir + '/channels/')
    if not os.path.isdir(ddir + '/fleet/'): os.mkdir(ddir + '/fleet/')
    if not os.path.isdir(ddir + '/pgp/'): os.mkdir(ddir + '/pgp/')
    if not os.path.isdir(ddir + '/plugs/'): os.mkdir(ddir + '/plugs/')
    if not os.path.isdir(ddir + '/old/'): os.mkdir(ddir + '/old/')
    if not os.path.isdir(ddir + '/containers/'): os.mkdir(ddir + '/containers/')
    if not os.path.isdir(ddir + '/chatlogs/'): os.mkdir(ddir + '/chatlogs/')
    if not os.path.isdir(ddir + '/botlogs/'): os.mkdir(ddir + '/botlogs/')

def getdatadir():
    global datadir
    return datadir

def setdatadir(ddir):
    global datadir
    datadir = ddir
