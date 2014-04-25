from os import environ,mkdir

debug = False

# CAVEAT name should not contains regex magic
name = 'bgt_titlebot'

workdir = '/tmp/state'

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

admin_file=workdir+'/'+'admin.lst'
try: 
    with open(admin_file,"x"): pass
except: pass
auth_file=workdir+'/'+'auth.lst'

def default_command(cmd):
  return {
    'capname': cmd,
    'pattern': '^(?:' + name + '|\\*):\\s*' + cmd + '\\s*(?:\\s+(?P<args>.*))?$',
    'argv': [ 'commands/' + cmd ] }
def titlebot_cmd(cmd):
  return {
    'capname': cmd,
    'pattern': '^\\.' + cmd + '\\s*(?:\\s+(?P<args>.*))?$',
    'argv': [ 'titlebot/commands/' + cmd ] }

public_commands = [
  default_command('caps'),
  default_command('hello'),
  default_command('badcommand'),
  default_command('rev'),
  default_command('uptime'),
  default_command('nocommand'),
  titlebot_cmd('list'),
  titlebot_cmd('help'),
  titlebot_cmd('up'),
  titlebot_cmd('new'),
  titlebot_cmd('undo'),
  titlebot_cmd('down'),
  # identify via direct connect
  { 'capname': 'identify',
    'pattern': '^identify' +  '\\s*(?:\\s+(?P<args>.*))?$',
    'argv' : [ 'commands/identify' ]}
]
commands = [
  default_command('reload'),
  titlebot_cmd('clear')
]

