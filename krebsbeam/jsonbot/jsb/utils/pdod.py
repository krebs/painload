# gozerbot/pdod.py
#
#

""" pickled dicts of dicts """

## jsb imports

from jsb.utils.lazydict import LazyDict
from jsb.lib.persist import Persist

## Pdod class

class Pdod(Persist):

    """ pickled dicts of dicts """

    def __getitem__(self, name):
        """ return item with name """
        if self.data.has_key(name): return self.data[name]

    def __delitem__(self, name):
        """ delete name item """
        if self.data.has_key(name): return self.data.__delitem__(name)

    def __setitem__(self, name, item):
        """ set name item """
        self.data[name] = item

    def __contains__(self, name):
        return self.data.__contains__(name)

    def setdefault(self, name, default):
        """ set default of name """
        return self.data.setdefault(name, default)

    def has_key(self, name):
        """ has name key """
        return self.data.has_key(name)

    def has_key2(self, name1, najsb):
        """ has [name1][najsb] key """
        if self.data.has_key(name1): return self.data[name1].has_key(najsb)

    def get(self, name1, najsb):
        """ get data[name1][najsb] """
        try:
            result = self.data[name1][najsb]
            return result
        except KeyError: pass

    def set(self, name1, najsb, item):
        """ set name, najsb item """
        if not self.data.has_key(name1): self.data[name1] = {}
        self.data[name1][najsb] = item
