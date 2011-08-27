# jsb/compat/karma.py
#
#

""" gozerbot compat karma plugin. """

## jsb imports

from jsb.lib.datadir import datadir
from jsb.utils.exception import handle_exception
from jsb.utils.statdict import Statdict

## basic imports

import thread
import pickle
import time
import os
import logging

## defines

savelist = []

## karma class

class Karma:

    """ holds karma data """

    def __init__(self, ddir):
        rlog(0, 'karma', 'reading %s' % datadir + os.sep + 'karma')
        self.datadir = ddir
        self.lock = thread.allocate_lock()
        try:
            karmafile = open(ddir + os.sep + 'karma', 'r')
            self.karma = pickle.load(karmafile)
            karmafile.close()
        except:
            self.karma = {}
        try:
            reasonupfile = open(ddir + os.sep + 'reasonup', 'r')
            self.reasonup = pickle.load(reasonupfile)
            reasonupfile.close()
        except:
            self.reasonup = {}
        try:
            reasondownfile = open(ddir + os.sep + 'reasondown', 'r')
            self.reasondown = pickle.load(reasondownfile)
            reasondownfile.close()
        except:
            self.reasondown = {}
        try:
            whoupfile = open(ddir + os.sep + 'whoup', 'r')
            self.whoup = pickle.load(whoupfile)
            whoupfile.close()
        except:
            self.whoup = {}
        try:
            whodownfile = open(ddir + os.sep + 'whodown', 'r')
            self.whodown = pickle.load(whodownfile)
            whodownfile.close()
        except:
            self.whodown = {}

    def size(self):
        return len(self.karma)
        
    def save(self):
        """ save karma data """
        try:
            self.lock.acquire()
            karmafile = open(self.datadir + os.sep + 'karma', 'w')
            pickle.dump(self.karma, karmafile)
            karmafile.close()
            rlog(1, 'karma', '%s karma saved' % self.datadir)
            reasonupfile = open(self.datadir + os.sep + 'reasonup', 'w')
            pickle.dump(self.reasonup, reasonupfile)
            reasonupfile.close()
            rlog(1, 'karma', '%s reasonup saved' % self.datadir)
            reasondownfile = open(self.datadir + os.sep + 'reasondown', 'w')
            pickle.dump(self.reasondown, reasondownfile)
            reasondownfile.close()
            rlog(1, 'karma', '%s reasondown saved' % self.datadir)
            whoupfile = open(self.datadir + os.sep + 'whoup', 'w')
            pickle.dump(self.whoup, whoupfile)
            whoupfile.close()
            rlog(1, 'karma', '%s whoup saved' % self.datadir)
            whodownfile = open(self.datadir + os.sep + 'whodown', 'w')
            pickle.dump(self.whoup, whodownfile)
            whodownfile.close()
            rlog(1, 'karma', '%s whodown saved' % self.datadir)
        finally:
            self.lock.release()

    def add(self, item, value):
        """ set karma value of item """
        self.karma[item.lower()] = value

    def delete(self, item):
        """ delete karma item """
        item = item.lower()
        try:
            del self.karma[item]
            return 1
        except KeyError:
            return 0

    def get(self, item):
        """ get karma of item """
        item = item.lower()
        if self.karma.has_key(item):
            return self.karma[item]
        else:
            return None

    def addwhy(self, item, updown, reason):
        """ add why of karma up/down """
        item = item.lower()
        if not self.karma.has_key(item):
            return 0
        reason = reason.strip()
        if updown == 'up':
            if self.reasonup.has_key(item):
                self.reasonup[item].append(reason)
            else:
                self.reasonup[item] = [reason]
        elif updown == 'down':
            if self.reasondown.has_key(item):
                self.reasondown[item].append(reason)
            else:
                self.reasondown[item] = [reason]
            
    def upitem(self, item, reason=None):
        """ up a karma item with/without reason """
        item = item.lower()
        if self.karma.has_key(item):
            self.karma[item] += 1
        else:
            self.karma[item] = 1
        if reason:
            reason = reason.strip()
            if self.reasonup.has_key(item):
                self.reasonup[item].append(reason)
            else:
                self.reasonup[item] = [reason]

    def down(self, item, reason=None):
        """ lower a karma item with/without reason """
        item = item.lower()
        if self.karma.has_key(item):
            self.karma[item] -= 1
        else:
            self.karma[item] = -1
        if reason:
            reason = reason.strip()
            if self.reasondown.has_key(item):
                self.reasondown[item].append(reason)
            else:
                self.reasondown[item] = [reason]

    def whykarmaup(self, item):
        """ get why of karma ups """
        item = item.lower()
        if self.reasonup.has_key(item):
            return self.reasonup[item]

    def whykarmadown(self, item):
        """ get why of karma downs """
        item = item.lower()
        if self.reasondown.has_key(item):
            return self.reasondown[item]

    def setwhoup(self, item, nick):
        """ set who upped a karma item """
        item = item.lower()
        if self.whoup.has_key(item):
            self.whoup[item].append(nick)
        else:
            self.whoup[item] = [nick]

    def setwhodown(self, item, nick):
        """ set who lowered a karma item """
        item = item.lower()
        if self.whodown.has_key(item):
            self.whodown[item].append(nick)
        else:
            self.whodown[item] = [nick]

    def getwhoup(self, item):
        """ get list of who upped a karma item """
        item = item.lower()
        try:
            return self.whoup[item]
        except KeyError:
            return None

    def getwhodown(self, item):
        """ get list of who downed a karma item """
        item = item.lower()
        try:
            return self.whodown[item]
        except KeyError:
            return None

    def good(self, limit=10):
        """ show top 10 of karma items """
        statdict = Statdict()
        for i in self.karma.keys():
            if i.startswith('quote '):
                continue
            statdict.upitem(i, value=self.karma[i])
        return statdict.top(limit=limit)

    def bad(self, limit=10):
        """ show lowest 10 of negative karma items """
        statdict = Statdict()
        for i in self.karma.keys():
            if i.startswith('quote '):
                continue
            statdict.upitem(i, value=self.karma[i])
        return statdict.down(limit=limit)

    def quotegood(self, limit=10):
        """ show top 10 of karma items """
        statdict = Statdict()
        for i in self.karma.keys():
            if not i.startswith('quote '):
                continue
            statdict.upitem(i, value=self.karma[i])
        return statdict.top(limit=limit)

    def quotebad(self, limit=10):
        """ show lowest 10 of negative karma items """
        statdict = Statdict()
        for i in self.karma.keys():
            if not i.startswith('quote '):
                continue
            statdict.upitem(i, value=self.karma[i])
        return statdict.down(limit=limit)

    def search(self, item):
        """ search karma items """
        result = []
        item = item.lower()
        for i, j in self.karma.iteritems():
            if item in i:
                result.append((i, j))
        return result

    def whatup(self, nick):
        """ show what items where upped by nick """
        nick = nick.lower()
        statdict = Statdict()
        for i, j in self.whoup.iteritems():
            for z in j:
                if nick == z:
                    statdict.upitem(i)
        return statdict.top()

    def whatdown(self, nick):
        """ show what items where lowered by nick """
        nick = nick.lower()
        statdict = Statdict()
        for i, j in self.whodown.iteritems():
            for z in j:
                if nick == z:
                    statdict.upitem(i)
        return statdict.top()

