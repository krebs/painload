#!/usr/bin/python
import irc.bot
import feedparser
import _thread
import math
import re
import subprocess
from datetime import datetime
from time import sleep

class RssBot(irc.bot.SingleServerIRCBot):
    def __init__(self, rss, name, url_shortener="http://localhost", server='ire', port=6667, chan='#news', timeout=60):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], name, name)
        self.url = rss
        self.name = name
        self.server = server
        self.port = port
        self.chan = chan
        self.to = timeout
        self.oldnews = []
        self.sendqueue = []
        self.loop = True
        self.lastnew = datetime.now()

    def start(self):
        self.upd_loop = _thread.start_new_thread(self.updateloop, ())
        self.bot = _thread.start_new_thread(irc.bot.SingleServerIRCBot.start, (self,))

    def stop(self):
        self.loop = False
        self.disconnect()

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
                    shorturl = subprocess.check_output(["curl", "-sS", "-F", "uri=" + entry.link, url_shortener]).decode()
                    self.send(entry.title + " " + shorturl)
                    self.oldnews.append(entry.link)
                    self.lastnew = datetime.now()
            sleep(self.to)


    def send(self, string):
        if self.connection.connected:
            for line in string.split('\n'):
                if len(line) < 450:
                    self.connection.privmsg(self.chan, line)
                else:
                    space = 0
                    for x in range(math.ceil(len(line)/400)):
                        oldspace = space
                        space = line.find(" ", (x+1)*400, (x+1)*400+50)
                        self.connection.privmsg(self.chan, line[oldspace:space])
                        sleep(1)
                sleep(1)
        else:
            self.connection.reconnect()
            self.send(string)

    def on_welcome(self, connection, event):
        connection.join(self.chan)
