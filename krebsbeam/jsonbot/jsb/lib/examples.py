# jsb/examples.py
#
#

""" examples is a dict of example objects. """

## basic imports

import re

## Example class

class Example(object):

    """ an example. """

    def __init__(self, descr, ex, url=False):
        self.descr = descr
        self.example = ex
        self.url = url

## Collection of exanples

class Examples(dict):

    """ examples holds all the examples. """

    def add(self, name, descr, ex, url=False):
        """ add description and example. """
        self[name.lower()] = Example(descr, ex, url)

    def size(self):
        """ return size of examples dict. """
        return len(self.keys())

    def getexamples(self):
        """ get all examples in list. """
        result = []
        for i in self.values():
            ex = i.example.lower()
            exampleslist = re.split('\d\)', ex)
            for example in exampleslist:
                if example: result.append(example.strip())
        return result

## global examples object

examples = Examples()
