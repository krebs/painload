# jsb/threadloop.py
#
#

""" class to implement start/stoppable threads. """

## lib imports

from jsb.utils.exception import handle_exception
from threads import start_new_thread, getname

## basic imports

import Queue
import time
import logging

## ThreadLoop class

class ThreadLoop(object):

    """ implement startable/stoppable threads. """

    def __init__(self, name="", queue=None):
        self.name = name or 'idle'
        self.stopped = False
        self.running = False
        self.outs = []
        self.queue = queue or Queue.Queue()
        self.nowrunning = "none"

    def _loop(self):
        """ the threadloops loop. """
        logging.warn('starting loop %s' % str(self))
        self.running = True
        nrempty = 0
        while not self.stopped:
            try: data = self.queue.get()
            except Queue.Empty:
                time.sleep(0.01)
                continue
            if self.stopped: break
            if not data: break
            self.handle(*data)
        self.running = False
        logging.warn('stopping loop- %s' % str(self))

    def put(self, *data):
        """ put data on task queue. """
        self.queue.put_nowait(data)

    def start(self):
        """ start the thread. """
        if not self.running and not self.stopped: start_new_thread(self._loop, ())

    def stop(self):
        """ stop the thread. """
        self.stopped = True
        self.running = False
        self.queue.put_nowait(None)

    def handle(self, *args, **kwargs):
        """ overload this. """
        pass

## RunnerLoop class

class RunnerLoop(ThreadLoop):

    """ dedicated threadloop for bot commands/callbacks. """

    def put(self, *data):
        """ put data on task queue. """
        self.queue.put_nowait(data)

    def _loop(self):
        """ runner loop. """
        logging.debug('%s - starting threadloop' % self.name)
        self.running = True
        while not self.stopped:
            try: data = self.queue.get()
            except Queue.Empty:
                time.sleep(0.1)
                continue
            if self.stopped: break
            if not data: break
            self.nowrunning = getname(data[1])
            try: self.handle(*data)
            except Exception, ex: handle_exception()
        self.running = False
        logging.debug('%s - stopping threadloop' % self.name)

class TimedLoop(ThreadLoop):

    """ threadloop that sleeps x seconds before executing. """

    def __init__(self, name, sleepsec=300, *args, **kwargs):
        ThreadLoop.__init__(self, name, *args, **kwargs)
        self.sleepsec = sleepsec

    def _loop(self):
        """ timed loop. sleep a while. """
        logging.debug('%s - starting timedloop (%s seconds)' % (self.name, self.sleepsec))
        self.stopped = False
        self.running = True
        while not self.stopped:
            time.sleep(self.sleepsec)
            if self.stopped:
                logging.debug("%s - loop is stopped" % self.name)
                break
            try: self.handle()
            except Exception, ex: handle_exception()
        self.running = False
        logging.debug('%s - stopping timedloop' % self.name)
