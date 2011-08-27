# jsb/socklib/irc/bot.py
# 
#
#

"""
    a bot object handles the dispatching of commands and check for callbacks
    that need to be fired.

"""

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.utils.generic import waitforqueue, uniqlist, strippedtxt
from jsb.lib.commands import cmnds
from jsb.lib.callbacks import callbacks
from jsb.lib.plugins import plugs as plugins
from jsb.lib.threads import start_new_thread, threaded
from jsb.utils.dol import Dol
from jsb.utils.pdod import Pdod
from jsb.lib.persiststate import PersistState
from jsb.lib.errors import NoSuchCommand
from jsb.lib.channelbase import ChannelBase
from jsb.lib.exit import globalshutdown
from jsb.lib.botbase import BotBase
from jsb.lib.partyline import partyline
from jsb.lib.wait import waiter

from channels import Channels
from irc import Irc
from ircevent import IrcEvent

## basic imports

import re
import socket
import struct
import Queue
import time
import os
import types
import logging

## defines

dccchatre = re.compile('\001DCC CHAT CHAT (\S+) (\d+)\001', re.I)

## classes

class IRCBot(Irc):

    """ class that dispatches commands and checks for callbacks to fire. """ 

    def __init__(self, cfg={}, users=None, plugs=None, *args, **kwargs):
        Irc.__init__(self, cfg, users, plugs, *args, **kwargs)
        if self.state:
            if not self.state.has_key('opchan'): self.state['opchan'] = []
        if not self.state.has_key('joinedchannels'): self.state['joinedchannels'] = []

    def _resume(self, data, botname, reto=None):
        """ resume the bot. """
        if not Irc._resume(self, data, botname, reto): return 0
        for channel in self.state['joinedchannels']: self.who(channel)
        return 1

    def _dccresume(self, sock, nick, userhost, channel=None):
        """ resume dcc loop. """
        if not nick or not userhost: return
        start_new_thread(self._dccloop, (sock, nick, userhost, channel))

    def _dcclisten(self, nick, userhost, channel):
        """ accept dcc chat requests. """
        try:
            listenip = socket.gethostbyname(socket.gethostname())
            (port, listensock) = getlistensocket(listenip)
            ipip2 = socket.inet_aton(listenip)
            ipip = struct.unpack('>L', ipip2)[0]
            chatmsg = 'DCC CHAT CHAT %s %s' % (ipip, port)
            self.ctcp(nick, chatmsg)
            self.sock = sock = listensock.accept()[0]
        except Exception, ex:
            handle_exception()
            logging.error('%s - dcc error: %s' % (self.cfg.name, str(ex)))
            return
        self._dodcc(sock, nick, userhost, channel)

    def _dodcc(self, sock, nick, userhost, channel=None):
        """ send welcome message and loop for dcc commands. """
        if not nick or not userhost: return
        try:
            sock.send('Welcome to the JSONBOT partyline ' + nick + " ;]\n")
            partylist = partyline.list_nicks()
            if partylist: sock.send("people on the partyline: %s\n" % ' .. '.join(partylist))
            sock.send("control character is ! .. bot broadcast is @\n")
        except Exception, ex:
            handle_exception()
            logging.error('%s - dcc error: %s' % (self.cfg.name, str(ex)))
            return
        start_new_thread(self._dccloop, (sock, nick, userhost, channel))

    def _dccloop(self, sock, nick, userhost, channel=None):

        """ loop for dcc commands. """

        sockfile = sock.makefile('r')
        sock.setblocking(True)
        res = ""
        partyline.add_party(self, sock, nick, userhost, channel)

        while 1:
            time.sleep(0.01)
            try:
                res = sockfile.readline()
                logging.debug("%s - dcc - %s got %s" % (self.cfg.name, userhost, res))
                if self.stopped or not res:
                    logging.warn('%s - closing dcc with %s' % (self.cfg.name, nick))
                    partyline.del_party(nick)
                    return
            except socket.timeout:
                continue
            except socket.error, ex:
                try:
                    (errno, errstr) = ex
                except:
                    errno = 0
                    errstr = str(ex)
                if errno == 35 or errno == 11:
                    continue
                else:
                    raise
            except Exception, ex:
                handle_exception()
                logging.warn('%s - closing dcc with %s' % (self.cfg.name, nick))
                partyline.del_party(nick)
                return
            try:
                res = self.normalize(res)
                ievent = IrcEvent()
                ievent.printto = sock
                ievent.bottype = "irc"
                ievent.nick = nick
                ievent.userhost = userhost
                ievent.auth = userhost
                ievent.channel = channel or ievent.userhost
                ievent.origtxt = res
                ievent.txt = res
                ievent.cmnd = 'DCC'
                ievent.cbtype = 'DCC'
                ievent.bot = self
                ievent.sock = sock
                ievent.speed = 1
                ievent.isdcc = True
                ievent.msg = True
                ievent.bind(self)
                logging.debug("%s - dcc - constructed event" % self.cfg.name)
                if ievent.txt[0] == "!":
                    self.doevent(ievent)
                    continue
                elif ievent.txt[0] == "@":
                    partyline.say_broadcast_notself(ievent.nick, "[%s] %s" % (ievent.nick, ievent.txt))
                    q = Queue.Queue()
                    ievent.queues = [q]
                    ievent.txt = ievent.txt[1:]
                    self.doevent(ievent)
                    result = waitforqueue(q, 3000)
                    if result:
                        for i in result:
                            partyline.say_broadcast("[bot] %s" % i)
                    continue
                else:
                    partyline.say_broadcast_notself(ievent.nick, "[%s] %s" % (ievent.nick, ievent.txt))
            except socket.error, ex:
                try:
                    (errno, errstr) = ex
                except:
                    errno = 0
                    errstr = str(ex)
                if errno == 35 or errno == 11:
                    continue
            except Exception, ex:
                handle_exception()
        sockfile.close()
        logging.warn('%s - closing dcc with %s' %  (self.cfg.name, nick))

    def _dccconnect(self, nick, userhost, addr, port):
        """ connect to dcc request from nick. """
        try:
            port = int(port)
            logging.warn("%s - dcc - connecting to %s:%s (%s)" % (self.cfg.name, addr, port, userhost))
            if re.search(':', addr):
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((addr, port))
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((addr, port))
        except Exception, ex:
            logging.error('%s - dcc error: %s' % (self.cfg.name, str(ex)))
            return
        self._dodcc(sock, nick, userhost, userhost)

    def broadcast(self, txt):
        """ broadcast txt to all joined channels. """
        for i in self.state['joinedchannels']: self.say(i, txt)

    def getchannelmode(self, channel):
        """ send MODE request for channel. """
        if not channel:
            return
        self.putonqueue(9, None, 'MODE %s' % channel)

    def join(self, channel, password=None):
        """ join a channel .. use optional password. """
        chan = ChannelBase(channel, self.cfg.name)
        if password:
            chan.data.key = password.strip()
            chan.save()
            #logging.warn("%s - using key %s for channel %s" % (self.cfg.name, chan.data.key, channel))
        result = Irc.join(self, channel, chan.data.key)
        if result != 1:
            return result
        got = False
        if not chan.data.cc:
            chan.data.cc = self.cfg.defaultcc or '!'
            got = True
        if not chan.data.perms:
            chan.data.perms = []
            got = True
        if not chan.data.mode:
            chan.data.mode = ""
            got = True
        if got:
            chan.save()
        self.getchannelmode(channel)
        return 1

    def handle_privmsg(self, ievent):
        """ check if PRIVMSG is command, if so dispatch. """
        if ievent.nick in self.nicks401:
            logging.debug("%s - %s is available again" % (self.cfg,name, ievent.nick))
            self.nicks401.remove(ievent.nick)
        if not ievent.txt: return
        chat = re.search(dccchatre, ievent.txt)
        if chat:
            if self.users.allowed(ievent.userhost, 'USER'):
                start_new_thread(self._dccconnect, (ievent.nick, ievent.userhost, chat.group(1), chat.group(2))) 
                return
        if '\001' in ievent.txt:
            Irc.handle_privmsg(self, ievent)
            return
        ievent.bot = self
        ievent.sock = self.sock
        chan = ievent.channel
        if chan == self.cfg.nick:
            ievent.msg = True
            ievent.speed =  4
            ievent.printto = ievent.nick
            ccs = ['!', '@', self.cfg['defaultcc']]
            if ievent.isresponse:
                return
            if self.cfg['noccinmsg'] and self.msg:
                self.put(ievent)
            elif ievent.txt[0] in ccs: 
                self.put(ievent)
            return
        self.put(ievent)

    def handle_join(self, ievent):
        """ handle joins. """
        if ievent.nick in self.nicks401:
             logging.debug("%s - %s is available again" % (self.cfg.name, ievent.nick))
             self.nicks401.remove(ievent.nick)
        chan = ievent.channel
        nick = ievent.nick
        if nick == self.cfg.nick:
            logging.warn("%s - joined %s" % (self.cfg.name, ievent.channel))
            time.sleep(0.5)
            self.who(chan)
            return
        logging.info("%s - %s joined %s" % (self.cfg.name, ievent.nick, ievent.channel))
        self.userhosts[nick] = ievent.userhost

    def handle_kick(self, ievent):
        """ handle kick event. """
        try:
            who = ievent.arguments[1]
        except IndexError:
            return
        chan = ievent.channel
        if who == self.cfg.nick:
            if chan in self.state['joinedchannels']:
                self.state['joinedchannels'].remove(chan)
                self.state.save()

    def handle_nick(self, ievent):
        """ update userhost cache on nick change. """
        nick = ievent.txt
        self.userhosts[nick] = ievent.userhost
        if ievent.nick == self.cfg.nick or ievent.nick == self.cfg.orignick:
            self.cfg['nick'] = nick
            self.cfg.save()

    def handle_part(self, ievent):
        """ handle parts. """
        chan = ievent.channel
        if ievent.nick == self.cfg.nick:
            logging.warn('%s - parted channel %s' % (self.cfg.name, chan))
            if chan in self.state['joinedchannels']:
                self.state['joinedchannels'].remove(chan)
                self.state.save()

    def handle_ievent(self, ievent):
        """ check for callbacks, call Irc method. """
        try:
            Irc.handle_ievent(self, ievent)
            if ievent.cmnd == 'JOIN' or ievent.msg:
                if ievent.nick in self.nicks401: self.nicks401.remove(ievent.nick)
            if ievent.cmnd != "PRIVMSG":
                i = IrcEvent()
                i.copyin(ievent)
                i.bot = self
                i.sock = self.sock
                ievent.nocb = True
                self.doevent(i)
        except:
            handle_exception()
 
    def handle_quit(self, ievent):
        """ check if quit is because of a split. """
        if '*.' in ievent.txt or self.cfg.server in ievent.txt: self.splitted.append(ievent.nick)
        
    def handle_mode(self, ievent):
        """ check if mode is about channel if so request channel mode. """
        logging.info("%s - mode change %s" % (self.cfg.name, str(ievent.arguments)))
        try:
            dummy = ievent.arguments[2]
        except IndexError:
            chan = ievent.channel
            self.getchannelmode(chan)
            if not ievent.chan: ievent.bind(self)
            if ievent.chan:
                ievent.chan.data.mode = ievent.arguments[1]
                ievent.chan.save()

    def handle_311(self, ievent):
        """ handle 311 response .. sync with userhosts cache. """
        target, nick, user, host, dummy = ievent.arguments
        nick = nick
        userhost = "%s@%s" % (user, host)
        logging.debug('%s - adding %s to userhosts: %s' % (self.cfg.name, nick, userhost))
        self.userhosts[nick] = userhost

    def handle_352(self, ievent):
        """ handle 352 response .. sync with userhosts cache. """
        args = ievent.arguments
        channel = args[1]  
        nick = args[5]
        user = args[2]
        host = args[3]
        userhost = "%s@%s" % (user, host)
        logging.debug('%s - adding %s to userhosts: %s' % (self.cfg.name, nick, userhost))
        self.userhosts[nick] = userhost
        
    def handle_353(self, ievent):
        """ handle 353 .. check if we are op. """
        userlist = ievent.txt.split()
        chan = ievent.channel
        for i in userlist:
            if i[0] == '@' and i[1:] == self.cfg.nick:
                if chan not in self.state['opchan']:
                    self.state['opchan'].append(chan)

    def handle_324(self, ievent):
        """ handle mode request responses. """
        if not ievent.chan: ievent.bind(self)
        ievent.chan.data.mode = ievent.arguments[2]
        ievent.chan.save()

    def handle_invite(self, ievent):
        """ join channel if invited by OPER. """
        if self.users and self.users.allowed(ievent.userhost, ['OPER', ]): self.join(ievent.txt)

    def settopic(self, channel, txt):
        """ set topic of channel to txt. """
        self.putonqueue(7, None, 'TOPIC %s :%s' % (channel, txt))

    def gettopic(self, channel, event=None):
        """ get topic data. """
        q = Queue.Queue()
        i332 = waiter.register("332", queue=q)
        i333 = waiter.register("333", queue=q)
        self.putonqueue(7, None, 'TOPIC %s' % channel)
        res = waitforqueue(q, 5000)
        who = what = when = None
        for r in res:
            if not r.postfix: continue
            try:
                if r.cmnd == "332": what = r.txt ; waiter.ready(i332) ; continue
                waiter.ready(i333)
                splitted = r.postfix.split()
                who = splitted[2]
                when = float(splitted[3])
            except (IndexError, ValueError): continue
            return (what, who, when)
