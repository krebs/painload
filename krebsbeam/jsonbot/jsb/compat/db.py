# jsb/compat/db.py
#
#

""" gozerbot compat database interface """

## jsb imports

from jsb.compat.config import config
from jsb.utils.locking import lockdec
from jsb.utils.generic import tolatin1
from jsb.utils.exception import handle_exception
from jsb.lib..datadir import datadir

## basic imports

import thread
import os
import time
import types

## locks

dblock = thread.allocate_lock()
dblocked = lockdec(dblock)

## Db class

class Db(object):

    """ this class implements a database connection. it connects to the 
        database on initialisation.
    """

    def __init__(self, doconnect=True, dbtype=None, ddir=None,config=config):
        self.datadir = ddir or datadir
        if hasattr(os, 'mkdir'):
            if not os.path.isdir(self.datadir + os.sep + 'db/'):
                os.mkdir(self.datadir + os.sep + 'db/')
        self.config = config
        self.dbname = self.config['dbname'] or ""
        self.dbhost = self.config['dbhost'] or ""
        self.dbuser = self.config['dbuser'] or ""
        self.dbpasswd = self.config['dbpasswd'] or ""
        self.connection = None
        self.timeout = 15
        self.oldstyle = ""
        self.dbtype = dbtype or self.config['dbtype'] or 'sqlite'
        if doconnect:
            self.connect()

    def connect(self, dbname=None, dbhost=None, dbuser=None, dbpasswd=None, timeout=15, oldstyle=False):
        """ connect to the database. """
        self.dbname = dbname or self.config['dbname']
        self.dbhost = dbhost or self.config['dbhost']
        self.dbuser = dbuser or self.config['dbuser']
        self.dbpasswd = dbpasswd or self.config['dbpasswd']
        self.timeout = timeout
        self.oldstyle = oldstyle or self.config['dboldstyle']
        if self.dbtype == 'mysql':
            import MySQLdb
            self.connection = MySQLdb.connect(db=self.dbname, host=self.dbhost, user=self.dbuser, passwd=self.dbpasswd, connect_timeout=self.timeout, charset='utf8')
        elif 'sqlite' in self.dbtype:
            try:
                import sqlite
                self.connection = sqlite.connect(self.datadir + os.sep + self.dbname)
            except ImportError:
                import sqlite3
                self.connection = sqlite3.connect(self.datadir + os.sep + self.dbname, check_same_thread=False)
        elif self.dbtype == 'postgres':
            import psycopg2
            rlog(1000, 'db', 'NOTE THAT POSTGRES IS NOT FULLY SUPPORTED')
            self.connection = psycopg2.connect(database=self.dbname, host=self.dbhost, user=self.dbuser, password=self.dbpasswd)
        else:
            rlog(100, 'db', 'unknown database type %s' % self.dbtype)
            return 0
        rlog(10, 'db', "%s database ok" % self.dbname)
        return 1

    def reconnect(self):
        """ reconnect to the database server. """
        return self.connect()

    @dblocked
    def execute(self, execstr, args=None):
        """ execute string on database. """
        time.sleep(0.001)
        result = None
        execstr = execstr.strip()
        if self.dbtype == 'sqlite':
            execstr = execstr.replace('%s', '?')
        # first to ping to see if connection is alive .. if not reconnect
        if self.dbtype == 'mysql':
            try:
                self.ping()
            except AttributeError:
                self.reconnect()                
            except Exception, ex:
                rlog(10, 'db', "can't ping database: %s" % str(ex))
                rlog(10, 'db', 'reconnecting')
                try:
                    self.reconnect()
                except Exception, ex:
                    rlog(10, 'db', 'failed reconnect: %s' % str(ex))
                    return
        # convert to latin1 if oldstyle is set
        if args and self.oldstyle:
            nargs = []
            for i in args:
                nargs.append(tolatin1(i))
            args = nargs
        rlog(-2, 'db', 'exec %s %s' % (execstr, args))

        # get cursor
        cursor = self.cursor()
        nr = 0

        # excecute string on cursor
        try:
            if args:
                if type(args) == tuple or type(args) == list:
                    nr = cursor.execute(execstr, args)
                else:
                    nr = cursor.execute(execstr, (args, ))
            else:
                nr = cursor.execute(execstr)
        except:
            if self.dbtype == 'postgres':
                cursor.execute(""" ROLLBACK """)
            if self.dbtype == 'sqlite':
                cursor.close()
            raise

        # see if we need to commit the query
        got = False
        if execstr.startswith('INSERT'):
            nr = cursor.lastrowid or nr
            got = True
        elif execstr.startswith('UPDATE'):
            nr = cursor.rowcount
            got = True
        elif execstr.startswith('DELETE'):
            nr = cursor.rowcount
            got = True
        if got:
            self.commit()

        # determine rownr
        if self.dbtype == 'sqlite' and not got and type(nr) != types.IntType:
            nr = cursor.rowcount or cursor.lastrowid
            if nr == -1:
                nr = 0

        # fetch results
        result = None
        try:
            result = cursor.fetchall()
            if not result:
                result = nr
        except Exception, ex:
            if 'no results to fetch' in str(ex):
                pass
            else:
                handle_exception()
            result = nr

        cursor.close()
        return result

    def cursor(self):

        """ return cursor to the database. """

        return self.connection.cursor()

    def commit(self):

        """ do a commit on the datase. """

        self.connection.commit()

    def ping(self):

        """ do a ping. """

        return self.connection.ping()

    def close(self):

        """ close database. """

        if 'sqlite' in self.dbtype:
            self.commit()
        self.connection.close()

