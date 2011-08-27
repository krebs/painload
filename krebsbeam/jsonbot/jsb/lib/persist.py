# jsb/persist.py
#
#

"""
    allow data to be written to disk or BigTable in JSON format. creating 
    the persisted object restores data. 

"""

## jsb imports

from jsb.utils.trace import whichmodule, calledfrom
from jsb.utils.lazydict import LazyDict
from jsb.utils.exception import handle_exception
from jsb.utils.name import stripname
from jsb.utils.locking import lockdec
from jsb.utils.timeutils import elapsedstring
from jsb.lib.callbacks import callbacks
from datadir import getdatadir

## simplejson imports

from jsb.imports import getjson
json = getjson()

## basic imports

import thread
import logging
import os
import os.path
import types
import copy
import sys
import time

## global list to keeptrack of what persist objects need to be saved

needsaving = []

def cleanup(bot=None, event=None):
    global needsaving
    r = []
    for p in needsaving:
        try: p.dosave() ; r.append(p) ; logging.warn("saved on retry - %s" % p.fn)
        except (OSError, IOError), ex: logging.error("failed to save %s - %s" % (p, str(ex)))
    for p in r:
        try: needsaving.remove(p)
        except ValueError: pass
    return needsaving

## try google first

try:
    import waveapi
    from google.appengine.ext import db
    import google.appengine.api.memcache as mc
    from google.appengine.api.datastore_errors import Timeout
    logging.debug("using BigTable based Persist")

    ## JSONindb class

    class JSONindb(db.Model):
        """ model to store json files in. """
        modtime = db.DateTimeProperty(auto_now=True, indexed=False)
        createtime = db.DateTimeProperty(auto_now_add=True, indexed=False)
        filename = db.StringProperty()
        content = db.TextProperty(indexed=False)

    ## Persist class

    class Persist(object):

        """ persist data attribute to database backed JSON file. """ 

        def __init__(self, filename, default={}, type="cache"):
            self.plugname = calledfrom(sys._getframe())
            if 'lib' in self.plugname: self.plugname = calledfrom(sys._getframe(1))
            try: del self.fn
            except: pass 
            self.fn = unicode(filename.strip()) # filename to save to
            self.logname = os.sep.join(self.fn.split(os.sep)[-1:])
            self.type = type
            self.counter = mcounter = mc.incr(self.fn, 1, "counters", 0)
            self.key = None
            self.obj = None
            self.size = 0
            self.init(default)

        def init(self, default={}, filename=None):
            cachetype = ""
            mcounter = mc.incr(self.fn, 1, "counters")
            logging.debug("%s - %s" % (self.counter, mcounter))
            #if self.type == "mem":
            #    tmp = get(self.fn) ; cachetype = "mem"
            #    if tmp: self.size = len(tmp)
            #    if tmp: self.data = tmp ; logging.debug("%s - loaded %s" % (cachetype, self.fn)) ; return
            jsontxt =  mc.get(self.fn) ; cachetype = "cache"
            #self.size = len(jsontxt)
            if type(default) == types.DictType:
                default2 = LazyDict()
                default2.update(default)
            else: default2 = copy.deepcopy(default)
            if jsontxt is None:
                logging.debug("%s - loading from db" % self.logname) 
                try:
                    try: self.obj = JSONindb.get_by_key_name(self.fn)
                    except Timeout: self.obj = JSONindb.get_by_key_name(self.fn)
                except Exception, ex:
                    # bw compat sucks
                    try: self.obj = JSONindb.get_by_key_name(self.fn)
                    except Exception, ex:
                        handle_exception()
                        self.data = default2
                        return
                if self.obj == None:
                    logging.debug("%s - no entry found" % self.logname)
                    self.obj = JSONindb(key_name=self.fn)
                    self.obj.content = unicode(default)
                    self.data = default2
                    return
                jsontxt = self.obj.content
                if jsontxt: mc.set(self.fn, jsontxt)
                logging.debug('jsontxt is %s' % jsontxt)
                cachetype = "file"
            else: cachetype = "cache"
            logging.debug("%s - loaded %s" % (cachetype, self.fn))
            self.data = json.loads(jsontxt)
            self.size = len(jsontxt)
            if type(self.data) == types.DictType:
                d = LazyDict()
                d.update(self.data)
                self.data = d
            cfrom = whichmodule()
            if 'jsb' in cfrom: 
                cfrom = whichmodule(2)
                if 'jsb' in cfrom: cfrom = whichmodule(3)
            cfrom = whichmodule(2)
            if 'jsb' in cfrom: 
                cfrom = whichmodule(3)
                if 'jsb' in cfrom: cfrom = whichmodule(4)
            if not 'run' in self.fn: 
                if cachetype: logging.debug("%s - loaded %s (%s) - %s - %s" % (cachetype, self.logname, len(jsontxt), self.data.tojson(), cfrom))
                else: logging.debug("loaded %s (%s) - %s - %s" % (self.logname, len(jsontxt), self.data.tojson(), cfrom))
            if self.data:
                set(self.fn, self.data)

        def sync(self):
            logging.info("syncing %s" % self.fn)
            data = json.dumps(self.data)
            mc.set(self.fn, data)
            delete(self.fn, self.data)
            return data
     
        def save(self, filename=None):
            """ save json data to database. """
            fn = filename or self.fn
            bla = json.dumps(self.data)
            if filename or self.obj == None:
                self.obj = JSONindb(key_name=fn)
                self.obj.content = bla
            else: self.obj.content = bla
            self.obj.filename = fn
            from google.appengine.ext import db
            key = db.run_in_transaction(self.obj.put)
            logging.debug("transaction returned %s" % key)
            mc.set(fn, bla)
            delete(fn, self.data)
            cfrom = whichmodule(0)
            if 'jsb' in cfrom: 
                cfrom = whichmodule(2)
                if 'jsb' in cfrom: cfrom = whichmodule(3)
            logging.warn('saved %s (%s) - %s' % (fn, len(bla), cfrom))

        def upgrade(self, filename):
            self.init(self.data, filename=filename)


