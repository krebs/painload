import socket

debug = False

name = socket.gethostname()

irc_alarm_timeout = 300
irc_hammer_interval = 10
irc_kill_timeout = 360
irc_nickname = name
irc_server = 'irc.freenode.org'
irc_port = 6667
irc_channels = [
  '#filehooker'
]

def default_command(cmd):
  return {
    'capname': cmd,
    'pattern': '^(?:' + name + '|\\*):\\s*' + cmd + '\\s*(?:\\s+(?P<args>.*))?$',
    'argv': [ 'commands/' + cmd ] }

commands = [
  default_command('caps'),
  default_command('hello'),
  default_command('reload'),
  default_command('badcommand'),
  default_command('rev'),
  default_command('uptime'),
  default_command('shares'),
  default_command('refresh_shares'),
  default_command('onion'),
  default_command('nocommand'),
  # command not found
  { 'pattern': '^(?:' + name + '|\\*):.*',
    'argv': [ 'commands/respond','You are made of stupid!'] },
  # "highlight"
  { 'pattern': '.*\\b' + name + '\\b.*',
    'argv': [ 'commands/say', 'I\'m famous' ] }
]
