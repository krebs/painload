# gozerbot/dol.py
#
#

""" dict of lists """

class Dol(dict):

    """ dol is dict of lists """

    def insert(self, nr, item, issue):
        """ add issue to item entry """
        if self.has_key(item): self[item].insert(nr, issue)
        else: self[item] = [issue]
        return True

    def add(self, item, issue):
        """ add issue to item entry """
        if self.has_key(item): self[item].append(issue)
        else: self[item] = [issue]
        return True

    def adduniq(self, item, issue):
        """ only add issue to item if it is not already there """
        if self.has_key(item):
            if issue in self[item]: return False
        self.add(item, issue)
        return True
            
    def delete(self, item, number):
        """ del self[item][number] """
        number = int(number)
        if self.has_key(item):
            try:
                del self[item][number]
                return True
            except IndexError: return False

    def remove(self, item, issue):
        """ remove issue from item """
        try:
            self[item].remove(issue)
            return True
        except ValueError: pass

    def has(self, item, issue):
        """ check if item has issue """
        try:
            if issue in self[item]: return True
            else: return False
        except KeyError: pass
