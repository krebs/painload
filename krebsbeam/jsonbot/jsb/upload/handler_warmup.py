# handler_warmup.py
#
#

""" xmpp request handler. """

## jsb imports

from jsb.version import getversion

## google imports

import webapp2

## basic imports

import sys
import time
import types
import logging

## greet

logging.warn(getversion('WARMUP'))

## classes

class WarmupHandler(webapp2.RequestHandler):

    def get(self, url=None):
        logging.warn("warmup")

    post = get

application = webapp2.WSGIApplication([webapp2.Route(r'<url:.*>', WarmupHandler)], 
                                      debug=True)

def main():
    global application
    application.run()

if __name__ == "__main__":
    main()
