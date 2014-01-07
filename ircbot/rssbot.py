#!/usr/bin/python
import irc.bot
from irc.client import IRC
import feedparser
import threading
import math
import re
import subprocess
from datetime import datetime
from time import sleep

class RssBot(irc.bot.SingleServerIRCBot):
    def __init__(self, rss, name, chans=['#news'], url_shortener="http://localhost", server='ire', port=6667, timeout=60):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], name, name)
        self.url = rss
        self.name = name
        self.server = server
        self.port = port
        self.chans = chans
        self.to = timeout
        self.oldnews = []
        self.sendqueue = []
        self.loop = True
        self.lastnew = datetime.now()
        self.url_shortener = url_shortener

        def better_loop(timeout=0.2):
            while self.loop:
                self.ircobj.process_once(timeout)
        self.ircobj.process_forever = better_loop


    def start(self):
        self.upd_loop = threading.Thread(target=self.updateloop)
        self.bot = threading.Thread(target=irc.bot.SingleServerIRCBot.start, args=(self,))
        self.upd_loop.start()
        self.bot.start()

    def stop(self):
        self.ircobj.disconnect_all()
        self.loop = False

    def updateloop(self):
        try:
            self.feed = feedparser.parse(self.url)
        except:
            print(self.name + ': rss timeout occured')
        for entry in self.feed.entries:
            self.oldnews.append(entry.link)
        while self.loop:
            try:
                self.feed = feedparser.parse(self.url)
            except:
                print(self.name + ': rss timeout occured')
            for entry in self.feed.entries:
                if not entry.link in self.oldnews:
                    #try:
                    #    self.send(entry.title + " " + entry.link + " com: " + entry.comments)
                    #except AttributeError:
                    shorturl = subprocess.check_output(["curl", "-sS", "-F", "uri=" + entry.link, self.url_shortener]).decode()
                    self.send(entry.title + " " + shorturl)
                    self.oldnews.append(entry.link)
                    self.lastnew = datetime.now()
            sleep(self.to)

    def send(self, string):
        if self.connection.connected:
            for line in string.split('\n'):
                if len(line) < 450:
                    for chan in self.channels:
                        self.connection.privmsg(chan, line)
                else:
                    space = 0
                    for x in range(math.ceil(len(line)/400)):
                        oldspace = space
                        space = line.find(" ", (x+1)*400, (x+1)*400+50)
                        for chan in self.channels:
                            self.connection.privmsg(chan, line[oldspace:space])
                        sleep(1)
                sleep(1)
        else:
            self.connection.reconnect()
            sleep(1)
            self.send(string)

    def on_invite(self, connection, event):
        for chan in event.arguments:
            connection.join(chan)

    def on_welcome(self, connection, event):
        for chan in self.chans:
            connection.join(chan)
