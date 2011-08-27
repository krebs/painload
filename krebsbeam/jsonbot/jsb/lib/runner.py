# jsb/runner.py
#
#

""" threads management to run jobs. """

## jsb imports

from jsb.lib.threads import getname, start_new_thread, start_bot_command
from jsb.utils.exception import handle_exception
from jsb.utils.locking import locked, lockdec
from jsb.utils.lockmanager import rlockmanager, lockmanager
from jsb.utils.generic import waitevents
from jsb.utils.trace import callstack
from jsb.lib.threadloop import RunnerLoop
from jsb.lib.callbacks import callbacks

## basic imports

import Queue
import time
import thread
import random
import logging
import sys

## Runner class

class Runner(RunnerLoop):

    """
        a runner is a thread with a queue on which jobs can be pushed. 
        jobs scheduled should not take too long since only one job can 
        be executed in a Runner at the same time.

    """

    def __init__(self, name="runner", doready=True):
        RunnerLoop.__init__(self, name)
        self.working = False
        self.starttime = time.time()
        self.elapsed = self.starttime
        self.finished = time.time()
        self.doready = doready

    def handle(self, descr, func, *args, **kwargs):
        """ schedule a job. """
        self.working = True
        name = getname(str(func))
        try:
            #rlockmanager.acquire(getname(str(func)))
            name = getname(str(func))
            self.name = name
            logging.debug('running %s: %s' % (descr, name))
            self.starttime = time.time()
            func(*args, **kwargs)
            self.finished = time.time()
            self.elapsed = self.finished - self.starttime
            if self.elapsed > 3:
                logging.debug('ALERT %s %s job taking too long: %s seconds' % (descr, str(func), self.elapsed))
        except Exception, ex: handle_exception()
        #finally: rlockmanager.release()
        self.working = False

## BotEventRunner class

class BotEventRunner(Runner):

    def handle(self, descr, func, bot, ievent, *args, **kwargs):
        """ schedule a bot command. """
        try:
            self.starttime = time.time()
            lockmanager.acquire(getname(str(func)))
            name = getname(str(func))
            self.name = name
            self.working = True
            logging.debug("now running %s" % name)
            func(bot, ievent, *args, **kwargs)
            self.finished = time.time()
            self.elapsed = self.finished - self.starttime
            if self.elapsed > 3:
                logging.info('ALERT %s %s job taking too long: %s seconds' % (descr, str(func), self.elapsed))
            #if ievent.iscommand: ievent.ready()
            if not ievent.type == "OUTPUT" and not ievent.dontclose: ievent.ready()
            #time.sleep(0.001)
        except Exception, ex:
            handle_exception(ievent)
        finally: lockmanager.release(getname(str(func)))
        self.working = False
        self.name = "finished"

## Runners class

class Runners(object):

    """ runners is a collection of runner objects. """

    def __init__(self, max=100, runnertype=Runner, doready=True):
        self.max = max
        self.runners = []
        self.runnertype = runnertype
        self.doready = doready

    def runnersizes(self):
        """ return sizes of runner objects. """
        result = []
        for runner in self.runners: result.append("%s - %s" % (runner.queue.qsize(), runner.name))
        return result

    def stop(self):
        """ stop runners. """
        for runner in self.runners: runner.stop()

    def start(self):
        """ overload this if needed. """
        pass
 
    def put(self, *data):
        """ put a job on a free runner. """
        logging.debug("size is %s" % len(self.runners))
        for runner in self.runners:
            if not runner.queue.qsize():
                runner.put(*data)
                return
        runner = self.makenew()
        runner.put(*data)
         
    def running(self):
        """ return list of running jobs. """
        result = []
        for runner in self.runners:
            if runner.queue.qsize(): result.append(runner.nowrunning)
        return result

    def makenew(self):
        """ create a new runner. """
        runner = None
        for i in self.runners:
            if not i.queue.qsize(): return i
        if len(self.runners) < self.max:
            runner = self.runnertype(self.doready)
            runner.start()
            self.runners.append(runner)
        else: runner = random.choice(self.runners)
        return runner

    def cleanup(self):
        """ clean up idle runners. """
        if not len(self.runners): logging.debug("nothing to clean")
        for index in range(len(self.runners)-1, -1, -1):
            runner = self.runners[index]
            logging.debug("cleanup %s" % runner.name)
            if not runner.queue.qsize():
                try: runner.stop() ; del self.runners[index]
                except IndexError: pass
                except: handle_exception()
            else: logging.info("now running: %s" % runner.nowrunning)

## show runner status

def runner_status():
    print cmndrunner.runnersizes()
    print callbackrunner.runnersizes()


## global runners

cmndrunner = defaultrunner = longrunner = Runners(20, BotEventRunner)
callbackrunner = Runners(100, BotEventRunner, doready=False)
waitrunner = Runners(10, BotEventRunner, doready=False)

## cleanup 

def runnercleanup(bot, event):
    cmndrunner.cleanup()
    logging.debug("cmndrunner sizes: %s" % str(cmndrunner.runnersizes()))
    callbackrunner.cleanup()
    logging.debug("callbackrunner sizes: %s" % str(cmndrunner.runnersizes()))
    waitrunner.cleanup()
    logging.debug("waitrunner sizes: %s" % str(cmndrunner.runnersizes()))

callbacks.add("TICK", runnercleanup)