except ImportError:

    ## file based persist

    logging.debug("using file based Persist")

    ## defines

    persistlock = thread.allocate_lock()
    persistlocked = lockdec(persistlock)

    ## imports for shell bots

    if True:
        got = False
        from jsb.memcached import getmc
        mc = getmc()
        if mc:
            status = mc.get_stats()
            if status:
                get = mc.get
                set = mc.set
                logging.warn("memcached uptime is %s" % elapsedstring(status[0][1]['uptime']))
                got = True
        if got == False:
            logging.warn("no memcached found - using own cache")
            from cache import get, set, delete

    import fcntl

    ## classes

    class Persist(object):

        """ persist data attribute to JSON file. """
        
        def __init__(self, filename, default=None, init=True, postfix=None):
            """ Persist constructor """
            if postfix: self.fn = str(filename.strip()) + str("-%s" % postfix)
            else: self.fn = str(filename.strip())
            self.logname = os.sep.join(self.fn.split(os.sep)[1:])
            self.lock = thread.allocate_lock() # lock used when saving)
            self.data = LazyDict() # attribute to hold the data
            self.count = 0
            self.ssize = 0
            self.jsontxt = ""
            self.dontsave = False
            if init:
                if default == None: default = LazyDict()
                self.init(default)

        def init(self, default={}, filename=None):
            """ initialize the data. """
            logging.debug('reading %s' % self.fn)
            cfrom = whichmodule(2)
            if 'lib' in cfrom: 
                cfrom = whichmodule(3)
                if 'lib' in cfrom: cfrom = whichmodule(4)
            gotcache = False
            cachetype = "cache"
            try:
                logging.debug("using name %s" % self.fn)
                self.jsontxt = get(self.fn) ; cachetype = "cache"
                if not self.jsontxt:
                   datafile = open(self.fn, 'r')
                   self.jsontxt = datafile.read()
                   datafile.close()
                   self.ssize = len(self.jsontxt)
                   cachetype = "file"
                   set(self.fn, self.jsontxt)
            except IOError, ex:
                if not 'No such file' in str(ex):
                    logging.error('failed to read %s: %s' % (self.logname, str(ex)))
                    raise
                else:
                    logging.debug("%s doesn't exist yet" % self.logname)
                    self.jsontxt = ""
            try:
                if self.jsontxt:
                    logging.debug(u"loading: %s" % type(self.jsontxt))
                    try: self.data = json.loads(str(self.jsontxt))
                    except Exception, ex: logging.error("couldn't parse %s" % self.jsontxt) ; self.data = None ; self.dontsave = True
                if not self.data: self.data = LazyDict()
                elif type(self.data) == types.DictType:
                    d = LazyDict()
                    d.update(self.data)
                    self.data = d
                logging.debug("%s - loaded %s (%s) - %s" % (cachetype, self.logname, len(self.jsontxt), cfrom))
            except Exception, ex:
                logging.error('ERROR: %s' % self.fn)
                raise

        def upgrade(self, filename):
            self.init(self.data, filename=filename)
            self.save(filename)

        def get(self):
            return json.loads(get(self.fn)) 

        def sync(self):
            logging.info("syncing %s" % self.fn)
            set(self.fn, json.dumps(self.data))
            return self.data

        @persistlocked
        def save(self):
            global needsaving
            try: self.dosave()
            except (IOError, OSError):
                self.sync()
                if self not in needsaving: needsaving.append(self)
        
        def dosave(self):
            """ persist data attribute. """
            try:
                if self.dontsave: logging.error("dontsave is set on  %s - not saving" % self.fn) ; return
                fn = self.fn
                d = []
                if fn.startswith(os.sep): d = [os.sep,]
                for p in fn.split(os.sep)[:-1]:
                    if not p: continue
                    d.append(p)
                    pp = os.sep.join(d)
                    if not os.path.isdir(pp):
                        logging.info("creating %s dir" % pp)
                        os.mkdir(pp)
                tmp = fn + '.tmp' # tmp file to save to
                datafile = open(tmp, 'w')
                fcntl.flock(datafile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                json.dump(self.data, datafile, indent=True)
                fcntl.flock(datafile, fcntl.LOCK_UN)
                datafile.close()
                try: os.rename(tmp, fn)
                except (IOError, OSError):
                    #handle_exception(txt="%s %s" % (tmp, fn))
                    os.remove(fn)
                    os.rename(tmp, fn)
                jsontxt = json.dumps(self.data)
                logging.debug("setting cache %s - %s" % (fn, jsontxt))
                set(fn, jsontxt)
                if 'lastpoll' in self.logname: logging.debug('%s saved (%s)' % (self.logname, (self.jsontxt)))
                else: logging.debug('%s saved (%s)' % (self.logname, len(self.jsontxt)))
            except IOError, ex: logging.error("not saving %s: %s" % (self.fn, str(ex))) ; raise
            except: raise
            finally: pass

class PlugPersist(Persist):

    """ persist plug related data. data is stored in jsondata/plugs/{plugname}/{filename}. """

    def __init__(self, filename, default=None, *args, **kwargs):
        plugname = calledfrom(sys._getframe())
        Persist.__init__(self, getdatadir() + os.sep + 'plugs' + os.sep + stripname(plugname) + os.sep + stripname(filename), *args, **kwargs)

callbacks.add("TICK60", cleanup)
