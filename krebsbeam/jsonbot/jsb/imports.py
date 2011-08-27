# jsb/imports.py
#
#

""" provide a import wrappers for the contrib packages. """

## lib imports

from lib.jsbimport import _import

## basic imports

import logging

## getdns function

def getdns():
    try:
        mod = _import("dns")
    except: mod = _import("jsb.contrib.dns")
    logging.debug("imports - dns module is %s" % str(mod))
    return mod

## getjson function

def getjson():
    try:
        import wave
        mod = _import("jsb.contrib.simplejson")
    except ImportError:
        try: mod = _import("json")
        except:
            try:
                mod = _import("simplejson")
            except:
                mod = _import("jsb.contrib.simplejson")
    logging.debug("imports - json module is %s" % str(mod))
    return mod

## getfeedparser function

def getfeedparser():
    try: mod = _import("feedparser")
    except:
        mod = _import("jsb.contrib.feedparser")
    logging.info("imports - feedparser module is %s" % str(mod))
    return mod

def getoauth():
    try: mod = _import("oauth")
    except:
        mod = _import("jsb.contrib.oauth")
    logging.info("imports - oauth module is %s" % str(mod))
    return mod

def getrequests():
    try: mod = _import("requests")
    except:
        mod = _import("jsb.contrib.requests")
    logging.info("imports - requests module is %s" % str(mod))
    return mod

def gettornado():
    try: mod = _import("tornado")
    except:
        mod = _import("jsb.contrib.tornado")
    logging.info("imports - tornado module is %s" % str(mod))
    return mod
