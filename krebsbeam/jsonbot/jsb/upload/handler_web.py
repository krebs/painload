# handler_web.py
#
#

""" web request handler. """

import time
import logging

## jsb imports

from jsb.version import getversion
from jsb.utils.exception import handle_exception
from jsb.lib.channelbase import ChannelBase

## gaelib import

from jsb.utils.gae.auth import finduser
from jsb.utils.gae.web import start, closer, loginurl, logouturl, login

## google imports

from webapp2 import RequestHandler, Route, WSGIApplication
from google.appengine.api import channel

## basic imports

import sys
import time
import types
import os
import logging
import google
import urllib

## init

logging.info(getversion('GAE WEB'))

## classes

class HomePageHandler(RequestHandler):

    """ the bots web command dispatcher. """


    def options(self):
        self.response.headers.add_header("Allow: *")
        
    def get(self):
        """ show basic page. """

        logging.warn("web_handler - in")
        try:
            logout = logouturl(self.request, self.response)
            user = finduser()
            if user:
                start(self.response, {'appname': 'JSONBOT' , 'who': user, 'loginurl': 'logged in', 'logouturl': logout, 'onload': 'consoleinit();'})
            else: 
                login(self.response, {'appname': 'JSONBOT' , 'who': "nobody", 'loginurl': 'not logged in', 'logouturl': logout, 'onload': 'consoleinit();'})

        except google.appengine.runtime.DeadlineExceededError:
            self.response.out.write("DeadLineExceededError .. this request took too long to finish.")
        except Exception, ex:
            #self.response.out.write("An exception occured: %s" % str(ex))
            handle_exception()
            self.response.set_status(500)
            #try: os._exit(1)
            #except: pass
        logging.warn("web_handler - out")

## the application 

application = WSGIApplication([('/', HomePageHandler)],
                               debug=True)

## main

def main():
    global application
    application.run()

if __name__ == "__main__":
    main()
