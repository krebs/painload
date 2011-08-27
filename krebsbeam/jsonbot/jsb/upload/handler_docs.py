# handler_docs.py
#
#

""" xmpp request handler. """

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.version import getversion

## google imports

import webapp2

## basic imports

import sys
import time
import types
import logging
import os

## greet

logging.warn(getversion('REDIRECT'))

## classes

class DocsHandler(webapp2.RequestHandler):

    def get(self, url=None):
        try:
            if not url.endswith(".html"):
                if not url.endswith('/'):
                    url += u"/index.html"
                else:
                    url += u"index.html"
            splitted = url.split(os.sep)
            splitted.insert(2, 'html')
            goto = os.sep.join(splitted)
            if goto in url: self.response.set_status(404) ; return
            logging.warn("docs - redirecting %s" % goto)
            self.redirect(goto)
        except Exception, ex:
            handle_exception()
            self.response.set_status(500)

application = webapp2.WSGIApplication([webapp2.Route(r'<url:.*>', DocsHandler)], 
                                      debug=True)

def main():
    global application
    application.run()

if __name__ == "__main__":
    main()
