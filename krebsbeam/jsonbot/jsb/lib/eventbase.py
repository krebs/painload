# jsb/eventbase.py
#
#

""" base class of all events.  """

## jsb imports

from channelbase import ChannelBase
from jsb.utils.lazydict import LazyDict
from jsb.utils.generic import splittxt, stripped, waitforqueue
from errors import NoSuchUser
from jsb.utils.opts import makeeventopts
from jsb.utils.trace import whichmodule
from jsb.utils.exception import handle_exception
from jsb.utils.locking import lockdec
from jsb.lib.config import Config, getmainconfig

## basic imports

from xml.sax.saxutils import unescape
import copy
import logging
import Queue
import types
import socket
import threading
import time
import thread
import urllib

## defines

cpy = copy.deepcopy
lock = thread.allocate_lock()
locked = lockdec(lock)

## classes

class EventBase(LazyDict):

    """ basic event class. """

    def __init__(self, input={}, bot=None):
        LazyDict.__init__(self)
        if bot: self.bot = bot
        self.txt = ""
        self.usercmnd = ""
        self.bottype = "botbase"
        self.relayed = []
        self.path = []
        self.cbs = []
        self.result = []
        self.waiting = []
        self.threads = self.threads or []
        self.queues = self.queues or []
        self.finished = self.finished or threading.Event()
        self.resqueue = self.resqueue or Queue.Queue()
        self.inqueue = self.inqueue or Queue.Queue()
        self.outqueue = self.outqueue or Queue.Queue()
        self.stop = False
        self.bonded = False
        self.copyin(input)
        self.ctime = time.time()
        
    def __deepcopy__(self, a):
        """ deepcopy an event. """
        logging.debug("cpy - %s (%s) - %s" % (str(type(self)).split(".")[-1][:-2], len(self), whichmodule(2)))
        e = EventBase(self)
        return e

    def ready(self, finish=True):
        """ signal the event as ready - push None to all queues. """
        if self.finished.isSet(): logging.debug("event is already finished.") ; return
        if self.type != "TICK": logging.info("%s.%s - %s - from %s - %s" % (self.bottype, self.cbtype, str(self.ctime), whichmodule(), self.txt))
        for i in range(10):
             if not self.outqueue.empty(): break
             time.sleep(0.01)
        if self.closequeue and self.queues:
            for q in self.queues:
                q.put_nowait(None)
        if not self.dontclose:
            self.outqueue.put_nowait(None)
            self.resqueue.put_nowait(None)
            self.inqueue.put_nowait(None)
        for cb in self.cbs:
            try: cb(self.result)
            except Exception, ex: handle_exception()
        if finish: self.finished.set()
        for event in self.waiting:
            if event != self: event.ready()

    def prepare(self, bot=None):
        """ prepare the event for dispatch. """
        if bot: self.bot = bot
        assert(self.bot)
        self.origin = self.channel
        self.origtxt = self.txt
        self.makeargs()
        logging.debug("%s - prepared event - %s" % (self.auth, self.cbtype))

    def bind(self, bot=None, user=None, chan=None):
        """ bind event.bot event.user and event.chan to execute a command on it. """
        if self.bonded: logging.debug("already bonded") ; return
        target = self.auth
        bot = bot or self.bot
        if not self.chan:
            if chan: self.chan = chan
            elif self.channel: self.chan = ChannelBase(self.channel, bot.cfg.name)
            elif self.userhost: self.chan = ChannelBase(self.userhost, bot.cfg.name)
            if self.chan:
                self.debug = self.chan.data.debug or False
                logging.debug("channel bonded - %s" % self.chan.data.tojson())
        if not target: self.prepare(bot) ; self.bonded = True ; return
        if not self.user and target:
            cfg = getmainconfig()
            if cfg.auto_register: 
                bot.users.addguest(target)
            self.user = user or bot.users.getuser(target)
            if self.user: logging.debug("user bonded - %s - from %s" % (self.user.data.tojson(), whichmodule()))
        if not self.user and target: logging.debug("no %s user found .. setting nodispatch" % target) ; self.nodispatch = True
        self.prepare(bot)
        self.bonded = True
        return self

    def addwaiting(self, event):
        if not event in self.waiting: self.waiting.append(event)

    def parse(self, event, *args, **kwargs):
        """ overload this. """
        self.bot = event.bot
        self.origin = event.origin
        self.ruserhost = self.origin
        self.userhost = self.origin
        self.channel = event.channel
        self.auth = stripped(self.userhost)

    def waitfor(self, cb):
        """ wait for the event to finish. """
        logging.warn(" waiting for %s" % self.txt)
        #self.finished.wait(5)
        self.cbs.append(cb)
        return True

    def copyin(self, eventin):
        """ copy in an event. """
        self.update(eventin)
        try: self.path = eventin.path
        except: pass
        self.threads = self.threads or []
        self.queues = self.queues or []
        self.waiting = self.waiting or []
        self.finished = self.finished or threading.Event()
        self.resqueue = self.resqueue or Queue.Queue()
        self.inqueue = self.inqueue or Queue.Queue()
        self.outqueue = self.outqueue or Queue.Queue()
        return self

    #@locked
    def reply(self, txt, result=[], event=None, origin="", dot=u", ", nr=375, extend=0, showall=False, *args, **kwargs):
        """ reply to this event """
        try: target = self.channel or self.arguments[1]
        except IndexError: target = self.channel
        #if txt not in result: result.insert(0, txt)
        if self.checkqueues(result): return self
        if self.silent:
            self.msg = True
            self.bot.say(self.nick, txt, result, self.userhost, extend=extend, event=self, dot=dot, nr=nr, showall=showall, *args, **kwargs)
        elif self.isdcc: self.bot.say(self.sock, txt, result, self.userhost, extend=extend, event=self, dot=dot, nr=nr, showall=showall, *args, **kwargs)
        else: self.bot.say(target, txt, result, self.userhost, extend=extend, event=self, dot=dot, nr=nr, showall=showall, *args, **kwargs)
        return self

    def missing(self, txt):
        """ display missing arguments. """
        self.reply("%s %s" % (self.usercmnd, txt), event=self) 
        return self

    def done(self):
        """ tell the user we are done. """
        self.reply('<b>done</b> - %s' % self.txt, event=self)
        return self

    def leave(self):
        """ lower the time to leave. """
        self.ttl -= 1
        if self.ttl <= 0 : self.status = "done"
        logging.info("======== STOP handling event ========")

    def makeoptions(self):
        """ check the given txt for options. """
        try: self.options = makeeventopts(self.txt)
        except: return 
        if not self.options: return
        logging.debug("options - %s" % unicode(self.options))
        self.txt = ' '.join(self.options.args)
        self.makeargs()

    def makeargs(self):
        """ make arguments and rest attributes from self.txt. """
        if not self.txt:
            self.args = []
            self.rest = ""
        else:
            args = self.txt.split()
            self.chantag = args[0]
            if len(args) > 1:
                self.args = args[1:]
                self.rest = ' '.join(self.args)
            else:
                self.args = []
                self.rest = ""

    def checkqueues(self, resultlist):
        """ check if resultlist is to be sent to the queues. if so do it. """
        if self.queues:
            for queue in self.queues:   
                for item in resultlist:
                    if item: queue.put_nowait(item)
            for item in resultlist:
                if item: self.outqueue.put_nowait(item)      
            return True
        return False

    def makeresponse(self, txt, result, dot=u", ", *args, **kwargs):
        """ create a response from a string and result list. """
        return self.bot.makeresponse(txt, result, dot, *args, **kwargs)

    def less(self, what, nr=365):
        """ split up in parts of <nr> chars overflowing on word boundaries. """
        return self.bot.less(what, nr)

    def isremote(self):
        """ check whether the event is off remote origin. """
        if self.txt: return self.txt.startswith('{"') or self.txt.startswith("{&")

    def iscmnd(self):
        """ check if event is a command. """
        if not self.txt: logging.debug("no txt set.") ; return
        if self.iscommand: return self.txt
        if self.isremote(): logging.info("event is remote") ; return
        logging.debug("trying to match %s" % self.txt)
        cc = "!"
        if not self.chan: logging.warn("channel is not set.") ; return False
        cc = self.chan.data.cc
        if not cc: self.chan.data.cc = "!" ; self.chan.save()
        if not cc: cc = "!"
        if self.type == "DISPATCH": cc += "!"
        if not self.bot: logging.warn("bot is not bind into event.") ; return False
        logging.debug("cc for %s is %s (%s)" % (self.title or self.channel or self.userhost, cc, self.bot.cfg.nick))
        if self.txt[0] in cc: return self.txt[1:]
        matchnick = unicode(self.bot.cfg.nick + u":")
        if self.txt.startswith(matchnick): return self.txt[len(matchnick):]
        return False

    def stripcc(self):
        bla = self.iscmnd()
        if bla: return bla
        return self.txt
   