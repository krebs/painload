# jsb/compat/config.py
#
#

""" gozerbot config compat. """

## jsb imports

from jsb.lib.datadir import datadir
from jsb.version import getversion

## basic imports

import os
import pickle
import subprocess

# version string

ver = getversion()

## diffdict function

def diffdict(dictfrom, dictto):
    """ check for differences between two dicts """
    temp = {}
    for i in dictto.iteritems():
        if dictfrom.has_key(i[0]):
            if dictfrom[i[0]] != i[1]:
                temp.setdefault(i[0], i[1])
        else:
            temp.setdefault(i[0], i[1])
    return temp

## Config Class

class Config(dict):

    """ config object is a dict """

    def __init__(self, ddir, *args, **kw):
        dict.__init__(self, *args, **kw)
        self.dir = str(ddir)
        self['dbtype'] = 'mysql'

    def __getitem__(self, item):
        """ get config item .. return None if not available"""
        if not self.has_key(item):
            return None
        else:
            return dict.__getitem__(self, item)

    def set(self, item, value):
        """ set a config item """
        dict.__setitem__(self, item, value)
        self.save()

    def load(self):
        """ load the config file """
        frompickle = {}
        picklemodtime = None
        # first do reload of the data/config file
        self.reload()
        # see if there is a configpickle
        try:
            picklemodtime = os.stat(self.dir + os.sep + 'configpickle')[8]
            configpickle = open(self.dir + os.sep + 'configpickle', 'r')
            frompickle = pickle.load(configpickle)
            configpickle.close()
        except OSError:
            return
        except:
            pass
        # see if data/config is more recent than the configpickle
        configmodtime = os.stat(self.dir + os.sep + 'config')[8]
        if picklemodtime and picklemodtime > configmodtime:
            # if so update the config dict with the pickled data
            # a = diffdict(self, frompickle)
            self.update(frompickle)
        # set version
        if self['dbenable']:
            self['version'] = ver + ' ' + self['dbtype'].upper()
        else:
            self['version'] = ver
    
    def save(self):
        """ save config data to pickled file """
        picklefile = open(self.dir + os.sep + 'configpickle', 'w')
        pickle.dump(self, picklefile)
        picklefile.close()

    def reload(self):
        """ use execfile to reload data/config """
        try:
            execfile(self.dir + os.sep + 'config', self)
        except IOError:
            self.defaultconfig()
        # remove builtin data
        try:
            del self['__builtins__']
        except:
            pass
        # set version
        if self['dbenable']:
            self['version'] = ver + ' ' + self['dbtype'].upper()
        else:
            self['version'] = ver

    def defaultconfig(self):
        """ init default config values if no config file is found """
        self['loglevel'] = 100
        self['jabberenable'] = 0
        self['ircdisable'] = 0
        self['stripident'] = 1
        self['owneruserhost'] = ['bart@127.0.0.1', ]
        self['nick'] = 'gozerbot'
        self['server'] = 'localhost'
        self['port'] = 6667
        self['ipv6'] = 0
        self['username'] = 'gozerbot'
        self['realname'] = 'GOZERBOT'
        self['defaultcc'] = "!"
        self['nolimiter'] = 0
        self['quitmsg'] = 'http://gozerbot.org'
        self['dbenable'] = 0
        self['udp'] = 0
        self['partyudp'] = 0
        self['mainbotname'] = 'main'
        self['addonallow'] = 0
        self['allowedchars'] = []

configtxt = """# config
#
#

__copyright__ = 'this file is in the public domain'

# gozerdata dir umask
umask = 0700

# logging level .. the higher this value is the LESS the bot logs
loglevel = 10

## jabber section:

jabberenable = 0
jabberowner = 'bartholo@localhost'
jabberhost = 'localhost'
jabberuser = 'gozerbot@localhost'
jabberpass = 'pass'
jabberoutsleep = 0.1

## irc section:

ircdisable = 0

# stripident .. enable stripping of ident from userhost
stripident = 1

# userhost of owner .. make sure this matches your client's userhost
# if it doesn't match you will get an userhost denied message when you
# try to send commands to the bot
owneruserhost = ['bart@127.0.0.1', ]

# the nick the bot tries to use, only used if no nick is set
# otherwise the bot will use the last nick used by the !nick command
nick = 'gozerbot'

# alternick
#alternick = 'gozerbot2'

# server to connect to
server = 'localhost'

# irc port to connect to 
port = 6667

# ircd password for main bot
#password = 'bla'

# ipv6
ipv6 = 0

# bindhost .. uncomment and edit to use
#bindhost = 'localhost'

# bots username
username = 'gozerbot'

# realname
realname = 'GOZERBOT'

# default control character
defaultcc = "!"

# no limiter
nolimiter = 0

# quit message
quitmsg = 'http://gozerbot.org'

# nickserv .. set pass to enable nickserv ident
nickservpass = ""
nickservtxt = ['set unfiltered on', ]

## if you want to use a database:

dbenable = 0 # set to 1 to enable
dbtype = 'mysql' # one of mysql or sqlite
dbname = "gb_db"
dbhost = "localhost"
dbuser = "bart"
dbpasswd = "mekker2"
dboldstyle = False # set to True if mysql database is <= 4.1

## if you want to use udp:

# udp
udp = 0 # set to 1 to enable
partyudp = 0
udpipv6 = 0
udphost = 'localhost'
udpport = 5500
udpmasks = ['192.168*', ]
udpallow = ['127.0.0.1', ]
udpallowednicks = ['#dunkbots', 'dunker']
udppassword = 'mekker'
udpseed = "" # set this to 16 char wide string if you want to encrypt the data
udpstrip = 1 # strip all chars < char(32)
udpsleep = 0 # sleep in sendloop .. can be used to delay packet traffic

# tcp
tcp = 0 # set to 1 to enable
partytcp = 0
tcpipv6 = 0
tcphost = 'localhost'
tcpport = 5500 
tcpmasks = ['192.168*', ]
tcpallow = ['127.0.0.1', ]
tcpallowednicks = ['#dunkbots', 'dunker', 'dunker@jabber.xs4all.nl']
tcppassword = 'mekker'
tcpseed = "bla1234567890bla"
# set this to 16 char wide string if you want to encrypt the data
tcpstrip = 1
tcpsleep = 0   

## other stuff:

# plugin server 
pluginserver = 'http://gozerbot.org'

# upgradeurl .. only needed if mercurial repo changed
#upgradeurl = 'http://gozerbot.org/hg/gozerbot'

# mail related
mailserver = None
mailfrom = None

# collective boot server
collboot = "gozerbot.org:8088"

# name of the main bot
mainbotname = 'main'

# allowed character for strippedtxt
allowedchars = []

# set to 1 to allow addons
addonallow = 0

# enable loadlist
loadlist = 0
"""

def writeconfig():
    """ wtite default config file to datadir/config """
    if not os.path.isfile(datadir + os.sep + 'config'):
        cfgfile = open(datadir + os.sep + 'config', 'w')
        cfgfile.write(configtxt)
        cfgfile.close()

loadlist = """
core
misc
irc
not
grep
reverse
count
chanperm
choice
fleet
ignore
upgrade
job
reload
rest
tail
user
googletalk
all
at
backup
install
reload
tell
reverse
to
underauth
userstate
alias
nickserv
"""

def writeloadlist():
    """ write loadlist to datadir """
    if not os.path.isfile(datadir + os.sep + 'loadlist'):
        cfgfile = open(datadir + os.sep + 'loadlist', 'w')
        cfgfile.write(loadlist)
        cfgfile.close()

# create the config dict and load it from file
#config = Config(datadir)
