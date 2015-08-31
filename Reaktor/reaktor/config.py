import os
from os.path import abspath, expanduser,dirname,join
import reaktor # to get the path to the reaktor basedir
import re

debug = True

# IRC_NICKNAME is set if the nick changes and the config is getting reloaded
# TODO: do not implement functionality in the config :\
name = os.environ.get('IRC_NICKNAME','crabmanner')


#workdir = './state'
workdir = expanduser('~') + '/state'

# TODO: YAY more functionality in config.py ..
# if this fails the bot will fail (which is ok)
if not os.path.isdir(workdir): os.makedirs(workdir)




irc_alarm_timeout = 300
irc_hammer_interval = 10
irc_kill_timeout = 360
irc_nickname = name
irc_server = 'irc.freenode.org'
irc_port = 6667
irc_restart_timeout = 5
irc_channels = [
  '#krebs'
]
admin_file=workdir+'/admin.lst'
auth_file=workdir+'/auth.lst'

nag_env={
  'hosts_repo': 'https://github.com/krebscode/hosts',
  'services_repo': 'gitolite@localhost:services',
  'inspect_services': 'false'
}

config_filename = abspath(__file__)

mod_dir=dirname(abspath(reaktor.__file__))
# the commands dirname (
dist_dir = abspath(join(mod_dir))

# me is used, so name cannot kill our patterns below

# TODO: name may change after reconnect, then this pattern fails to match
# this may need a complete refactor of how to create patterns and matches
me = '\\b' + re.escape(name) + '\\b'
me_or_us = '(?:' + me + '|\\*)'

def distc(cmd):
    """ builds a path to a cmd in the distribution command folder"""
    return join(dist_dir,"commands",cmd)


# using partial formatting {{}}
indirect_pattern='^{}:\\s*{{}}\\s*(?:\\s+(?P<args>.*))?$'.format(me_or_us)
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

public_commands = [
  default_command('caps', env={
    'config_filename': config_filename
  }),
  default_command('hello'),
  default_command('badcommand'),
  default_command('rev'),
  default_command('uptime'),
  default_command('nocommand'),
  default_command('tell', cmd='tell-on_privmsg', env={
    'state_file': workdir + '/tell.txt'
  }),
  # TODO this is disabled until someone fixes it
  #default_command('nag', env=nag_env),
  simple_command('identify', env={
    'config_filename': config_filename
  }),
  # command not found
  { 'pattern': '^' + me_or_us + ':.*',
    'argv': [ distc('respond'),'You are made of stupid!'] },
  # "highlight"
  { 'pattern': '.*' + me + '.*',
    'argv': [ distc('say'), 'I\'m famous' ] },
  # identify via direct connect
]

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

on_ping = [
  {
    'capname': 'nag',
    'argv': [ distc('nag') ],
    'env': nag_env,
    'targets': irc_channels
  }
]
