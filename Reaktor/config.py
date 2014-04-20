from os import environ

debug = True

# CAVEAT name should not contains regex magic
name = 'crabmanner'

workdir = environ['HOME'] + '/state'

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
admin_file='admin.lst'
auth_file='auth.lst'
def default_command(cmd):
  return {
    'capname': cmd,
    'pattern': '^(?:' + name + '|\\*):\\s*' + cmd + '\\s*(?:\\s+(?P<args>.*))?$',
    'argv': [ 'commands/' + cmd ] }

public_commands = [
  default_command('caps'),
  default_command('hello'),
  default_command('badcommand'),
  default_command('rev'),
  default_command('uptime'),
  default_command('nocommand'),
  # command not found
  { 'pattern': '^(?:' + name + '|\\*):.*',
    'argv': [ 'commands/respond','You are made of stupid!'] },
  # "highlight"
  { 'pattern': '.*\\b' + name + '\\b.*',
    'argv': [ 'commands/say', 'I\'m famous' ] },
  # identify via direct connect
  { 'capname': 'identify',
    'pattern': 'identify' +  '\\s*(?:\\s+(?P<args>.*))?$',
    'argv' : [ 'commands/identify' ]}
]
commands = [
  default_command('reload')
]
