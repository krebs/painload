# jsb/users.py
#
#

""" bot's users in JSON file.  NOT USED AT THE MOMENT. """

## lib imports

from jsb.utils.exception import handle_exception, exceptionmsg
from jsb.utils.generic import stripped
from jsb.utils.name import stripname
from persiststate import UserState
from persist import Persist
from jsb.utils.lazydict import LazyDict
from datadir import getdatadir
from errors import NoSuchUser
from config import Config, getmainconfig

## basic imports

import re
import types
import os
import time
import logging
import copy

## defines

cpy = copy.deepcopy

## JsonUser class

class JsonUser(Persist):

    """ LazyDict representing a user. """

    def __init__(self, name, userhosts=[], perms=[], permits=[], status=[], email=[]):
        assert name
        name = stripname(name.lower())
        Persist.__init__(self, getdatadir() + os.sep + 'users' + os.sep + name)
        self.data.datadir = self.data.datadir or getdatadir()
        self.data.name = self.data.name or name
        self.data.userhosts = self.data.userhosts or userhosts
        self.data.perms = self.data.perms or perms
        self.data.permits = self.data.permits or permits
        self.data.status = self.data.status or status
        self.data.email = self.data.email or email
        self.state = UserState(name)

## Users class

class Users(Persist):

    """ class representing all users. """

    def __init__(self, ddir=None, filename=None):
        self.datadir = ddir or getdatadir()
        self.filename = filename or 'mainusers'
        Persist.__init__(self, self.datadir + os.sep + self.filename)
        if not self.data: self.data = LazyDict()
        self.data.names = self.data.names or {}

    def all(self):
        """ get all users. """
        result = []
        for name in self.data['names'].values(): result.append(JsonUser(name).lower())
        return result

    ## Misc. Functions

    def size(self):
        """ return nr of users. """
        return len(self.data['names'])

    def names(self):
        """ get names of all users. """
        return self.data.names

    def byname(self, name):
        """ return user by name. """ 
        try:
            name = name.lower()
            name = stripname(name)
            user = JsonUser(name)
            if user.data.userhosts: return user
        except KeyError: raise NoSuchUser(name)

    def merge(self, name, userhost):
        """ add userhosts to user with name """
        name = name.lower()
        user = self.byname(name)
        if user:
            if not userhost in user.data.userhosts:
                user.data.userhosts.append(userhost)
                user.save()
            self.data.names[userhost] = name
            self.save()
            logging.warn("%s merged with %s" % (userhost, name))
            return 1

    def usersearch(self, userhost):
        """ search for users with a userhost like the one specified """
        result = []
        for u, name in self.data.names.iteritems():
            if userhost in u: result.append((name.lower(), u))
        return result

    def getuser(self, userhost):
        """ get user based on userhost. """
        try:
            user = self.byname(self.data.names[userhost])
            if user: return user
        except KeyError:
            logging.debug("can't find %s in names cache" % userhost) 

    ## Check functions

    def exist(self, name):
        """ see if user with <name> exists """
        return self.byname(name)

    def allowed(self, userhost, perms, log=True, bot=None):
        """ check if user with userhosts is allowed to execute perm command """
        if not type(perms) == types.ListType: perms = [perms, ]
        if 'ANY' in perms: return 1
        if bot and bot.allowall: return 1
        res = None
        user = self.getuser(userhost)
        if not user:
            logging.warn('%s userhost denied' % userhost)
            return res
        else:
            uperms = set(user.data.perms)
            sperms = set(perms)
            intersection = sperms.intersection(uperms)
            res = list(intersection) or None
        if not res and log: logging.warn("%s perm %s denied (%s)" % (userhost, str(perms), str(uperms)))
        return res

    def permitted(self, userhost, who, what):
        """ check if (who,what) is in users permit list """
        user = self.getuser(userhost)
        res = None
        if user: 
            if '%s %s' % (who, what) in user.data.permits: res = 1
        return res

    def status(self, userhost, status):
        """ check if user with <userhost> has <status> set """
        user = self.getuser(userhost)
        res = None
        if user:
            if status.upper() in user.data.status: res = 1
        return res

    def gotuserhost(self, name, userhost):
        """ check if user has userhost """
        user = self.byname(name)
        return userhost in user.data.userhosts

    def gotperm(self, name, perm):
        """ check if user had permission """
        user = self.byname(name)
        if user: return perm.upper() in user.data.perms

    def gotpermit(self, name, permit):
        """ check if user permits something.  permit is a (who, what) tuple """
        user = self.byname(name)
        if user: return '%s %s' % permit in user.data.permits
        
    def gotstatus(self, name, status):
        """ check if user has status """
        user = self.byname(name)
        return status.upper() in user.data.status

    ## Get Functions

    def getname(self, userhost):
        """ get name of user belonging to <userhost> """
        try: return self.data.names[userhost]
        except KeyError:
            try: return self.data.names[userhost]
            except KeyError:
                user = self.getuser(userhost)
                if user: return user.data.name.lower()

    def gethosts(self, userhost):
        """ return the userhosts of the user associated with the specified userhost """
        user = self.getuser(userhost)
        if user: return user.data.userhosts
    
    def getemail(self, userhost):
        """ return the email of the specified userhost """
        user = self.getuser(userhost)
        if user:
            if user.data.email: return user.data.email[0]

    def getperms(self, userhost):
        """ return permission of user"""
        user = self.getuser(userhost)
        if user: return user.data.perms

    def getpermits(self, userhost):
        """ return permits of the specified userhost"""
        user = self.getuser(userhost)
        if user: return user.data.permits

    def getstatuses(self, userhost):
        """ return the list of statuses for the specified userhost. """
        user = self.getuser(userhost)
        if user: return user.data.status

    def getuserhosts(self, name):
        """ return the userhosts associated with the specified user. """
        user = self.byname(name)
        if user: return user.data.userhosts

    def getuseremail(self, name):
        """ get email of user. """
        user = self.byname(name)
        if user:
            if user.data.email: return user.data.email[0]

    def getuserperms(self, name):
        """ return permission of user. """
        user = self.byname(name)
        if user: return user.data.perms

    def getuserpermits(self, name):
        """ return permits of user. """
        user = self.byname(name)
        if user: return user.data.permits

    def getuserstatuses(self, name):
        """ return the list of statuses for the specified user. """
        user = self.byname(name)
        if user: return user.data.status

    def getpermusers(self, perm):
        """ return all users that have the specified perm. """
        result = []
        names = cpy(self.data.names)
        for name in names:
            user = JsonUser(name)
            if perm.upper() in user.data.perms: result.append(user.data.name)
        return result

    def getstatususers(self, status):
        """ return all users that have the specified status. """
        result = []
        for name in self.data.names:
            user = JsonUser(name.lower())
            if status in user.data.status: result.append(user.data.name.lower())
        return result

    ## Set Functions

    def setemail(self, name, email):
        """ set email of user. """
        user = self.byname(name)
        if user:
            try: user.data.email.remove(email)
            except: pass
            user.data.email.insert(0, email)
            user.save()
            return True
        return False

    ## Add functions

    def add(self, name, userhosts, perms):
        """ add an user. """
        name = name.lower()
        newuser = JsonUser(name, userhosts, perms)
        for userhost in userhosts: self.data.names[userhost] = name
        newuser.save()
        self.save()
        logging.warn('%s - %s - %s - added to user database' % (name, userhosts, perms))
        return True

    def addguest(self, userhost):
        if not self.getname(userhost):
            if getmainconfig().guestasuser: self.add(userhost, [userhost, ], ["USER",])
            else: self.add(userhost, [userhost, ], ["GUEST",])

    def addemail(self, userhost, email):
        """ add an email address to the userhost. """
        user = self.getuser(userhost)
        if user:
            user.data.email.append(email)
            user.save()
            return 1

    def addperm(self, userhost, perm):
        """ add the specified perm to the userhost. """
        user = self.getuser(userhost)
        if user:
            user.data.perms.append(perm.upper())
            user.save()
            return 1

    def addpermit(self, userhost, permit):
        """ add the given (who, what) permit to the given userhost. """
        user = self.getuser(userhost)
        if user:
            user.data.permits.append(permit)
            user.save()
            return 1

    def addstatus(self, userhost, status):
        """ add status to given userhost. """
        user = self.getuser(userhost)
        if user:
            user.data.status.append(status.upper())
            user.save()
            return 1

    def adduserhost(self, name, userhost):
        """ add userhost. """
        name = name.lower()
        user = self.byname(name)
        if not user: user = self.users[name] = JsonUser(name=name)
        user.data.userhosts.append(userhost)
        user.save()
        self.data.names[userhost] = name
        self.save()
        return 1

    def adduseremail(self, name, email):
        """ add email to specified user. """
        user = self.byname(name)
        if user:
            user.data.email.append(email)
            user.save()
            return 1

    def adduserperm(self, name, perm):
        """ add permission. """
        user = self.byname(name)
        if user:
            perm = perm.upper()
            user.data.perms.append(perm)
            user.save()
            return 1

    def adduserpermit(self, name, who, permit):
        """ add (who, what) permit tuple to sepcified user. """
        user = self.byname(name)
        if user:
            p = '%s %s' % (who, permit)
            user.data.permits.append(p)
            user.save()
            return 1

    def adduserstatus(self, name, status):
        """ add status to given user. """
        user = self.byname(name)
        if user:
            user.data.status.append(status.upper())
            user.save()
            return 1

    def addpermall(self, perm): 
        """ add permission to all users. """
        for name in self.data.names:
            user = JsonUser(name.lower())
            user.data.perms.append(perm.upper())
            user.save()

    ## Delete functions

    def delemail(self, userhost, email):
        """ delete email from userhost. """
        user = self.getuser(userhost)
        if user:
            if email in user.emails:
                user.data.emails.remove(email)
                user.save()
                return 1

    def delperm(self, userhost, perm):
        """ delete perm from userhost. """
        user = self.getuser(userhost)
        if user:
            p = perm.upper()
            if p in user.perms:
                user.data.perms.remove(p)
                user.save()
                return 1

    def delpermit(self, userhost, permit):
        """ delete permit from userhost. """
        user = self.getuser(userhost)
        if user:
            p = '%s %s' % permit
            if p in user.permits:
                user.data.permits.remove(p)
                user.save()
                return 1

    def delstatus(self, userhost, status):
        """ delete status from userhost. """
        user = self.getuser(userhost)
        if user:
            st = status.upper()
            if st in user.data.status:
                user.data.status.remove(st)
                user.save()
                return 1

    def delete(self, name):
        """ delete user with name. """
        try:
            name = name.lower()
            user = JsonUser(name)
            user.data.deleted = True
            user.save()
            if user:
                 for userhost in user.data.userhosts:
                     try: del self.data.names[userhost]
                     except KeyError: pass
            self.save()
            return True
        except NoSuchUser:
            pass
        
    def deluserhost(self, name, userhost):
        """ delete the userhost entry. """
        user = self.byname(name)
        if user:
            if userhost in user.data.userhosts:
                user.data.userhosts.remove(userhost)
                user.save()
            try: del self.data.names[userhost] ; self.save()
            except KeyError: pass
            return 1

    def deluseremail(self, name, email):
        """ delete email. """
        user = self.byname(name)
        if user:
            if email in user.data.email:
                user.data.email.remove(email)
                user.save()
                return 1

    def deluserperm(self, name, perm):
        """ delete permission. """
        user = self.byname(name)
        if user:
            p = perm.upper()
            if p in user.data.perms:
                user.data.perms.remove(p)
                user.save()
                return 1

    def deluserpermit(self, name, permit):
        """ delete permit. """
        user = self.byname(name)
        if user:
            p = '%s %s' % permit
            if p in user.data.permits:
                user.data.permits.remove(p)
                user.save()
                return 1

    def deluserstatus(self, name, status):
        """ delete the status from the given user. """
        user = self.byname(name)
        if user:
            st = status.upper()
            if st in user.data.status:
                user.data.status.remove(status)
                user.save()
                return 1

    def delallemail(self, name):
        """ delete all emails for the specified user. """
        user = self.byname(name)
        if user:
            user.data.email = []
            user.save()
            return 1

    def make_owner(self, userhosts):
        """ see if owner already has a user account if not add it. """ 
        if not userhosts:
            logging.info("no usershosts provided in make_owner")
            return
        owner = []
        if type(userhosts) != types.ListType: owner.append(userhosts)
        else: owner = userhosts
        for userhost in owner:
            username = self.getname(unicode(userhost))
            if not username or username != 'owner':
                if not self.merge('owner', unicode(userhost)): self.add('owner', [unicode(userhost), ], ['USER', 'OPER', 'GUEST'])

## global users object

users = None

## users_boot function

def users_boot():
    """ initialize global users object. """
    global users
    users = Users()
    return users

def getusers():
    global users
    if not users: users_boot()
    return users