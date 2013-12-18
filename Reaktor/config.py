
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

irc_commands = [
  { 'pattern': '^(?:asybot|\\*):\\s*caps\\s*$', 'argv': [ 'commands/caps' ] },
  { 'pattern': '^(?:asybot|\\*):\\s*hello\\s*$', 'argv': [ 'commands/hello' ] },
  { 'pattern': '^(?:asybot|\\*):\\s*reload\\s*$', 'argv': [ 'commands/reload' ] },
  { 'pattern': '^(?:asybot|\\*):\\s*badcommand\\s*$', 'argv': [ 'commands/badcommand' ] },
  { 'pattern': '^(?:asybot|\\*):\\s*rev\\s*$', 'argv': [ 'commands/rev' ] },
  { 'pattern': '^(?:asybot|\\*):\\s*uptime\\s*$', 'argv': [ 'commands/uptime' ] },
  { 'pattern': '^(?:asybot|\\*):\\s*nocommand\\s*$', 'argv': [ 'commands/nocommand' ] },
  { 'pattern': '^.*\\basybot(?:\\b[^:].*)?$', 'argv': [ 'commands/say', 'I\'m famous' ] }
]
