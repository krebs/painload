# jsb/compat/dbusers.py
#
#

""" gozerbot users for mysql interface"""

## jsb imports

from jsb.compat.db import Db

## basic imports

import types
import logging

## Dbusers class

class Dbusers(object):

    """ users class """

    def __init__(self):
        self.db = Db()

    def size(self):
        """ return nr of users """
        result = self.db.execute(""" SELECT DISTINCT COUNT(*) FROM userhosts \
""")
        if result:
            return result[0][0]

    def getperms(self, userhost):
        """ return permission of user"""
        name = self.getname(userhost)
        if not name:
            return ['ANON', ]
        result = self.db.execute(""" SELECT perm FROM perms WHERE name = %s \
""", name)
        res = []
        for i in result:
            res.append(i[0])
        return res

    def exist(self, name):
        """ see if user with <name> exists """
        name = name.lower()
        result = self.db.execute(""" SELECT name,userhost FROM userhosts WHERE \
name = %s """, name)
        return result

    def getname(self, userhost):
        """ get name of user belonging to <userhost> """
        result = self.db.execute(""" SELECT name FROM userhosts WHERE \
%s LIKE userhost """, userhost)
        if result:
            return result[0][0]

    def add(self, name, userhosts, perms):
        """ add an user """
        if type(userhosts) != types.ListType:
            logging.warn('i need a list of userhosts')
            return 0
        for i in userhosts:
            self.adduserhost(name, i)
        for i in perms:
            self.addperm(name, i)
            logging.warn('%s added to user database' % name)
        return 1

    def adduserhost(self, name, userhost):
        """ add userhost """
        name = name.lower()
        res = None
        result = self.db.execute(""" INSERT INTO userhosts(name, userhost) \
values(%s, %s) """, (name, userhost))
        if result:
            res = 1
            logging.warn('%s (%s) added to userhosts' % (name, userhost))
        return res

    def addperm(self, name, perm):
        """ add permission """
        name = name.lower()
        perm = perm.upper()
        res = None
        result = self.db.execute(""" INSERT INTO perms(name, perm) \
values(%s, %s) """, (name, perm))
        if result:
            res = 1
            logging.warn('%s perm %s added' % (name, perm))
        return res

    def delperm(self, name, perm):
        """ add permission """
        name = name.lower()
        perm = perm.upper()
        result = self.db.execute(""" DELETE FROM perms WHERE name = %s AND \
perm = %s """, (name, perm))
        if result:
            logging.warn('%s perm %s deleted' % (name, perm))
            return result

    def permitted(self, userhost, who, what):
        """ check if (who,what) is in users permit list """
        name = self.getname(userhost)
        res = None
        if name:
            result = self.db.execute(""" SELECT permit FROM permits WHERE \
name = %s """, name)
            if result:
                for i in result:
                    if "%s %s" % (who, what) == i[0]:
                        res = 1
        return res

    def names(self):
        """ get names of all users """
        res = []
        result = self.db.execute(""" SELECT DISTINCT name FROM userhosts """)
        if result:
            for i in result:
                res.append(i[0])
        return res

    def merge(self, name, userhost):
        """ add userhosts to user with name """
        name = name.lower()
        if not self.exist(name):
            return 0
        res = None
        result = self.db.execute(""" INSERT INTO userhosts(userhost, name) \
VALUES (%s, %s) """, (userhost, name))
        if result:
            res = 1
        return res

    def delete(self, name):
        """ delete user with name """
        name = name.lower()
        res = None
        nr1 = self.db.execute(""" DELETE FROM userhosts WHERE name = %s \
""", name)
        nr2 = self.db.execute(""" DELETE FROM perms WHERE name = %s \
""", name)
        if nr1 and nr2:
            res = 1
        return res

    def status(self, userhost, status):
        """ check if user with <userhost> has <status> set """
        name = self.getname(userhost)
        res = None
        if name:
            status = status.upper()
            result = self.db.execute(""" SELECT status FROM statuses WHERE \
name = %s """, name)
            if result:
                for i in result:
                    if status == i[0]:
                        res = 1
        return res

    def gotperm(self, name, perm):
        """ check if user had permission """
        name = name.lower()
        perm = perm.upper()
        result = self.db.execute(""" SELECT perm FROM perms WHERE \
name = %s """, name)
        if result:
            for i in result:
                if i[0] == perm:
                    return True

    def gotstatus(self, name, status):
        """ check if user has status """
        name = name.lower()
        status = status.upper()
        result = self.db.execute(""" SELECT status FROM statuses WHERE \
name = %s """, name)
        if result:
            for i in result:
                if status == i[0]:
                    return True

    def gotuserhost(self, name, userhost):
        """ check if user has userhost """
        name = name.lower()
        result = self.db.execute(""" SELECT userhost FROM userhosts WHERE \
name = %s """, name)
        if result:
            for i in result:
                if i[0] == userhost:
                    return True

    def gotpermit(self, name, permit):
        """ check if user permits something """
        name = name.lower()
        result = self.db.execute(""" SELECT permit FROM permits WHERE \
name = %s """, name)
        if result:
            for i in result:
                if "%s %s" % permit == i[0]:
                    return True

    def allowed(self, userhost, perms, log=True):
        """ check if user with userhosts is allowed to execute perm command """
        if not type(perms) == types.ListType:
            perms = [perms, ]
        if 'ANY' in perms:
            return 1
        res = None
        name = self.getname(userhost)
        if not name:
            if log:
                logging.warn('%s userhost denied' % userhost)
            return res
        result = self.db.execute(""" SELECT perm FROM perms WHERE \
name = %s """, name)
        if result:
            for i in result:
                if i[0] in perms:
                    res = 1
        if not res:
            if log:
                logging.warn("%s perm %s denied" % (userhost, perms))
        return res

    def getemail(self, name):
        """ get email of user """
        name = name.lower()
        email = None
        email = self.db.execute(""" SELECT email FROM email WHERE name = %s \
""", name)
        if email:
            return email[0][0]

    def setemail(self, name, email):
        """ set email of user """
        res = 0
        try:
            result = self.db.execute(""" INSERT INTO email(name, email) \
VALUES (%s, %s) """, (name, email))
        except:
            try:
                result = self.db.execute(""" UPDATE email SET email = %s \
WHERE name = %s """, (email, name))
            except:
                pass
        if result:
            res = 1
        return res

    def addpermall(self, perm): 
        """ add permission to all users """
        perm = perm.upper()
        for i in self.names():
            try:
                self.addperm(i, perm)
            except:
                pass

    def delpermall(self, perm):
        """ delete permission from all users """
        perm = perm.upper()
        for i in self.names():
            try:
                self.delperm(i, perm)
            except:
                pass
