#!/usr/bin/python
from Queue import Queue
from SocketServer import BaseRequestHandler, ThreadingTCPServer
from threading import Thread
from time import sleep, strftime, strptime

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

class PunaniRequestHandler(BaseRequestHandler):
    """Handler for Punani messages."""

    def handle(self):
        try:
            msg = self.request.recv(1024).strip()
        except ValueError:
            msg = 'Invalid message.'
        else:
            self.server.queue.put((self.client_address, msg))
        print ('%s:%d' % self.client_address), str(msg)


class PunaniReceiveServer(ThreadingTCPServer):
    """UDP server that waits for Punani messages."""

    def __init__(self):
        ThreadingTCPServer.__init__(self, ('127.0.0.1', 5555), PunaniRequestHandler)
        self.queue = Queue()

class PunaniBot(SingleServerIRCBot):

    def __init__(self, server_list, channel_list, nickname='punani-ircbot',
            realname='Bob Ross'):
        SingleServerIRCBot.__init__(self, server_list, nickname, realname)
        self.channel_list = channel_list

    def on_welcome(self, conn, event):
        """Join channels after connect."""
        print 'Connected to %s:%d.' % conn.socket.getsockname()
        for channel, key in self.channel_list:
            conn.join(channel, key)

    def on_nicknameinuse(self, conn, event):
        """Choose another nickname if conflicting."""
        self._nickname += '_'
        conn.nick(self._nickname)

    def on_ctcp(self, conn, event):
        """Answer CTCP PING and VERSION queries."""
        whonick = nm_to_n(event.source())
        message = event.arguments()[0].lower()
        if message == 'version':
            conn.notice(whonick, 'Punani2irc')
        elif message == 'ping':
            conn.pong(whonick)

    def on_privmsg(self, conn, event):
        """React on private messages.

        Die, for example.
        """
        whonick = nm_to_n(event.source())
        message = event.arguments()[0]
        if message == 'die!':
            print 'Shutting down as requested by %s...' % whonick
            self.die('Shutting down.')

    def say(self, msg):
        """Say message to channels."""
        for channel, key in self.channel_list:
            self.connection.privmsg(channel, msg)

def process_queue(announce_callback, queue, delay=2):
    """Process received messages in queue."""
    while True:
        sleep(delay)
        try:
            addr, msg = queue.get()
        except Empty:
            continue
        #do something with the addr?
        announce_callback(str(msg))
if __name__ == '__main__':
    # Set IRC connection parameters.
    irc_servers = [('supernode', 6667)]
    irc_channels = [('#retiolum','')]

    # Prepare and start IRC bot.
    bot = PunaniBot(irc_servers, irc_channels)
    t = Thread(target=bot.start)
    t.daemon = True
    t.start()
    announce = bot.say

    receiver = PunaniReceiveServer()
    t = Thread(target=process_queue,args=(announce,receiver.queue))
    t.daemon = True
    t.start()
    receiver.serve_forever()
