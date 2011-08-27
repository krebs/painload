# jsb/exit.py
#
#

""" jsb's finaliser """

## jsb imports

from jsb.utils.locking import globallocked
from jsb.utils.exception import handle_exception
from jsb.utils.trace import whichmodule
from jsb.memcached import killmcdaemon
from jsb.lib.persist import cleanup
from runner import defaultrunner, cmndrunner, callbackrunner, waitrunner

## basic imports

import atexit
import os
import time
import sys
import logging

## functions

@globallocked
def globalshutdown():
    """ shutdown the bot. """
    try:
        logging.warn('shutting down'.upper())
        sys.stdout.write("\n")
        from fleet import getfleet
        fleet = getfleet()
        if fleet:
            logging.warn('shutting down fleet')
            fleet.exit()
        logging.warn('shutting down plugins')
        from jsb.lib.plugins import plugs
        plugs.exit()
        logging.warn("shutting down runners")
        cmndrunner.stop()
        callbackrunner.stop()
        waitrunner.stop()
        logging.warn("cleaning up any open files")
        while cleanup(): time.sleep(1)
        try: os.remove('jsb.pid')
        except: pass
        killmcdaemon()
        time.sleep(0.5)
        logging.warn('done')
        os._exit(0)
    except Exception, ex: handle_exception() ; os._exit(1)

