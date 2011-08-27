# jsb/gatekeeper.py
#
#

""" keep a whitelist of allowed entities based on userhost. """

## jsb imports

from jsb.lib.persist import Persist
from jsb.lib.datadir import getdatadir

## basic imports

import logging
import os

## GateKeeper class

class GateKeeper(Persist):

    """ keep a whitelist of allowed entities based on userhost. """

    def __init__(self, name):
        self.name = name
        try: import waveapi
        except:
            if not os.path.exists(getdatadir() + os.sep +'gatekeeper'): os.mkdir(getdatadir() + os.sep + 'gatekeeper')
        Persist.__init__(self, getdatadir() + os.sep + 'gatekeeper' + os.sep + name)
        self.data.whitelist = self.data.whitelist or []

    def isblocked(self, userhost):
        """ see if userhost is blocked. """
        if not userhost: return False
        userhost = userhost.lower()
        if userhost in self.data.whitelist:
            logging.debug("%s - allowed %s" % (self.fn, userhost))
            return False
        logging.warn("%s - denied %s" % (self.fn, userhost))
        return True

    def allow(self, userhost):
        """ allow userhost. """
        userhost = userhost.lower()
        if not userhost in self.data.whitelist:
            self.data.whitelist.append(userhost)
            self.save()

    def deny(self, userhost):
        """ deny access. """
        userhost = userhost.lower()
        if userhost in self.data.whitelist: self.data.whitelist.remove(userhost)
