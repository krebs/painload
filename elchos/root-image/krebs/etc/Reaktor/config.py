import socket

debug = False

name = socket.gethostname()

irc_alarm_timeout = 300
irc_hammer_interval = 10
irc_kill_timeout = 360
irc_nickname = name
#irc_server = 'elchirc.nsupdate.info'
irc_server = 'irc.freenode.net'
irc_restart_timeout = 5
irc_port = 6667
irc_channels = [
  '#elchOS'
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
  default_command('search'),
  default_command('list_downloads'),
  default_command('badcommand'),
  default_command('rev'),
  default_command('io'),
  default_command('ips'),
  default_command('uptime'),
  default_command('shares'),
  default_command('onion'),
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
  default_command('reload'),
  default_command('update-search'),
  default_command('refresh_shares'),
  default_command('ftpget'),
  default_command('reboot')
]
