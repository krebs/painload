# jsb/lib/aliases.py
#
#

""" global aliases. """

## jsb imports

from jsb.lib.datadir import getdatadir

## basic imports

import os

## getaliases function

def getaliases():
    """ return global aliases. """
    from jsb.lib.persist import Persist
    p = Persist(getdatadir() + os.sep + "aliases")
    if not p.data: p.data = {}
    return p