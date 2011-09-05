#! /usr/bin/env python2

from irclib import IRC, ServerConnectionError, is_channel
from sys import exit
from os import environ as env

host = str(env.get('host', 'irc.freenode.org'))
port = int(env.get('port', 6667))
nick = str(env.get('nick', 'crabspasm'))
channel = str(env.get('channel', '#tincspasm'))
print '====> irc://%s@%s:%s/%s' % (nick, host, port, channel)

irc = IRC()
try:
  client = irc.server().connect(host, port, nick)
except ServerConnectionError, error:
  print error
  exit

def on_connect(connection, event):
  connection.join(channel)
  print 'Es passiert...'

def on_join(connection, event):
  connection.privmsg(channel, 'lol')

def on_disconnect(connection, event):
  exit

client.add_global_handler('welcome', on_connect)
client.add_global_handler('join', on_join)
client.add_global_handler('disconnect', on_disconnect)

irc.process_forever()
