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
log = logging.getLogger('asybot')
hdlr = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON)
formatter = logging.Formatter( '%(filename)s: %(levelname)s: %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
logging.basicConfig(level = logging.INFO)

# s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g -- removes color codes


class asybot(asychat):
  def __init__(self, server, port, channels, realname, nickname, username, hostname, ircname, hammer_interval, alarm_timeout, kill_timeout):
    asychat.__init__(self)
    self.server = server
    self.port = port
    self.channels = channels
    self.realname = realname
    self.nickname = nickname
    self.username = username
    self.hostname = hostname
    self.ircname = ircname
    self.data = ''
    self.myterminator = '\r\n'
    self.set_terminator(self.myterminator.encode())
    self.create_socket(AF_INET, SOCK_STREAM)
    self.connect((self.server, self.port))
    self.wrapper = TextWrapper(subsequent_indent=" ",width=400)

    log.info('=> irc://%s@%s:%s/%s' % (self.nickname, self.server, self.port, self.channels))

    # When we don't receive data for alarm_timeout seconds then issue a
    # PING every hammer_interval seconds until kill_timeout seconds have
    # passed without a message.  Any incoming message will reset alarm.
    self.alarm_timeout = alarm_timeout
    self.hammer_interval = hammer_interval
    self.kill_timeout = kill_timeout
    signal(SIGALRM, lambda signum, frame: self.alarm_handler())
    self.reset_alarm()


  def reset_alarm(self):
    self.last_activity = date.now()
    alarm(self.alarm_timeout)

  def alarm_handler(self):
    delta = date.now() - self.last_activity
    if delta > timedelta(seconds=self.kill_timeout):
      log.error('No data for %s.  Giving up...' % delta)
      exit(2)
    else:
      log.error('No data for %s.  PINGing server...' % delta)
      self.push('PING :%s' % self.nickname)
      alarm(self.hammer_interval)

  def collect_incoming_data(self, data):
    self.data += data.decode(encoding='UTF-8')

  def found_terminator(self):
    log.debug('<< %s' % self.data)

    message = self.data
    self.data = ''

    _, prefix, command, params, rest, _ = \
        split('^(?::(\S+)\s)?(\S+)((?:\s[^:]\S*)*)(?:\s:(.*))?$', message)
    params = params.split(' ')[1:]

    if command == 'PING':
      self.push('PONG :%s' % rest)
      log.debug("Replying to servers PING with PONG :%s" %rest)

    elif command == 'PRIVMSG':
      self.on_privmsg(prefix, command, params, rest)

    elif command == '433':
      # ERR_NICKNAMEINUSE, retry with another name
      _, nickname, int, _ = split('^.*[^0-9]([0-9]+)$', self.nickname) \
          if search('[0-9]$', self.nickname) \
          else ['', self.nickname, 0, '']
      self.nickname = nickname + str(int + 1)
      self.handle_connect()

    self.reset_alarm()

  def push(self, message):
    log.debug('>> %s' % message)
    msg = (message + self.myterminator).encode()
    log.debug('>> %s' % msg)
    asychat.push(self, msg)

  def handle_connect(self):
    self.push('NICK %s' % self.nickname)
    self.push('USER %s %s %s :%s' %
        (self.username, self.hostname, self.server, self.realname))
    self.push('JOIN %s' % ','.join(self.channels))

  def on_privmsg(self, prefix, command, params, rest):
    pass

  def PRIVMSG(self, target, text):
    for line in self.wrapper.wrap(text):
      msg = 'PRIVMSG %s :%s' % (','.join(target), line)
      log.info(msg)
      self.push(msg)
      sleep(1)

  def ME(self, target, text):
    self.PRIVMSG(target, ('ACTION ' + text + ''))
