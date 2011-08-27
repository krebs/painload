# jsb/socklib/partyline.py
#
#

""" provide partyline functionality .. manage dcc sockets. """


__copyright__ = 'this file is in the public domain'
__author__ = 'Aim'

## jsb imports

from jsb.lib.fleet import getfleet
from jsb.utils.exception import handle_exception
from jsb.lib.threads import start_new_thread
from jsb.imports import getjson
json = getjson()

## basic imports

import thread
import pickle
import socket
import logging

## classes

class PartyLine(object):

    """ partyline can be used to talk through dcc chat connections. """

    def __init__(self):
        self.socks = [] # partyline sockets list
        self.jids = []
        self.lock = thread.allocate_lock()

    def resume(self, sessionfile):
        """ resume bot from session file. """
        try:
            session = json.load(open(sessionfile, 'r'))
            self._resume(session) 
        except: handle_exception()

    def _resume(self, data, reto=None):
        """ resume a party line connection after reboot. """
        fleet = getfleet()
        for i in data['partyline']:
            logging.warn("partyline - resuming %s" % i)
            bot = fleet.byname(i['botname'])
            if not bot: logging.error("partyline - can't find bot") ; continue
            sock = socket.fromfd(i['fileno'], socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(1)
            nick = i['nick']
            userhost = i['userhost']
            channel = i['channel']
            if not bot:
                logging.error("partyline - can't find %s bot in fleet" % i['botname'])
                continue
            self.socks.append({'bot': bot, 'sock': sock, 'nick': nick, 'userhost': userhost, 'channel': channel, 'silent': i['silent']})
            bot._dccresume(sock, nick, userhost, channel)        
            if reto: self.say_nick(nick, 'rebooting done')

    def _resumedata(self):
        """ return data used for resume. """
        result = []
        for i in self.socks: result.append({'botname': i['bot'].cfg.name, 'fileno': i['sock'].fileno(), 'nick': i['nick'], 'userhost': i['userhost'], 'channel': i['channel'], 'silent': i['silent']})
        return result

    def stop(self, bot):
        """ stop all users on bot. """
        for i in self.socks:
            if i['bot'] == bot:
                try:
                    i['sock'].shutdown(2)
                    i['sock'].close()
                except: pass
                 
    def stop_all(self):
        """ stop every user on partyline. """
        for i in self.socks:
            try:
                i['sock'].shutdown(2)
                i['sock'].close()
            except:
                pass

    def loud(self, nick): 
        """ enable broadcasting of txt for nick. """
        for i in self.socks:
            if i['nick'] == nick: i['silent'] = False

    def silent(self, nick):
        """ disable broadcasting txt from/to nick. """
        for i in self.socks:
            if i['nick'] == nick: i['silent'] = True

    def add_party(self, bot, sock, nick, userhost, channel):
        ''' add a socket with nick to the list. '''
        for i in self.socks:
            if i['sock'] == sock: return            
        self.socks.append({'bot': bot, 'sock': sock, 'nick': nick, 'userhost': userhost, 'channel': channel, 'silent': False})
        logging.debug("partyline - added user %s" % nick)

    def del_party(self, nick):
        ''' remove a socket with nick from the list. '''
        nick = nick.lower()
        self.lock.acquire()
        try:
            for socknr in range(len(self.socks)-1, -1, -1):	
                if self.socks[socknr]['nick'].lower() == nick: del self.socks[socknr]
            logging.debug('partyline - removed user %s' % nick)
        finally: self.lock.release()

    def list_nicks(self):
        ''' list all connected nicks. '''
        result = []
        for item in self.socks: result.append(item['nick'])
        return result

    def say_broadcast(self, txt):
        ''' broadcast a message to all ppl on partyline. '''
        for item in self.socks:
            if not item['silent']: item['sock'].send("%s\n" % txt)

    def say_broadcast_notself(self, nick, txt):
        ''' broadcast a message to all ppl on partyline, except the sender. '''
        nick = nick.lower()
        for item in self.socks:
            if item['nick'] == nick: continue
            if not item['silent']: item['sock'].send("%s\n" % txt)

    def say_nick(self, nickto, msg):
        ''' say a message on the partyline to an user. '''
        nickto = nickto.lower()
        for item in self.socks:
            if item['nick'].lower() == nickto:
                if not '\n' in msg: msg += "\n"
                item['sock'].send("%s" % msg)
                return

    def is_on(self, nick):
        ''' checks if user an is on the partyline. '''
        nick = nick.lower()
        for item in self.socks:
            if item['nick'].lower() == nick: return True
        return False

## global partyline object

partyline = PartyLine()
