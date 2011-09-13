#! /usr/bin/env python
#
# //Reaktor/IRC/asybot.py
#

from __future__ import print_function

def is_executable(x):
  import os
  return os.path.exists(x) and os.access(x, os.X_OK)

from asynchat import async_chat as asychat
from asyncore import loop
from socket import AF_INET, SOCK_STREAM
from signal import SIGALRM, signal, alarm
from datetime import datetime as date, timedelta
from sys import exit
from re import split, search
class asybot(asychat):
  def __init__(self, server, port, nickname, targets, **kwargs):
    asychat.__init__(self)
    self.server = server
    self.port = port
    self.nickname = nickname
    self.targets = targets
    self.username = kwargs['username'] if 'username' in kwargs else nickname
    self.hostname = kwargs['hostname'] if 'hostname' in kwargs else nickname
    self.ircname = kwargs['ircname'] if 'ircname' in kwargs else nickname
    self.realname = kwargs['realname'] if 'realname' in kwargs else nickname
    self.data = ''
    self.set_terminator('\r\n')
    self.create_socket(AF_INET, SOCK_STREAM)
    self.connect((self.server, self.port))
    self.alarm_timeout = 300
    self.kill_timeout = 360
    self.last_activity = date.now()
    signal(SIGALRM, lambda signum, frame: self.alarm_handler())
    alarm(self.alarm_timeout)
    loop()

  def alarm_handler(self):
    delta = date.now() - self.last_activity
    if delta > timedelta(seconds=self.kill_timeout):
      print('kill alarm %s' % delta)
      exit()
    else:
      print('alarm %s' % delta)
      self.push('PING :asybot')
      alarm(self.alarm_timeout)

  def collect_incoming_data(self, data):
    self.data += data

  def found_terminator(self):
    print('< %s' % self.data)
    self.last_activity = date.now()

    message = self.data
    self.data = ''

    _, prefix, command, params, rest, _ = \
        split('^(?::(\S+)\s)?(\S+)((?:\s[^:]\S*)*)(?:\s:(.*))?$', message)
    params = params.split(' ')[1:]
    #print([prefix, command, params, rest])

    if command == 'PING':
      self.push('PONG :%s' % rest)

    elif command == 'PRIVMSG':
      self.on_privmsg(prefix, command, params, rest)

    # reset alarm
    alarm(self.alarm_timeout)

  def push(self, message):
    print('> %s' % message)
    asychat.push(self, message + self.get_terminator())

  def handle_connect(self):
    self.push('NICK %s' % self.nickname)
    self.push('USER %s %s %s :%s' %
        (self.username, self.hostname, self.server, self.realname))
    self.push('JOIN %s' % ','.join(self.targets))

  def on_privmsg(self, prefix, command, params, rest):
    def PRIVMSG(text):
      self.push('PRIVMSG %s :%s' % (','.join(params), text))

    def ME(text):
      PRIVMSG('ACTION ' + text + '')

    _from = prefix.split('!', 1)[0]

    try:
      _, _handle, _command, _argument, _ = split(
          '^(\w+|\*):\s*(\w+)(?:\s+(.*))?$', rest)
    except ValueError, error:
      if search(self.nickname, rest):
        PRIVMSG('I\'m so famous')
      return # ignore

    if _handle == self.nickname or _handle == '*':

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
          ME('is made of stupid')
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
          [PRIVMSG(x) for x in stdout]
          [PRIVMSG(x) for x in stderr]
        else:
          ME('mimimi')

      else:
        if _handle != '*':
          PRIVMSG(_from + ': you are made of stupid')

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

if __name__ == "__main__":
  from os import environ as env
  name = getconf1('Name', '/etc/tinc/retiolum/tinc.conf')
  hostname = '%s.retiolum' % name
  nick = str(env.get('nick', name))
  host = str(env.get('host', 'supernode'))
  port = int(env.get('port', 6667))
  target = str(env.get('target', '#retiolum'))
  print('====> irc://%s@%s:%s/%s' % (nick, host, port, target))

  from getpass import getuser
  asybot(host, port, nick, [target], username=getuser(),
      ircname='//Reaktor running at %s' % hostname,
      hostname=hostname)
