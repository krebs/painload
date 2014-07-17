from os import environ,mkdir
from os.path import abspath, expanduser
import re
debug = False

# CAVEAT name should not contains regex magic
name = 'bgt_titlebot'

workdir = '/home/titlebot/state'

try:
  mkdir(workdir)
except: pass

irc_alarm_timeout = 300
irc_hammer_interval = 10
irc_kill_timeout = 360
irc_nickname = name
irc_server = 'irc.freenode.org'
irc_port = 6667
irc_restart_timeout = 5
irc_channels = [
  '#binaergewitter'
]
admin_file=workdir+'/admin.lst'
auth_file=workdir+'/auth.lst'

config_filename = abspath(__file__)

try: 
    with open(admin_file,"x"): pass
except: pass

# me is used, so name cannot kill our patterns below
me = '\\b' + re.escape(name) + '\\b'
me_or_us = '(?:' + me + '|\\*)'

def default_command(cmd, env=None):
  if not env: env = {}
  return {
    'capname': cmd,
    'pattern': '^' + me_or_us + ':\\s*' + cmd + '\\s*(?:\\s+(?P<args>.*))?$',
    'argv': [ 'commands/' + cmd ],
    'env': env
  }
def titlebot_cmd(cmd):
  return {
    'capname': cmd,
    'pattern': '^\\.' + cmd + '\\s*(?:\\s+(?P<args>.*))?$',
    'argv': [ 'titlebot/commands/' + cmd ] }

public_commands = [
  default_command('caps', env={
    'config_filename': config_filename
  }),
  default_command('hello'),
  default_command('badcommand'),
  default_command('rev'),
  default_command('uptime'),
  default_command('nocommand'),
  titlebot_cmd('list'),
  titlebot_cmd('help'),
  titlebot_cmd('highest'),
  titlebot_cmd('top'),
  titlebot_cmd('up'),
  titlebot_cmd('new'),
  titlebot_cmd('undo'),
  titlebot_cmd('down'),
  # identify via direct connect
  { 'capname': 'identify',
    'pattern': '^identify' + '\\s*(?:\\s+(?P<args>.*))?$',
    'argv' : [ 'commands/identify' ],
    'env':{'config_filename': config_filename}}
]
commands = [
  default_command('reload'),
  titlebot_cmd('clear')
]

