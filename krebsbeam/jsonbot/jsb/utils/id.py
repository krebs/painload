# jsb/utils/id.py
#
#

""" id related functions. """

## jsb imports

from jsb.utils.generic import toenc

## basic imports

import uuid

## getrssid function

def getrssid(url, time):
    """ get an id based on url and time. """
    key = unicode(url) + unicode(time)
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, toenc(key)))
