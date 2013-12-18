
debug = True
name = 'kwasybot'

irc_alarm_timeout = 300
irc_hammer_interval = 10
irc_kill_timeout = 360
irc_nickname = name
irc_server = 'irc.freenode.org'
irc_port = 6667
irc_channels = [
  '#krebs'
]

def default_command(cmd):
  return {
    'pattern': '^(?:' + name + '|\\*):\\s*' + cmd + '\\s*$',
    'argv': [ 'commands/' + cmd ] }

irc_commands = [
  default_command('caps'),
  default_command('hello'),
  default_command('reload'),
  default_command('badcommand'),
  default_command('rev'),
  default_command('uptime'),
  default_command('nocommand'),
  { 'pattern': '^.*\\b' + name + '(?:\\b[^:].*)?$',
    'argv': [ 'commands/say', 'I\'m famous' ] }
]
