# jsb/compat/users.py
#
#

""" gozerbot compat users """

## jsb imports

from jsb.lib.datadir import datadir
from jsb.utils.generic import stripident, stripidents
from jsb.utils.exception import handle_exception
from jsb.utils.generic import die, stripped
from jsb.compat.persist import Persist
from jsb.lib.config import mainconfig as config

## basic imports

import re
import types
import os

## init

config.load()

## User class

class User(object):

    """ repesents a user """

    def __init__(self, name, userhosts, perms):
        self.name = str(name)
        self.userhosts = list(userhosts)
        self.perms = list(perms)
        self.email = ""
        self.permit = []
        self.status = []
        self.passwd = ""
        self.allowed = []
        self.notallowed = []
        self.tempuserhosts = []
        self.userdata = {}

    def __str__(self):
        return "name: %s userhosts: %s perms: %s email: %s status: %s \
allowed: %s notallowed: %s tempusershosts: %s permit: %s" % (self.name, \
self.userhosts, self.perms, self.email, self.status, self.allowed, \
self.notallowed, self.tempuserhosts, self.permit)

## Users class

class Users(Persist):

    """ holds multiple users """

    def __init__(self, filename):
        self.userhosts = {}
        self.masks = {}
        self.compiled = {}
        Persist.__init__(self, filename)
        if not self.data:
            self.data = []
        for i in self.data:
            for j in i.userhosts:
                self.adduserhost(j, i)

    def adduserhost(self, userhost, user):
        """ add userhost/mask """
        if '?' in userhost or '*' in userhost:
            tmp = re.escape(userhost)
            tmp = tmp.replace('\?','.')
            tmp = tmp.replace('\*','.*?')
            regex = re.compile(tmp)
            self.compiled[regex] = user
            self.masks[userhost] = regex
        else:
            self.userhosts[userhost] = user

    def deluserhost(self, userhost):
        """ del userhost/mask """
        try:
            if '?' in userhost or '*' in userhost:
                regex = self.masks[userhost]
                del self.compiled[regex]
                del self.masks[userhost]
            else:
                del self.userhosts[userhost]
            return 1
        except KeyError:
            return 0
            
    def exist(self, name):
        """ see if user with username exists """
        name = name.lower()
        for i in self.data:
            if i.name == name:
                return 1

    def getperms(self, userhost):
        """ get permissions """
        user = self.getuser(userhost)
        if user:
            return user.perms
        else:
            return ['ANON', ]

    def getuser(self, userhost):
        """ get user for which userhost matches """
        userhost = stripident(userhost)
        if userhost in self.userhosts:
            return self.userhosts[userhost]
        else:
            for i in self.compiled:
                if re.search(i, userhost):
                    return self.compiled[i]
        for user in self.data:
            for i in user.userhosts:
                if i == userhost or i == stripped(userhost):
                    return user
        return None

    def gotperm(self, name, perm):
        user = self.byname(name)
        if not user:
            return 0
        if perm in user.perms:
            return 1

    def size(self):
        """ return nr of users """
        return len(self.data)

    def add(self, name, userhosts, perms):
        """ add user """
        self.addnosave(name, userhosts, perms)
        self.save()
        return 1

    def addnosave(self, name, userhosts, perms):
        """ add user without saving """
        name = name.lower()
        for item in self.data:
            if item.name == name:
                return 0
        userhosts = stripidents(userhosts)
        # add user
        user = User(name, userhosts, perms)
        self.data.append(user)
        rlog(10, 'users', 'added user %s %s with perms %s' % (name, userhosts, perms))
        for i in userhosts:
            self.adduserhost(i, user)
        return 1

    def permitted(self, userhost, who, what):
        """ check if (who,what) is in users permit list """
        user = self.getuser(userhost)
        if not user:
            return 0
        if (who, what) in user.permit:
            return 1

    def names(self):
        """ get names of all users """
        result = []
        for item in self.data:
            result.append(item.name)
        return result

    def getname(self, userhost):
        """ get name of user with userhost """
        item = self.getuser(userhost)
        if item:
            return item.name
        else:
            return None

    def byname(self, name):
        """ return user with name """
        name = name.lower()
        for item in self.data:
            if item.name.lower() == name:
                return item
        return None

    def merge(self, name, userhost):
        """ add userhosts to user with name """
        name = name.lower()
        for item in self.data:
            if item.name == name:
                userhost = stripident(userhost)
                item.userhosts.append(userhost)
                self.adduserhost(userhost, item)
                self.save()
                rlog(10, 'users', 'merged %s (%s) with %s' % (name, userhost, item.name))
                return 1
        return None

    def delete(self, name):
        """ delete user with name """
        data = self.data
        name = name.lower()
        got = 0
        for itemnr in range(len(data)-1, -1, -1):
            if data[itemnr].name == name:
                for i in data[itemnr].userhosts:
                    self.deluserhost(i)
                del data[itemnr]
                got = 1
        if got:
            self.save()
            return 1
        return None

    def allowed(self, userhost, perms, log=True):
        """ check if user with userhosts is allowed to execute perm command """
        if type(perms) != types.ListType:
            perms = [perms, ]
        if 'ANY' in perms:
            return 1
        item = self.getuser(userhost)
        if not item:
            if log:
                rlog(10, 'users', '%s userhost denied' % userhost)
            return 0
        for i in perms:
            if i in item.perms:
                return 1
        if log:
            rlog(10, 'users', '%s perm %s denied' % (userhost, perms))
        return 0

    def status(self, userhost, status):
        """ check if user has status set """
        status = status.upper()
        item = self.getuser(userhost)
        if not item:
            return 0
        if status in item.status:
            return 1
        return 0

    def getemail(self, name):
        """ return email of user """
        user = self.byname(name)
        return user.email
        
    def setemail(self, name, email):
        """ set email of user """
        user = self.byname(name)
        user.email = email
        self.save()
        return 1
        
