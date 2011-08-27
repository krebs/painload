# jsb/utils/source.py
#
#

""" get the location of a source """

## basic imports

import os
import logging
import sys

## getsource function

def getsource(mod):
    if not os.getcwd() in sys.path: sys.path.insert(0, os.getcwd())
    source = None
    splitted = mod.split(".")
    if len(splitted) == 1: splitted.append("")
    thedir = mod.replace(".", os.sep)
    if os.path.isdir(thedir): source = thedir
    if source and os.path.exists(source):
        logging.info("datadir - source is %s" % source)
        return source
    if not source:
        try:
            import pkg_resources
            source = pkg_resources.resource_filename(".".join(splitted[:len(splitted)-1]), splitted[-1])
        except ImportError:
            try:
                import jsb.contrib.pkg_resources as pkg_resources
                source = pkg_resources.resource_filename(".".join(splitted[:len(splitted)-1]), splitted[-1])
            except ImportError: pass
    logging.info("datadir - source is %s" % source)
    return source
