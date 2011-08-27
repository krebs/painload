# jsb/less.py
#
#

""" maintain bot output cache. """

# jsb imports

from jsb.utils.exception import handle_exception
from jsb.utils.limlist import Limlist

## google imports

try:
    import waveapi
    from google.appengine.api.memcache import get, set, delete
except ImportError:
    from jsb.lib.cache import get, set, delete

## basic imports

import logging


## Less class

class Less(object):

    """ output cache .. caches upto <nr> item of txt lines per channel. """

    def clear(self, channel):
        """ clear outcache of channel. """
        channel = unicode(channel).lower()
        try: delete(u"outcache-" + channel) 
        except KeyError: pass

    def add(self, channel, listoftxt):
        """ add listoftxt to channel's output. """
        channel = unicode(channel).lower()
        data = get("outcache-" + channel)
        if not data: data = []
        data.extend(listoftxt)
        set(u"outcache-" + channel, data, 3600)

    def set(self, channel, listoftxt):
        """ set listoftxt to channel's output. """
        channel = unicode(channel).lower()
        set(u"outcache-" + channel, listoftxt, 3600)

    def get(self, channel):
        """ return 1 item popped from outcache. """
        channel = unicode(channel).lower()
        global get
        data = get(u"outcache-" + channel)
        if not data: txt = None
        else: 
            try: txt = data.pop(0) ; set(u"outcache-" + channel, data, 3600)
            except (KeyError, IndexError): txt = None
        if data: size = len(data)
        else: size = 0
        return (txt, size)

    def copy(self, channel):
        """ return 1 item popped from outcache. """
        channel = unicode(channel).lower()
        global get
        return get(u"outcache-" + channel)

    def more(self, channel):
        """ return more entry and remaining size. """
        return self.get(channel)

outcache = Less()