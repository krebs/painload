# jsb/utils/log.py
#
#

""" log module. """

## jsb import

from jsb.lib.config import getmainconfig
from jsb.lib.datadir import getdatadir

## basic imports

import logging
import logging.handlers
import os
import os.path
import getpass

## defines

ERASE_LINE = '\033[2K'
BOLD='\033[1m'
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
ENDC = '\033[0m'


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'warn': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL
         }

RLEVELS = {logging.DEBUG: 'debug',
           logging.INFO: 'info',
           logging.WARNING: 'warn',
           logging.ERROR: 'error',
           logging.CRITICAL: 'critical'
          }

def init(d):
    try:
        import waveapi
    except ImportError:
        LOGDIR = d + os.sep + "botlogs" # BHJTW change this for debian

    try:
        ddir = os.sep.join(LOGDIR.split(os.sep)[:-1])
        if not os.path.isdir(ddir): os.mkdir(ddir)
    except: pass

    try:
        if not os.path.isdir(LOGDIR): os.mkdir(LOGDIR)
    except: pass
    return LOGDIR

## setloglevel function

def setloglevel(level_name="warn", colors=False, datadir=None):
    """ set loglevel to level_name. """
    if not level_name: return
    LOGDIR = init(datadir or getdatadir())
    format_short = "\033[94m[!]\033[0m\033[0m \033[97m%(asctime)-8s\033[0m - \033[92m%(module)+12s\033[0m - \033[93m%(message)s\033[0m"
    format = "\033[94m[!]\033[0m\033[0m \033[97m%(asctime)s.%(msecs)-13s\033[0m - \033[92m%(lineno)-5s%(module)+12s.%(funcName)-15s\033[0m - \033[93m%(message)s\033[0m - %(levelname)s - <%(threadName)s>"
    format_short_plain = "[!] %(asctime)-8s - %(module)+12s - %(message)s"
    format_plain = "[!] %(asctime)s.%(msecs)-13s - %(lineno)-5s%(module)+12s.%(funcName)-15s - %(message)s - %(levelname)s - <%(threadName)s>"
    datefmt = '%H:%M:%S'
    formatter_short = logging.Formatter(format_short, datefmt=datefmt)
    formatter = logging.Formatter(format, datefmt=datefmt)
    formatter_short_plain = logging.Formatter(format_short_plain, datefmt=datefmt)
    formatter_plain = logging.Formatter(format_plain, datefmt=datefmt)
    try:
        import waveapi
    except ImportError:
        try:
            filehandler = logging.handlers.TimedRotatingFileHandler(LOGDIR + os.sep + "jsb.log", 'midnight')
        except (IOError, AttributeError), ex:
            logging.error("can't create file loggger %s" % str(ex))
            filehandler = None
    mainconfig = getmainconfig()
    docolors = colors or mainconfig.color
    level = LEVELS.get(str(level_name).lower(), logging.NOTSET)
    root = logging.getLogger()
    root.setLevel(level)
    if root and root.handlers:
        for handler in root.handlers: root.removeHandler(handler)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    if level_name in ["debug", "info"]: 
         if docolors: ch.setFormatter(formatter)
         else: ch.setFormatter(formatter_plain)
         if filehandler: filehandler.setFormatter(formatter_plain)
    else:
         if docolors: ch.setFormatter(formatter_short)
         else: ch.setFormatter(formatter_short_plain)
         if filehandler: filehandler.setFormatter(formatter_short_plain)
    try: import waveapi
    except ImportError:
        root.addHandler(ch)
        if filehandler: root.addHandler(filehandler)
    logging.warn("loglevel is %s (%s)" % (str(level), level_name))
    if colors: mainconfig.color = True ; mainconfig.save()

def getloglevel():
    import logging
    root = logging.getLogger()
    return RLEVELS.get(root.level)
