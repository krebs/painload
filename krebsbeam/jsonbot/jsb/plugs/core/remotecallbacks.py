# jsb/plugs/core/remotecallbacks.py
#
#

""" dispatch remote events. """

## jsb imports

from jsb.utils.lazydict import LazyDict
from jsb.utils.generic import fromenc
from jsb.utils.exception import handle_exception
from jsb.lib.callbacks import callbacks, remote_callbacks, first_callbacks
from jsb.lib.container import Container
from jsb.lib.eventbase import EventBase
from jsb.lib.errors import NoProperDigest
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.contrib.xmlstream import NodeBuilder, XMLescape, XMLunescape

## basic imports

import logging
import copy
import hmac
import hashlib
import cgi

## defines

cpy = copy.deepcopy

## callback

def remotecb(bot, event):
    """ dispatch an event. """
    try: container = Container().load(event.txt)
    except TypeError:
        handle_exception()
        logging.warn("remotecallbacks - not a remote event - %s " % event.userhost)
        return
    logging.debug('doing REMOTE callback')
    try:
        digest = hmac.new(str(container.hashkey), XMLunescape(container.payload), hashlib.sha512).hexdigest()
        logging.debug("remotecallbacks - digest is %s" % digest)
    except TypeError:
        handle_exception()
        logging.error("remotecallbacks - can't load payload - %s" % container.payload)
        return
    if container.digest == digest: e = EventBase().load(XMLunescape(container.payload))
    else: raise NoProperDigest()
    e.txt = XMLunescape(e.txt)
    e.nodispatch = True
    e.forwarded = True
    bot.doevent(e)
    event.status = "done"  
    return

remote_callbacks.add("MESSAGE", remotecb)
