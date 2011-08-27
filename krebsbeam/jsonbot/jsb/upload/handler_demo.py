# handler_demo.py
#
#

""" jsb demo handler.  dispatches remote commands.  """

## boot

from jsb.lib.boot import boot
boot()

## jsb imports

from jsb.utils.generic import fromenc, toenc
from jsb.version import getversion
from jsb.utils.xmpp import stripped
from jsb.utils.url import getpostdata, useragent
from jsb.lib.plugins import plugs
from jsb.lib.persist import Persist
from jsb.utils.exception import handle_exception, exceptionmsg
from jsb.lib.fleet import fleet
from jsb.lib.errors import NoSuchCommand
from jsb.utils.lazydict import LazyDict
from jsb.utils.gae.web import start, closer, loginurl, logouturl, login, demo
from jsb.lib.config import getmainconfig

## gaelib imports

from jsb.lib.botbase import BotBase
from jsb.drivers.gae.web.bot import WebBot
from jsb.drivers.gae.web.event import WebEvent
from jsb.utils.gae.auth import checkuser

## google imports

from webapp2 import RequestHandler, Route, WSGIApplication
from google.appengine.api import users as gusers

## basic imports

import sys
import time
import types
import os
import logging
import google

logging.warn(getversion('GAE DEMO'))

bot = WebBot(botname="gae-web")

class Demo_Handler(RequestHandler):

    """ the bots remote command dispatcher. """

    def options(self):
         if not getmainconfig().demo: self.response.set_status(404) ; return
         self.response.headers.add_header('Content-Type', 'application/x-www-form-urlencoded')
         self.response.headers.add_header("Server", getversion())
         self.response.headers.add_header("Public", "*")
         self.response.headers.add_header('Accept', '*')
         self.response.headers.add_header('Access-Control-Allow-Origin', self.request.headers['Origin'])
         self.response.out.write("Allow: *")
         self.response.out.write('Access-Control-Allow-Origin: *') 
         logging.warn("dispatch - options response send to %s - %s" % (self.request.remote_addr, str(self.request.headers)))

    def get(self):
        """ show basic page. """
        logging.warn("demo_handler - in")
        try:
            if not getmainconfig().demo: self.response.set_status(404) ; return
            logout = logouturl(self.request, self.response)
            user =  "demouser" + "@" + self.request.remote_addr
            demo(self.response, {'appname': 'JSONBOT DEMO' , 'who': user, 'loginurl': 'logged in', 'logouturl': logout, 'onload': 'consoleinit();'})
        except google.appengine.runtime.DeadlineExceededError:
            self.response.out.write("DeadLineExceededError .. this request took too long to finish.")
        except Exception, ex:
            handle_exception()
            self.response.set_status(500)
        logging.warn("demo_handler - out")

    def post(self):

        """ this is where the command get disaptched. """
        starttime = time.time()
        try:
            if not getmainconfig().demo: self.response.set_status(404) ; return
            logging.warn("DEMO incoming: %s - %s" % (self.request.get('content'), self.request.remote_addr))
            event = WebEvent(bot=bot).parse(self.response, self.request)
            event.cbtype = "DISPATCH"
            event.type = "DISPATCH"
            bot.gatekeeper.allow(event.userhost)
            event.bind(bot)
            bot.doevent(event)
        except NoSuchCommand:
            self.response.out.write("no such command: %s" % event.usercmnd)
        except google.appengine.runtime.DeadlineExceededError, ex:
            self.response.out.write("the command took too long to finish: %s" % str(time.time()-starttime))
        except Exception, ex:
            self.response.out.write("the command had an eror: %s" % exceptionmsg())
            handle_exception()

# the application 

application = WSGIApplication([Route('/demo', Demo_Handler),
                               Route('/demo/', Demo_Handler) ], debug=True)

def main():
    global bot
    global application
    try: application.run()
    except google.appengine.runtime.DeadlineExceededError:
        pass
    except Exception, ex:
        logging.error("demo - %s" % str(ex))

if __name__ == "__main__":
    main()
