# jsb/lib/nextid.py
#
#

""" provide increasing counters """

## basic imports

import os

## Nextid class

class Nextid(object):

    """ counters by name """

    def __init__(self, fname):
        self.data = {}

    def get(self, item):
        """ get counter for item """
        item = item.lower()
        try:
            result = self.data[item]
        except KeyError:
            return None 
        return result

    def set(self, item, number):
        """ set counter of item to number """
        item = item.lower()
        try:
            self.data[item] = int(number)
        except ValueError:
            return 0
        self.save()
        return 1

    def next(self, item):
        """ get increment of item counter """
        item = item.lower()
        try:
            self.data[item] += 1
        except KeyError:
            self.data[item] = 1
        self.save()
        return self.data[item]

    def nextlist(self, item, nr):
        """ get increment of item counter """
        item = item.lower()
        try:
            start = self.data[item] + 1
        except KeyError:
            start = 1
        stop = start + nr
        l = range(start, stop)
        self.data[item] = stop - 1
        self.save()
        return l

    def save(self):
        pass

nextid = Nextid('notused')
