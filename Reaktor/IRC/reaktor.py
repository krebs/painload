import os
from ircasy import asybot
from asyncore import loop
from translate_colors import translate_colors
import shlex
from re import split, search, match

config_filename = './config.py'
from getconf import make_getconf
getconf = make_getconf(config_filename)

import logging,logging.handlers
log = logging.getLogger('asybot')
hdlr = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON)
formatter = logging.Formatter( '%(filename)s: %(levelname)s: %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
logging.basicConfig(level = logging.DEBUG if getconf('debug') else logging.INFO)


class Reaktor(asybot):
  def __init__(self):
    nick = getconf('irc_nickname')
    asybot.__init__(self, getconf('irc_server'), getconf('irc_port'), getconf('irc_channels'), nick, nick, nick, nick, nick, getconf('irc_hammer_interval'), getconf('irc_alarm_timeout'), getconf('irc_kill_timeout'))

  def on_privmsg(self, prefix, command, params, rest):
    for command in getconf('commands'):
      y = match(command['pattern'], rest)
      if y:
        self.execute_command(command, y, prefix, params)
        break

  def execute_command(self, command, match, prefix, target):
    from os.path import realpath, dirname, join
    from subprocess import Popen as popen, PIPE
    from time import time

    #TODO: allow only commands below ./commands/
    exe = join(dirname(realpath(dirname(__file__))), command['argv'][0])
    myargv = [exe] + command['argv'][1:]
    if match.groupdict().get('args',None):
      myargv += shlex.split(match.groupdict()['args'])

    env = {}
    env['_from'] = prefix.split('!', 1)[0]
    env['config_filename'] = os.path.abspath(config_filename)
    start = time()
    try:
      p = popen(myargv, bufsize=1, stdout=PIPE, stderr=PIPE, env=env)
    except (OSError, Exception) as error:
      self.ME(target, 'brain damaged')
      log.error('OSError@%s: %s' % (myargv, error))
      return
    pid = p.pid
    for line in iter(p.stdout.readline, ''.encode()):
      try:
        self.PRIVMSG(target, translate_colors(line.decode()))
      except Exception as error:
        log.error('no send: %s' % error)
      log.debug('%s stdout: %s' % (pid, line))
    p.wait()
    elapsed = time() - start
    code = p.returncode
    log.info('command: %s -> %s in %d seconds' % (myargv, code, elapsed))
    [log.debug('%s stderr: %s' % (pid, x)) for x in p.stderr.readlines()]

    if code != 0:
      self.ME(target, 'mimimi')

if __name__ == "__main__":
  Reaktor()
  loop()
