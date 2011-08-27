# gozerbot/periodical.py
#
#

""" provide a periodic structure. """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = "BSD License"

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.utils.trace import calledfrom, whichmodule
from jsb.utils.locking import lockdec
from jsb.utils.timeutils import strtotime
from jsb.lib.callbacks import callbacks
import jsb.lib.threads as thr

## basic imorts

import datetime
import sys
import time
import thread
import types
import logging

## locks

plock    = thread.allocate_lock()
locked   = lockdec(plock)

## defines

pidcount = 0

## JobError class

class JobError(Exception):

    """ job error exception. """
    pass

## Job class

class Job(object):

    """ job to be scheduled. """

    group = ''
    pid   = -1

    def __init__(self):
        global pidcount
        pidcount += 1
        self.pid = pidcount

    def id(self):
        """ return job id. """
        return self.pid

    def member(self, group):
        """ check for group membership. """
        return self.group == group

    def do(self):
        """ try the callback. """
        try: self.func(*self.args, **self.kw)
        except Exception, ex: handle_exception()

class JobAt(Job):

    """ job to run at a specific time/interval/repeat. """

    def __init__(self, start, interval, repeat, func, *args, **kw):
        Job.__init__(self)
        self.func = func
        self.args = args
        self.kw = kw
        self.repeat = repeat
        self.description = ""
        self.counts = 0
        if type(start) in [types.IntType, types.FloatType]: self.next = float(start)
        elif type(start) in [types.StringType, types.UnicodeType]:
            d = strtotime(start)
            if d and d > time.time(): self.next = d
            else: raise JobError("invalid date/time")
        if type(interval) in [types.IntType]:
            d = datetime.timedelta(days=interval)
            self.delta = d.seconds
        else: self.delta = interval

    def __repr__(self):
        """ return a string representation of the JobAt object. """
        return '<JobAt instance next=%s, interval=%s, repeat=%d, function=%s>' % (str(self.next), str(self.delta), self.repeat, str(self.func))

    def check(self):
        """ run check to see if job needs to be scheduled. """
        if self.next <= time.time():
            logging.warn('running %s - %s' % (str(self.func), self.description))
            self.func(*self.args, **self.kw)
            self.next += self.delta
            self.counts += 1
            if self.repeat > 0 and self.counts >= self.repeat: return False
        return True

class JobInterval(Job):

    """ job to be scheduled at certain interval. """

    def __init__(self, interval, repeat, func, *args, **kw):
        Job.__init__(self)
        self.func = func
        self.args = args
        self.kw = kw
        self.repeat = int(repeat)
        self.counts = 0
        self.interval = float(interval)
        self.description = ""
        self.next = time.time() + self.interval
        self.group = None
        logging.warn('scheduled next run of %s in %d seconds' % (str(self.func), self.interval))

    def __repr__(self):
        return '<JobInterval instance next=%s, interval=%s, repeat=%d, group=%s, function=%s>' % (str(self.next), str(self.interval), self.repeat, self.group, str(self.func))

    def check(self):
        """ run check to see if job needs to be scheduled. """
        if self.next <= time.time():
            logging.warn('running %s - %s' % (str(self.func), self.description))
            self.next = time.time() + self.interval
            thr.start_new_thread(self.do, ())
            self.counts += 1
            if self.repeat > 0 and self.counts >= self.repeat: return False
        return True


