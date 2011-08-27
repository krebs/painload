# jsb/console/event.py
#
#

""" a console event. """

## jsb imports

from jsb.lib.eventbase import EventBase
from jsb.lib.channelbase import ChannelBase
from jsb.lib.errors import NoInput

## basic imports

import getpass
import logging
import re

## ConsoleEvent class

class ConsoleEvent(EventBase):

    def __deepcopy__(self, a):
        """ deepcopy an console event. """
        e = ConsoleEvent()
        e.copyin(self)
        return e

    def parse(self, bot, input, console, *args, **kwargs):
        """ overload this. """
        if not input: raise NoInput()
        self.bot = bot
        self.console = console
        self.nick = getpass.getuser()
        self.auth = self.nick + '@' + bot.cfg.uuid
        self.userhost = self.auth
        self.origin = self.userhost
        self.txt = input
        self.usercmnd = input.split()[0]
        self.channel = self.userhost
        self.cbtype = self.cmnd = unicode("CONSOLE")
        self.showall = True
        self.bind(bot)
