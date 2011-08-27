# jsb/socklib/xmpp/wait.py
#
#

""" wait for ircevent based on ircevent.CMND """

## jsb imports

from jsb.utils.locking import lockdec
from jsb.lib.wait import Wait
import jsb.lib.threads as thr

## basic imports

import time
import thread
import logging

## locks

waitlock = thread.allocate_lock()
locked = lockdec(waitlock)

## classes

class XMPPWait(Wait):

    """ wait object for jabber messages. """

    def register(self, catch, queue, timeout=15):
        """ register wait for privmsg. """
        logging.debug('xmpp.wait - registering for %s' % catch)
        self.ticket += 1
        self.waitlist.append((catch, queue, self.ticket))
        if timeout:
            thr.start_new_thread(self.dotimeout, (timeout, self.ticket))
        return self.ticket

    def check(self, msg):
        """ check if <msg> is waited for. """
        for teller in range(len(self.waitlist)-1, -1, -1):
            i = self.waitlist[teller]
            if i[0] == msg.userhost:
                msg.ticket = i[2]
                i[1].put_nowait(msg)
                self.delete(msg.ticket)
                logging.debug('xmpp.wait - got response for %s' % i[0])
                msg.isresponse = 1

    def delete(self, ticket):
        """ delete wait item with ticket nr. """
        for itemnr in range(len(self.waitlist)-1, -1, -1):
            item = self.waitlist[itemnr]
            if item[2] == ticket:
                item[1].put_nowait(None)
                try:
                    del self.waitlist[itemnr]
                    logging.debug('sxmpp.wait - deleted ' + str(ticket))
                except IndexError:
                    pass
                return 1

class XMPPErrorWait(XMPPWait):

    """ wait for jabber errors. """

    def check(self, msg):
        """ check if <msg> is waited for. """
        if not msg.type == 'error':
            return
        errorcode = msg.error

        for teller in range(len(self.waitlist)-1, -1, -1):
            i = self.waitlist[teller]
            if i[0] == 'ALL' or i[0] == errorcode:
                msg.error = msg.error
                msg.ticket = i[2]
                i[1].put_nowait(msg)
                self.delete(msg.ticket)
                logging.debug('sxmpp.errorwait - got error response for %s' % i[0])
