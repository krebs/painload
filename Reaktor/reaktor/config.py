import os
from os.path import abspath, expanduser,dirname,join
import reaktor # to get the path to the reaktor basedir
import re
env = os.environ

# TODO: put this somewhere else
def str2bool(v):
      return v.lower() in ("yes", "true", "t", "1")

#### ENVIRON CONFIG
# this provides a simple means of reconfiguring this config without the need to
# copy-paste the whole thing
debug = str2bool(env.get('REAKTOR_DEBUG',"False"))
# IRC_NICKNAME is set if the nick changes and the config is getting reloaded
name = env.get('REAKTOR_NICKNAME','crabmanner')
irc_server = env.get('REAKTOR_HOST','irc.freenode.org')
irc_port = int(env.get('REAKTOR_PORT',6667))
# TODO: do not implement functionality in the config :\
workdir = env.get('REAKTOR_STATEDIR',expanduser('~') + '/state')
irc_channels = env.get('REAKTOR_CHANNELS','#krebs').split(',')

#### static config
# if you want to change this part you have to copy the config
irc_alarm_timeout = 300
irc_hammer_interval = 10
irc_kill_timeout = 360
irc_nickname = name
irc_restart_timeout = 5

#### IMPLEMENTATION
# this config contains the implementation of how commands should match

# TODO: YAY more functionality in config.py ..
# create the workdir somewhere # else in the code ...
# if this fails the bot will fail (which is ok)
if not os.path.isdir(workdir): os.makedirs(workdir)


admin_file=workdir+'/admin.lst'
auth_file=workdir+'/auth.lst'

config_filename = abspath(__file__)
mod_dir=dirname(abspath(reaktor.__file__))
# the commands dirname (
dist_dir = abspath(join(mod_dir))

# me is used, so name cannot kill our patterns below

# TODO: name may change after reconnect, then this pattern fails to match
# this may need a complete refactor of how to create patterns and matches

## IMPLEMENTATION

me = '\\b' + re.escape(name) + '\\b'
me_or_us = '(?:' + me + '|\\*)'
indirect_pattern='^'+me_or_us+':\\s*{}\\s*(?:\\s+(?P<args>.*))?$'

def distc(cmd):
    """ builds a path to a cmd in the command folder of the Reaktor distribution"""
    return join(dist_dir,"commands",cmd)


def default_command(cap, cmd=None, env=None):
  """ (botname|*): cmd args

  query the bot in the channel, e.g.:
    crabmanner: hello
    *: hello
  """
  if not env: env = {}
  if cmd == None: cmd=cap
  return {
    'capname': cap,
    'pattern': indirect_pattern.format(cap),
    'argv': [ distc(cmd) ],
    'env': env
  }

direct_pattern='^{}\\s*(?:\\s+(?P<args>.*))?$'
def simple_command(cap, cmd=None, env=None):
  """ cmd args

  query the bot directly, e.g.: /msg crabmanner identity dick butt
  """
  if not env: env = {}
  if cmd == None: cmd=cap
  return {
    'capname': cap,
    'pattern': direct_pattern.format(cap),
    'argv' : [ distc( cmd ) ],
    'env': env
  }

# unauthenticated commands
public_commands = [
  default_command('caps', env={
    'config_filename': config_filename
  }),
  default_command('hello'),
  default_command('badcommand'),
  #default_command('rev'), # TODO: when uploaded to pypi the rev gets lost
  default_command('version'),
  default_command('uptime'),
  default_command('nocommand'),
  default_command('tell', cmd='tell-on_privmsg', env={
    'state_file': workdir + '/tell.txt'
  }),
  simple_command('identify', env={
    'config_filename': config_filename
  }),
  # command not found
  #{ 'pattern': '^' + me_or_us + ':.*',
  #  'argv': [ distc('respond'),'You are made of stupid!'] },
  # "highlight"
  { 'pattern': '.*' + me + '.*',
    'argv': [ distc('say'), 'I\'m famous' ] },
  # identify via direct connect
]

# authenticated commands
commands = [
  default_command('reload'),
]

on_join = [
  {
    'capname': 'tell',
    'argv': [ distc('tell-on_join') ],
    'env': { 'state_file': workdir + '/tell.txt' }
  }
]

# Timer
on_ping = [
]

## END IMPLEMENTATION
