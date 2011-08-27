# handler_channel.py
#
#

""" channel handler. """

## jsb imports

from jsb.lib.channelbase import ChannelBase
from jsb.version import getversion
from jsb.utils.name import stripname

## google imports

import webapp2

## basic imports

import sys
import time
import types
import logging

## greet

logging.warn(getversion('CHANNEL'))

## classes

class ChannelHandler(webapp2.RequestHandler):

    def post(self, url=None):
        try:
            logging.warn("url is %s" % url)
            if not url: self.response.set_status(404)
            client_id = self.request.get('from')
            logging.warn("client_id is %s" % client_id)
            if client_id: 
                try: (id, t) = client_id.split("-", 1)
                except Exception, ex: logging.warn(str(ex)) ; self.response.set_status(500) ; return
            logging.warn("channel id is %s" % id)
            chan = ChannelBase(id, 'gae-web')
            if "disconnected" in url: 
                if client_id in chan.data.webchannels: chan.data.webchannels.remove(client_id) ; chan.save() ; logging.warn("removed channel %s" % client_id) ; return
            elif "connected" in url:
                if client_id not in chan.data.webchannels: chan.data.webchannels.append(client_id) ; chan.save() ; logging.warn("added channel %s" % client_id) ; return
            elif "error" in url:
                logging.warn(dir(self.request))
                logging.warn(self.request.body)
                logging.warn(dir(self.response))
                logging.warn(self.response)
                logging.warn(url)
                if client_id in chan.data.webchannels: chan.data.webchannels.remove(client_id) ; chan.save() ; logging.warn("removed channel %s" % client_id)
        except Exception, ex: handle_exception(); self.response.set_status(500)

application = webapp2.WSGIApplication([webapp2.Route(r'<url:.*>', ChannelHandler)], 
                                      debug=True)

def main():
    global application
    application.run()

if __name__ == "__main__":
    main()
