# handler_dispatch.py
#
#

""" jsb dispatch handler.  dispatches remote commands.  """

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

logging.warn(getversion('GAE DISPATCH'))

bot = WebBot(botname="gae-web")

class Dispatch_Handler(RequestHandler):

    """ the bots remote command dispatcher. """

    def options(self):
         self.response.headers.add_header('Content-Type', 'application/x-www-form-urlencoded')
         #self.response.headers.add_header("Cache-Control", "private")
         self.response.headers.add_header("Server", getversion())
         self.response.headers.add_header("Public", "*")
         self.response.headers.add_header('Accept', '*')
         self.response.headers.add_header('Access-Control-Allow-Origin', self.request.headers['Origin'])
         self.response.out.write("Allow: *")
         self.response.out.write('Access-Control-Allow-Origin: *') 
         logging.warn("dispatch - options response send to %s - %s" % (self.request.remote_addr, str(self.request.headers)))

    def post(self):

        """ this is where the command get disaptched. """
        starttime = time.time()
        try:
            logging.warn("DISPATCH incoming: %s - %s" % (self.request.get('content'), self.request.remote_addr))
            if not gusers.get_current_user():
                logging.warn("denied access for %s - %s" % (self.request.remote_addr, self.request.get('content')))
                self.response.out.write("acess denied .. plz login")
                self.response.set_status(400)
                return
            event = WebEvent(bot=bot).parse(self.response, self.request)
            event.cbtype = "DISPATCH"
            event.type = "DISPATCH"
            (userhost, user, u, nick) = checkuser(self.response, self.request, event)
            bot.gatekeeper.allow(userhost)
            event.bind(bot)
            bot.doevent(event)
        except NoSuchCommand:
            self.response.out.write("no such command: %s" % event.usercmnd)
        except google.appengine.runtime.DeadlineExceededError, ex:
            self.response.out.write("the command took too long to finish: %s" % str(time.time()-starttime))
        except Exception, ex:
            self.response.out.write("the command had an eror: %s" % exceptionmsg())
            handle_exception()

    get = post

# the application 

application = WSGIApplication([Route('/dispatch/', Dispatch_Handler),
                               Route('/dispatch', Dispatch_Handler) ], debug=True)

def main():
    global bot
    global application
    try: application.run()
    except google.appengine.runtime.DeadlineExceededError:
        pass
    except Exception, ex:
        logging.error("dispatch - %s" % str(ex))

if __name__ == "__main__":
    main()
