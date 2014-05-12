import socket
name = socket.gethostname()
source = "/krebs/config.sh"

# TODO: shell config file cannot contain variables or anything fancy
ret ={}
with open(cfg_file) as f:
    for line in f:
        k,v = line.split("=")
        ret[k] = v

#irc_server = 'irc.freenode.net'
irc_server = ret["IRC_SERVER"]

debug = False

state_dir='/krebs/painload/Reaktor'
irc_alarm_timeout = 300
irc_hammer_interval = 10
irc_kill_timeout = 360
irc_nickname = name
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

def elch_command(cmd):
  return {
    'capname': cmd,
    'pattern': '^(?:' + name + '|\\*):\\s*' + cmd + '\\s*(?:\\s+(?P<args>.*))?$',
    'argv': [ 'elchos/commands/' + cmd ] }

public_commands = [
  default_command('caps'),
  default_command('hello'),
  default_command('uptime'),
  default_command('badcommand'),
  default_command('rev'),
  elch_command('search'),
  elch_command('list_downloads'),
  elch_command('io'),
  elch_command('ips'),
  elch_command('shares'),
  elch_command('onion'),
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
  elch_command('update_search'),
  elch_command('refresh_shares'),
  elch_command('ftpget'),
  elch_command('reboot')
]
