#! /usr/bin/env python
#
# //Reaktor/IRC/asybot.py
#
from asynchat import async_chat as asychat
from asyncore import loop
from socket import AF_INET, SOCK_STREAM,gethostname
from signal import SIGALRM, signal, alarm
from datetime import datetime as date, timedelta
from time import sleep
from sys import exit
from re import split, search, match
from textwrap import TextWrapper

import logging,logging.handlers

# s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g -- removes color codes


class asybot(asychat):
  def __init__(self, server, port, nickname, channels, realname=False, username=False, hostname=False, hammer_interval=10, alarm_timeout=300, kill_timeout=360, loglevel=logging.ERROR):
    asychat.__init__(self)
    #logger magic
    self.log = logging.getLogger('asybot_' + nickname)
    self.nickname = nickname

    if realname:
      self.realname = realname
    else:
      self.realname = nickname

    if username:
      self.username = username
    else:
      self.username = nickname

    if hostname:
      self.hostname = hostname
    else:
      self.hostname = nickname

    self.retry = True
    self.server = server
    self.port = port
    self.channels = channels
    self.data = ''
    self.myterminator = '\r\n'
    self.set_terminator(self.myterminator.encode())
    self.create_socket(AF_INET, SOCK_STREAM)
    self.connect((self.server, self.port))
    self.wrapper = TextWrapper(subsequent_indent=" ",width=400)

    self.log.info('=> irc://%s@%s:%s/%s' % (self.nickname, self.server, self.port, self.channels))

    # When we don't receive data for alarm_timeout seconds then issue a
    # PING every hammer_interval seconds until kill_timeout seconds have
    # passed without a message.  Any incoming message will reset alarm.
    self.alarm_timeout = alarm_timeout
    self.hammer_interval = hammer_interval
    self.kill_timeout = kill_timeout
    try:
      signal(SIGALRM, lambda signum, frame: self.alarm_handler())
    except Exception as e:
      print('asybot: ' + str(e))
    self.reset_alarm()

  def reset_alarm(self):
    self.last_activity = date.now()
    alarm(self.alarm_timeout)

  def alarm_handler(self):
    delta = date.now() - self.last_activity
    if delta > timedelta(seconds=self.kill_timeout):
      self.log.error('No data for %s.  Giving up...' % delta)
      self.handle_disconnect()
    else:
      self.log.error('No data for %s.  PINGing server...' % delta)
      self.push('PING :%s' % self.nickname)
      alarm(self.hammer_interval)

  def collect_incoming_data(self, data):
    try:
      self.data += data.decode()
    except Exception as e:
      print('error decoding message: ' + str(e));
      print('current data: %s' % self.data);
      print('received data: %s' % data);
      print('trying to decode as latin1')
      self.data += data.decode('latin1')

  def found_terminator(self):
    self.log.debug('<< %s' % self.data)

    message = self.data
    self.data = ''
    try:
        _, prefix, command, params, rest, _ = \
            split('^(?::(\S+)\s)?(\S+)((?:\s[^:]\S*)*)(?:\s:(.*))?$', message)
    except Exception as e:
        print("cannot split message :(\nmsg: %s"%message)
        return
    params = params.split(' ')[1:]

    if command == 'PING':
      self.push('PONG :%s' % rest)
      self.log.debug("Replying to servers PING with PONG :%s" %rest)
      self.on_ping(prefix, command, params, rest)

    elif command == 'PRIVMSG':
      self.on_privmsg(prefix, command, params, rest)

    elif command == 'INVITE':
      self.on_invite(prefix, command, params, rest)

    elif command == 'KICK':
      self.on_kick(prefix, command, params, rest)

    elif command == 'JOIN':
      self.on_join(prefix, command, params, rest)

    elif command == '433':
      # ERR_NICKNAMEINUSE, retry with another name
      self.on_nickinuse(prefix, command, params, rest)

    elif command == '376':
      self.on_welcome(prefix, command, params, rest)

    self.reset_alarm()

  def push(self, message):
    try:
      self.log.debug('>> %s' % message)
      msg = (message + self.myterminator).encode()
      self.log.debug('>> %s' % msg)
      asychat.push(self, msg)
    except:
        pass

  def disconnect(self):
    self.push('QUIT')
    self.close()

  def reconnect(self):
    if self.connected:
      self.push('QUIT')
    self.close()
    self.create_socket(AF_INET, SOCK_STREAM)
    self.connect((self.server, self.port))

  def handle_connect(self):
    self.push('NICK %s' % self.nickname)
    self.push('USER %s %s %s :%s' %
        (self.username, self.hostname, self.server, self.realname))

  def handle_disconnect(self):
    if self.retry:
      self.reconnect()
    else:
      self.log.error('No retry set, giving up')

  def PRIVMSG(self, target, text):
    for line in self.wrapper.wrap(text):
      msg = 'PRIVMSG %s :%s' % (','.join(target), line)
      self.log.info(msg)
      self.push(msg)
      sleep(1)

  def ME(self, target, text):
    self.PRIVMSG(target, ('ACTION ' + text + ''))

  def on_welcome(self, prefix, command, params, rest):
    self.push('JOIN %s' % ','.join(self.channels))

  def on_kick(self, prefix, command, params, rest):
    self.log.debug(params)
    if params[-1] == self.nickname:
      for chan in params[:-1]:
        self.channels.remove(chan)

  def on_join(self, prefix, command, params, rest):
    pass

  def on_ping(self, prefix, command, params, rest):
    pass

  def on_privmsg(self, prefix, command, params, rest):
    pass

  def on_invite(self, prefix, command, params, rest):
    pass

  def on_nickinuse(self, prefix, command, params, rest):
    regex = search('(\d+)$', self.nickname)
    if regex:
      theint = int(regex.group(0))
      self.nickname = self.nickname.strip(str(theint)) + str(theint + 1)
    else:
      self.nickname = self.nickname + '0'
    self.handle_connect()
