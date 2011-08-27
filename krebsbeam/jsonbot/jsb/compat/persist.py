# gozerbot/persist.py
#
#

""" 
    allow data to be pickled to disk .. creating the persisted object
    restores data
"""

## basic imports 

import cPickle
import thread
import os
import copy
import logging

## defines

saving = []
stopsave = 0

## Persist

class Persist(object):

    """ persist data attribute to pickle file """

    def __init__(self, filename, default=None):
        logging.info('reading %s' % filename)
        self.fn = filename
        self.lock = thread.allocate_lock()
        self.data = None
        # load data from pickled file
        try:
            datafile = open(filename, 'r')
        except IOError:
            if default != None:
                self.data = copy.deepcopy(default)
            return
        try:
            self.data = cPickle.load(datafile)
            datafile.close()
        except:
            if default != None:
                self.data = copy.deepcopy(default)
            else:
                logging.error('ERROR: %s' % filename)
                raise

    def save(self):
        """ save persist data """
        if stopsave:
            logging.warn('stopping mode .. not saving %s' % self.fn)
            return
        try:
            saving.append(str(self.fn))
            self.lock.acquire()
            # first save to temp file and when done rename
            tmp = self.fn + '.tmp'
            try:
                datafile = open(tmp, 'w')
            except IOError:
                logging.error("can't save %s" % self.fn)
                return
            cPickle.dump(self.data, datafile)
            datafile.close()
            os.rename(tmp, self.fn)
            logging.warn('%s saved' % self.fn)
        finally:
            saving.remove(self.fn)
            self.lock.release()
