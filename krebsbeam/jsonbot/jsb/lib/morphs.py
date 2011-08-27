# gozerbot/morphs.py
#
#

""" convert input/output stream. """

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.utils.trace import calledfrom

## basic imports

import sys
import logging

## Morph claas

class Morph(object):

    """ transform stream. """

    def __init__(self, func):
        self.modname = calledfrom(sys._getframe(1))
        self.func = func
        self.activate = True

    def do(self, *args, **kwargs):
        """ do the morphing. """
        if not self.activate: logging.warn("morphs - %s morph is not enabled" % str(self.func)) ; return
        #logging.warn("morphs - using morph function %s" % str(self.func))
        try: return self.func(*args, **kwargs)
        except Exception, ex: handle_exception()

class MorphList(list):

    """ list of morphs. """

    def add(self, func, index=None):
        """ add morph. """
        m = Morph(func)
        if not index: self.append(m)
        else: self.insert(index, m)
        logging.warn("morphs - added morph function %s - %s" % (str(func), m.modname))
        return self

    def do(self, input, *args, **kwargs):
        """ call morphing chain. """
        for morph in self: input = morph.do(input, *args, **kwargs) or input
        return input

    def unload(self, modname):
        """ unload morhps belonging to plug <modname>. """
        for index in range(len(self)-1, -1, -1):
            if self[index].modname == modname: del self[index]

    def disable(self, modname):
        """ disable morhps belonging to plug <modname>. """
        for index in range(len(self)-1, -1, -1):
            if self[index].modname == modname: self[index].activate = False

    def activate(self, plugname):
        """ activate morhps belonging to plug <plugname>. """
        for index in range(len(self)-1, -1, -1):
            if self[index].modname == modname: self[index].activate = True

## global morphs

inputmorphs = MorphList()
outputmorphs = MorphList()
