# plugs/quote.py
#
#

## jsb imports

from jsb.compat.persist import Persist

## Quoteitem class

class Quoteitem(object):

    """ object representing a quote """

    def __init__(self, idnr, txt, nick=None, userhost=None, ttime=None):
        self.id = idnr
        self.txt = txt
        self.nick = nick
        self.userhost = userhost
        self.time = ttime

## Quotes class

class Quotes(Persist):

    """ list of quotes """

    def __init__(self, fname):
        Persist.__init__(self, fname)
        if not self.data:
            self.data = []

    def size(self):
        """ return nr of quotes """
        return len(self.data)

    def add(self, nick, userhost, quote):
        """ add a quote """
        id = nextid.next('quotes')
        item = Quoteitem(id, quote, nick, userhost, time.time())
        self.data.append(item)
        self.save()
        return id

    def addnosave(self, nick, userhost, quote, ttime):
        """ add quote but don't call save """
        id = nextid.next('quotes')
        item = Quoteitem(nextid.next('quotes'), quote, nick, userhost, ttime)
        self.data.append(item)
        return id

    def delete(self, quotenr):
        """ delete quote with id == nr """
        for i in range(len(self.data)):
            if self.data[i].id == quotenr:
                del self.data[i]
                self.save()
                return 1

    def random(self):
        """ get random quote """
        if not self.data:
            return None
        quotenr = random.randint(0, len(self.data)-1)
        return self.data[quotenr]

    def idquote(self, quotenr):
        """ get quote by id """
        for i in self.data:
            if i.id == quotenr:
                return i

    def whoquote(self, quotenr):
        """ get who quoted the quote """
        for i in self.data:
            if i.id == quotenr:
                return (i.nick, i.time)

    def last(self, nr=1):
        """ get last quote """
        return self.data[len(self.data)-nr:]

    def search(self, what):
        """ search quotes """
        if not self.data:
            return []
        result = []
        andre = re.compile('and', re.I)
        ands = re.split(andre, what)
        got = 0
        for i in self.data:
            for item in ands:
                if i.txt.find(item.strip()) == -1:
                    got = 0
                    break  
                got = 1
            if got:                  
                result.append(i)
        return result

    def searchlast(self, what, nr=1):
        """ search quotes backwards limit to 1"""
        if not self.data:
            return []
        result = []
        andre = re.compile('and', re.I)
        ands = re.split(andre, what)
        got = 0
        for i in self.data[::-1]:
            for item in ands:
                if i.txt.find(item.strip()) == -1:
                    got = 0
                    break  
                got = 1
            if got:                  
                result.append(i)
                got = 0
        return result

