# jsb/utils/limlist.py
#
#

""" limited list """

class Limlist(list):

    """ list with limited number of items """

    def __init__(self, limit):
        self.limit = limit
        list.__init__(self)

    def insert(self, index, item):
        """ insert item at index .. pop oldest item if limit is reached """
        if index > len(self): return -1
        if len(self) >= self.limit: self.pop(len(self)-1)
        list.insert(self, index, item)

    def append(self, item):
        """ add item to list .. pop oldest item if limit is reached """
        if len(self) >= self.limit: self.pop(0)
        list.append(self, item)
