#!/usr/bin/env python3
""" usage:
        reaktor (get-config|run) [CONFIG]

    `get-config`    writes the reaktor configuration to stdout
                    if CONFIG is not given it will write the
                    reaktor default config.

                    use this for creating your own config


"""
import os
from reaktor.ircasy import asybot
from asyncore import loop
import reaktor
from reaktor.translate_colors import translate_colors
import shlex
from re import split, search, match
from os.path import dirname

default_config = dirname(reaktor.__file__)+'/config.py'
from reaktor.getconf import make_getconf

import logging,logging.handlers
log = logging.getLogger('Reaktor')

#hdlr = logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_DAEMON)
#formatter = logging.Formatter( '%(filename)s: %(levelname)s: %(message)s')
#hdlr.setFormatter(formatter)
#log.addHandler(hdlr)



class Reaktor(asybot):
  def __init__(self,config=default_config,getconf=None):
    self.config = config

    if not getconf:
        self.getconf = make_getconf(self.conf)
    else:
        self.getconf = getconf
    log.info("using config file %s"%(config))

    asybot.__init__(self,
                getconf('irc_server'),
                getconf('irc_port'),
                getconf('irc_nickname'),
                getconf('irc_channels'),
                hammer_interval=getconf('irc_hammer_interval'),
                alarm_timeout=getconf('irc_alarm_timeout'),
                kill_timeout=getconf('irc_kill_timeout'))

  def is_admin(self,prefix):
    try:
      with open(self.getconf('auth_file')) as f:
        for line in f:
          if line.strip() == prefix:
            return True
    except Exception as e:
      log.info(e)
    return False

  def on_join(self, prefix, command, params, rest):
    for command in self.getconf('on_join', []):
      self.execute_command(command, None, prefix, params)

  def on_ping(self, prefix, command, params, rest):
    for command in self.getconf('on_ping', []):
      prefix = '!' # => env = { _prefix: '!', _from: '' }
      params = command.get('targets') # TODO why don't we get a list here and use ','.join() ?
      self.execute_command(command, None, prefix, params)

  def on_privmsg(self, prefix, command, params, rest):
    if not ( self.nickname == self.getconf('name')):
        # reload config if the name changed
        # TODO: this sucks, use another sidechannel to tell config the new
        # nickname
        log.debug("nickname differs ('{}' to '{}')".format(
                    self.nickname, self.getconf('name')))

        os.environ['REAKTOR_NICKNAME'] = self.nickname
        self.getconf = make_getconf(self.config)
        log.info('nickname changed to {}'.format(self.getconf('name')))

    for command in self.getconf('commands'):
      y = match(command['pattern'], rest)
      if y:
        if not self.is_admin(prefix):
          self.PRIVMSG(params,'unauthorized!')
        else:
          return self.execute_command(command, y, prefix, params)

    for command in self.getconf('public_commands'):
      y = match(command['pattern'], rest)
      if y:
        return self.execute_command(command, y, prefix, params)


  def execute_command(self, command, match, prefix, target):
    from os.path import realpath, dirname, join
    from subprocess import Popen as popen, PIPE
    from time import time

    #TODO: allow only commands below ./commands/
    exe = join(dirname(realpath(dirname(__file__))), command['argv'][0])
    myargv = [exe] + command['argv'][1:]
    try:
      if match and match.groupdict().get('args', None):
        myargv += [match.groupdict()['args']]
    except:
        log.info("cannot parse args!")

    cwd = self.getconf('workdir')
    if not os.access(cwd,os.W_OK):
        log.error("Workdir '%s' is not Writable! Falling back to root dir"%cwd)
        cwd = "/"

    env = {}

    env.update(os.environ) # first merge os.environ
    env.update(command.get('env', {})) # then env of cfg

    env['_prefix'] = prefix
    env['_from'] = prefix.split('!', 1)[0]

    log.debug('self:' +self.nickname)
    # when receiving /query, answer to the user, not to self
    if self.nickname in target:
      target.remove(self.nickname)
      target.append(env['_from'])
    log.debug('target:' +str(target))

    start = time()
    try:
      log.debug("Running : %s"%str(myargv))
      log.debug("Environ : %s"%(str(env)))
      p = popen(myargv, bufsize=1, stdout=PIPE, stderr=PIPE, env=env, cwd=cwd)
    except Exception as error:
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

def main():
  import sys
  from docopt import docopt
  from docopt import docopt
  args = docopt(__doc__)
  conf = args['CONFIG'] if args['CONFIG'] else default_config
  getconf = make_getconf(conf)
  logging.basicConfig(level = logging.DEBUG if getconf('debug') else
          logging.INFO)
  log.debug("Debug enabled")

  if args['run']:
    Reaktor(conf,getconf)
    loop()
  elif args['get-config']:
    print(open(conf).read())

if __name__ == "__main__":
    main()

