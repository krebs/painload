# handler_xmpp.py
#
#

""" xmpp request handler. """

## jsb imports

from jsb.utils.generic import fromenc, toenc
from jsb.version import getversion
from jsb.utils.lazydict import LazyDict
from jsb.utils.exception import handle_exception
from jsb.lib.plugins import plugs
from jsb.lib.boot import boot, plugin_packages

## gaelib imports

from jsb.drivers.gae.xmpp.bot import XMPPBot
from jsb.drivers.gae.xmpp.event import XMPPEvent
from jsb.utils.gae.auth import checkuser

## google imports

from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users as gusers
from google.appengine.ext import db
from google.appengine.ext.webapp import xmpp_handlers

## basic imports

import wsgiref.handlers
import sys
import time
import types
import logging

## boot

logging.info(getversion('GAE XMPP'))

boot()

## defines

bot = XMPPBot()

## functions

def xmppbox(response):
    response.out.write("""
          <form action="/_ah/xmpp/message/chat/" method="post">
            <div><b>enter command:</b> <input type="commit" name="body">
          </form>
          """)

## classes

class XMPPHandler(webapp.RequestHandler):

    """ relay incoming messages to the bot. """

    def post(self):
        try:
            logging.info("XMPP incoming: %s" % self.request.remote_addr)
            if not self.request.POST.has_key('from'): logging.debug('no from in POST: %s' % str(self.request.POST)) ; return
            if not self.request.POST.has_key('to'): logging.debug('no to in POST: %s' % str(self.request.POST)) ; return
            event = XMPPEvent(bot=bot).parse(self.request, self.response)
            bot.doevent(event)
        except Exception, ex:
            handle_exception()
            self.response.set_status(500)

application = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', XMPPHandler), ],
                                      debug=True)

def main():
    global application
    global bot
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
