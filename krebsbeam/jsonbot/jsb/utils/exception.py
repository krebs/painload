# jsb/utils/exception.py
#
#

""" exception related functions. """

## basic imports

import sys
import traceback
import logging
import thread
import os
import logging

## defines

exceptionlist = []
exceptionevents = []

ERASE_LINE = '\033[2K'
BOLD='\033[1m'
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
ENDC = '\033[0m'


## exceptionmsg function

def exceptionmsg():
    """ create exception message as a string. """
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = ""
    for i in trace:
        fname = i[0]
        linenr = i[1]
        func = i[2]
        plugfile = fname[:-3].split(os.sep)
        mod = []
        for i in plugfile[::-1]:
            if i in ['jsb.upload']: break
            mod.append(i)
            if i in ['jsb', 'waveapi', 'google', 'data']: break
        ownname = '.'.join(mod[::-1])
        result += "%s:%s %s | " % (ownname, linenr, func)
    del trace
    res = "%s%s: %s" % (result, exctype, excvalue)
    if res not in exceptionlist: exceptionlist.append(res)
    return res

## handle_exception function

def handle_exception(event=None, log=True, txt="", stop=False):
    """ handle exception.. for now only print it. """
    errormsg = exceptionmsg()
    if txt: errormsg = "%s - %s" % (txt, errormsg)
    if log: logging.error(RED + txt + " " + errormsg + ENDC)
    if event:
        exceptionevents.append((event, errormsg))
        if event.bot:
            event.bot.error = errormsg
            if event.bot.type == "irc": target = event.nick
            else: target = event.channel 
            if target: event.bot.saynocb(target, "*sorry* - an exception occured - %s" % errormsg)
    if stop: os._exit(1)
