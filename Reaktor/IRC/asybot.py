#! /usr/bin/env python
#
# //Reaktor/IRC/asybot.py
#
from translate_colors import translate_colors
def is_executable(x):
  import os
  return os.path.exists(x) and os.access(x, os.X_OK)

from asynchat import async_chat as asychat
from asyncore import loop
from socket import AF_INET, SOCK_STREAM,gethostname
from signal import SIGALRM, signal, alarm
from datetime import datetime as date, timedelta
import shlex
from time import sleep
from sys import exit
from re import split, search, match
from textwrap import TextWrapper
import logging,logging.handlers
from getconf import make_getconf
getconf = make_getconf('config.py')
log = logging.getLogger('asybot')
hdlr = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON)
formatter = logging.Formatter( '%(filename)s: %(levelname)s: %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
logging.basicConfig(level = logging.DEBUG if getconf('debug') else logging.INFO)

# s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g -- removes color codes


class asybot(asychat):
  def __init__(self):
    asychat.__init__(self)
    self.server = getconf('irc_server')
    self.port = getconf('irc_port')
    self.channels = getconf('irc_channels')
    self.realname = getconf('irc_nickname')
    self.nickname = getconf('irc_nickname')
    self.username = getconf('irc_nickname')
    self.hostname = getconf('irc_nickname')
    self.ircname = getconf('irc_nickname')
    self.data = ''
    self.set_terminator('\r\n'.encode(encoding='UTF-8'))
    self.create_socket(AF_INET, SOCK_STREAM)
    self.connect((self.server, self.port))
    self.wrapper = TextWrapper(subsequent_indent=" ",width=400)

    log.info('=> irc://%s@%s:%s/%s' % (self.nickname, self.server, self.port, self.channels))

    # When we don't receive data for alarm_timeout seconds then issue a
    # PING every hammer_interval seconds until kill_timeout seconds have
    # passed without a message.  Any incoming message will reset alarm.
    self.alarm_timeout = getconf('irc_alarm_timeout')
    self.hammer_interval = getconf('irc_hammer_interval')
    self.kill_timeout = getconf('irc_kill_timeout')
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
    msg = (message + self.get_terminator().decode(encoding='UTF-8')).encode(encoding='UTF-8')
    log.debug('>> %s' % msg)
    asychat.push(self, msg)

  def handle_connect(self):
    self.push('NICK %s' % self.nickname)
    self.push('USER %s %s %s :%s' %
        (self.username, self.hostname, self.server, self.realname))
    self.push('JOIN %s' % ','.join(self.channels))

  def on_privmsg(self, prefix, command, params, rest):
    def PRIVMSG(text):
      for line in self.wrapper.wrap(text.decode(encoding='UTF-8')):
        msg = 'PRIVMSG %s :%s' % (','.join(params), line)
        log.info(msg)
        self.push(msg)
        sleep(1)

    def ME(text):
      PRIVMSG(('ACTION ' + text + '').encode(encoding='UTF-8'))

    for command in getconf('irc_commands'):
      y = match(command['pattern'], rest)
      if y:
        self.execute_command(command, y, PRIVMSG, ME)

  def execute_command(self, command, match, PRIVMSG, ME):
    from os.path import realpath, dirname, join
    from subprocess import Popen as popen, PIPE
    from time import time

    #TODO: allow only commands below ./commands/
    exe = join(dirname(realpath(dirname(__file__))), command['argv'][0])
    myargv = [exe] + command['argv'][1:]

    env = {}
    start = time()
    try:
      p = popen(myargv, bufsize=1, stdout=PIPE, stderr=PIPE, env=env)
    except (OSError, Exception) as error:
      ME('brain damaged')
      log.error('OSError@%s: %s' % (myargv, error))
      return
    pid = p.pid
    for line in iter(p.stdout.readline, ''.encode(encoding='UTF-8')):
      try:
        PRIVMSG(translate_colors(line))
      except Exception as error:
        log.error('no send: %s' % error)
      log.debug('%s stdout: %s' % (pid, line))
    p.wait()
    elapsed = time() - start
    code = p.returncode
    log.info('command: %s -> %s in %d seconds' % (myargv, code, elapsed))
    [log.debug('%s stderr: %s' % (pid, x)) for x in p.stderr.readlines()]

    if code != 0:
      ME('mimimi')

if __name__ == "__main__":
  asybot()
  loop()
