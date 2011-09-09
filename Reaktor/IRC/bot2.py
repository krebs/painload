#! /usr/bin/env python
#
# //Reaktor/IRC/bot2.py
#

from __future__ import print_function
from irclib import SimpleIRCClient, ServerConnectionError, is_channel
from sys import exit
from os import environ as env
import re

class IRCBot(SimpleIRCClient):
  def __init__(self, target):
    SimpleIRCClient.__init__(self)
    self.target = target

  def on_pubmsg(self, connection, event):

    def PRIVMSG(target, text):
      self.connection.privmsg(target, text)

    def ME(target, text):
      PRIVMSG(target, 'ACTION ' + text + '')

    def is_executable(x):
      import os
      return os.path.exists(x) and os.access(x, os.X_OK)

    _nickname = connection.get_nickname()
    _source = event.source()
    _from = _source.split('!', 1)[0]
    _target = event.target()

    try:
      _, _handle, _command, _argument, _ = re.split(
          '^(\w+|\*):\s*(\w+)(?:\s+(.*))?$', event.arguments()[0])
    except ValueError, error:
      if re.search(_nickname, event.arguments()[0]):
        PRIVMSG(self.target, 'I\'m so famous')
      return # ignore

    if _handle == _nickname or _handle == '*':

      from os.path import realpath, dirname, join
      from subprocess import Popen as popen, PIPE

      Reaktor_dir = dirname(realpath(dirname(__file__)))
      public_commands = join(Reaktor_dir, 'public_commands')
      command = join(public_commands, _command)

      if is_executable(command):

        env = {}
        if _argument != None:
          env['argument'] = _argument

        try:
          p = popen([command], stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
        except OSError, error:
          ME(self.target, 'is made of stupid')
          print('OSError@%s: %s' % (command, error))
          return

        stdout, stderr = [ x[:len(x)-1] for x in
            [ x.split('\n') for x in p.communicate()]]
        code = p.returncode
        pid = p.pid

        print('command: %s -> %s' % (command, code))
        [print('%s stdout: %s' % (pid, x)) for x in stdout]
        [print('%s stderr: %s' % (pid, x)) for x in stderr]

        if code == 0:
          [PRIVMSG(self.target, x) for x in stdout]
          [PRIVMSG(_source, x) for x in stderr]
        else:
          ME(self.target, 'mimimi')

      else:
        if _handle != '*':
          PRIVMSG(self.target, _from + ': you are made of stupid')

  def on_welcome(self, connection, event):
    print('I\'m welcome! :D joining to %s now...' % (self.target))
    if is_channel(self.target):
      connection.join(self.target)
    else:
      self.connection.privmsg(self.target, 'lol')
      self.connection.quit('Pong timeout: 423 seconds')

  def on_join(self, connection, event):
    print('Es passiert in %s' % (self.target))

  def on_disconnect(self, connection, event):
    # TODO reconnect
    exit(0)

# retrieve the value of a [singleton] variable from a tinc.conf(5)-like file
def getconf1(x, path):
  from re import findall
  pattern = '(?:^|\n)\s*' + x + '\s*=\s*(.*\w)\s*(?:\n|$)'
  y = findall(pattern, open(path, 'r').read())
  if len(y) < 1:
    raise AttributeError("len(getconf1('%s', '%s') < 1)" % (x, path))
  if len(y) > 1:
    y = ' '.join(y)
    raise AttributeError("len(getconf1('%s', '%s') > 1)\n  ====>  %s"
        % (x, path, y))
  return y[0]

def main():
  name = getconf1('Name', '/etc/tinc/retiolum/tinc.conf')
  nick = str(env.get('nick', name))
  host = str(env.get('host', 'supernode'))
  port = int(env.get('port', 6667))
  target = str(env.get('target', '#retiolum'))
  print('====> irc://%s@%s:%s/%s' % (nick, host, port, target))

  client = IRCBot(target)
  try:
    from getpass import getuser
    client.connect(host, port, nick, username=getuser(),
        ircname='//Reaktor running at %s.retiolum' % (name))
  except ServerConnectionError, error:
    print(error)
    exit(1)
  client.start()

if __name__ == "__main__":
  main()
