# jsb/cache.py
#
#

""" jsb cache provding get, set and delete functions. """

## basic imports

import logging

## defines

cache = {}

## functions

def get(name, namespace=""):
    """ get data from the cache. """
    global cache
    try: 
        data = cache[name]
        if data: logging.debug("cache - returning %s" % name) ; return data
    except KeyError: pass

def set(name, item, timeout=0, namespace=""):
    """ set data in the cache. """
    logging.debug("cache - setting %s (%s)" % (name, len(item)))
    global cache
    cache[name] = item

def delete(name, namespace=""):
    """ delete data from the cache. """
    try:
        global cache
        del cache[name]
        logging.warn("cache - deleted %s" % name)
        return True
    except KeyError: return False
