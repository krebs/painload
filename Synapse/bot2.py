#! /usr/bin/env python

from irclib import SimpleIRCClient, ServerConnectionError, is_channel
from sys import exit
from os import environ as env
import tokenize
import cStringIO
import pprint
import re
pp = pprint.PrettyPrinter(indent=2)

class IRCBot(SimpleIRCClient):
  def __init__(self, target):
    SimpleIRCClient.__init__(self)
    self.target = target

  def on_welcome(self, connection, event):
    print 'I\'m welcome! :D joining to %s now...' % (self.target)
    if is_channel(self.target):
      connection.join(self.target)
    else:
      self.connection.privmsg(self.target, 'lol')
      self.connection.quit('Pong timeout: 423 seconds')

  def on_join(self, connection, event):
    print 'Es passiert in %s' % (self.target)

  def on_disconnect(self, connection, event):
    exit(0)

  def on_pubmsg(self, connection, event):
    arguments = ''.join(event.arguments())
    nickname = connection.get_nickname()
    server_name = connection.get_server_name()
    is_connected = connection.is_connected()
    #readline = cStringIO.StringIO(''.join(event.arguments())).readline
    #self.connection.privmsg(self.target, 'nickname: ' + nickname)
    #self.connection.privmsg(self.target, 'server_name: ' + server_name)

    arguments = re.split(':\s+', arguments, 1)
    if len(arguments) != 2:
      return

    target, arguments = arguments

    arguments = re.split('\s+', arguments, 1)

    command, arguments = arguments if len(arguments) == 2 else [arguments[0],[]]

    self.connection.privmsg(self.target, '- target: ' + target)
    self.connection.privmsg(self.target, '- command: ' + command)
    self.connection.privmsg(self.target, '- arguments: ' + pp.pformat(arguments))
    

def main():
  host = str(env.get('host', 'irc.freenode.org'))
  port = int(env.get('port', 6667))
  nick = str(env.get('nick', 'crabspasm'))
  target = str(env.get('target', '#tincspasm'))
  print '====> irc://%s@%s:%s/%s' % (nick, host, port, target)

  client = IRCBot(target)
  try:
    client.connect(host, port, nick)
  except ServerConnectionError, error:
    print error
    exit(1)
  client.start()

if __name__ == "__main__":
    main()