class Periodical(object):

    """ periodical scheduler. """

    def __init__(self):
        self.jobs = []
        self.running = []
        self.run = True

    def addjob(self, sleeptime, repeat, function, description="" , *args, **kw): 
        """ add a periodical job. """
        job = JobInterval(sleeptime, repeat, function, *args, **kw)
        job.group = calledfrom(sys._getframe())
        job.description = str(description) or whichmodule()
        self.jobs.append(job)
        return job.pid

    def changeinterval(self, pid, interval):
        """ change interval of of peridical job. """
        for i in periodical.jobs:
            if i.pid == pid:
                i.interval = interval
                i.next = time.time() + interval

    def looponce(self, bot, event):
        """ loop over the jobs. """
        for job in self.jobs:
            if job.next <= time.time():
                self.runjob(job)

    def runjob(self, job):
        """ run a periodical job. """
        if not job.check(): self.killjob(job.id())
        else: self.running.append(job)

    def kill(self):
        """ kill all jobs invoked by another module. """
        group = calledfrom(sys._getframe())
        self.killgroup(group)

    def killgroup(self, group):
        """ kill all jobs with the same group. """

        def shoot():
            """ knock down all jobs belonging to group. """
            deljobs = [job for job in self.jobs if job.member(group)]
            for job in deljobs:
                self.jobs.remove(job)
                try: self.running.remove(job)
                except ValueError: pass
            logging.warn('killed %d jobs for %s' % (len(deljobs), group))
            del deljobs

        return shoot()

    def killjob(self, jobId):
        """ kill one job by its id. """
        def shoot():
            deljobs = [x for x in self.jobs if x.id() == jobId]
            numjobs = len(deljobs)
            for job in deljobs:
                self.jobs.remove(job)
                try: self.running.remove(job)
                except ValueError: pass
            del deljobs
            return numjobs

        return shoot()


def interval(sleeptime, repeat=0):
    """ interval decorator. """
    group = calledfrom(sys._getframe())

    def decorator(function):
        decorator.func_dict = function.func_dict

        def wrapper(*args, **kw):
            job = JobInterval(sleeptime, repeat, function, *args, **kw)
            job.group = group
            job.description = whichmodule()
            periodical.jobs.append(job)
            logging.warn('new interval job %d with sleeptime %d' % (job.id(), sleeptime))
        return wrapper

    return decorator

def at(start, interval=1, repeat=1):

    """ at decorator. """
    group = calledfrom(sys._getframe())

    def decorator(function):
        decorator.func_dict = function.func_dict

        def wrapper(*args, **kw):
            job = JobAt(start, interval, repeat, function, *args, **kw)
            job.group = group
            job.description = whichmodule()
            periodical.jobs.append(job)

        wrapper.func_dict = function.func_dict
        return wrapper

    return decorator

def persecond(function):
    """ per second decorator. """
    minutely.func_dict = function.func_dict
    group = calledfrom(sys._getframe())

    def wrapper(*args, **kw):
        job = JobInterval(1, 0, function, *args, **kw)
        job.group = group
        job.description = whichmodule()
        periodical.jobs.append(job)
        logging.debug('new interval job %d running per second' % job.id())

    return wrapper

def minutely(function):
    """ minute decorator. """
    minutely.func_dict = function.func_dict
    group = calledfrom(sys._getframe())

    def wrapper(*args, **kw):
        job = JobInterval(60, 0, function, *args, **kw)
        job.group = group
        job.description = whichmodule()
        periodical.jobs.append(job)
        logging.debug('new interval job %d running minutely' % job.id())

    return wrapper

def hourly(function):
    """ hour decorator. """
    logging.warn('@hourly(%s)' % str(function))
    hourly.func_dict = function.func_dict
    group = calledfrom(sys._getframe())

    def wrapper(*args, **kw):
        job = JobInterval(3600, 0, function, *args, **kw)
        job.group = group
        job.description = whichmodule()
        logging.warn('new interval job %d running hourly' % job.id())
        periodical.jobs.append(job)

    return wrapper

def daily(function):
    """ day decorator. """
    logging.warn('@daily(%s)' % str(function))
    daily.func_dict = function.func_dict
    group = calledfrom(sys._getframe())

    def wrapper(*args, **kw):
        job = JobInterval(86400, 0, function, *args, **kw)
        job.group =  group
        job.description = whichmodule()
        periodical.jobs.append(job)
        logging.warb('new interval job %d running daily' % job.id())

    return wrapper

periodical = Periodical()

callbacks.add("TICK", periodical.looponce)
