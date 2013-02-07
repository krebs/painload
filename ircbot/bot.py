#!/usr/bin/python
import irc.bot
import feedparser
import _thread
import math
from time import sleep

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, rss, name, server='10.243.231.66', port=6667, chan='#news', timeout=60):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], name, name)
        self.url = rss
        self.feed = feedparser.parse(self.url)
        self.name = name
        self.server = server
        self.port = port
        self.chan = chan
        self.to = timeout
        self.oldnews = []
        self.sendqueue = []
        for entry in self.feed.entries:
            self.sendqueue.append(entry.title + " " + entry.link)
            self.oldnews.append(entry.link)

    def start(self):
        self.upd_thread = _thread.start_new_thread(self.updateloop, ())
        self.bot = _thread.start_new_thread(irc.bot.SingleServerIRCBot.start, (self,))
        

    def updateloop(self):
        while True:
            sleep(self.to)
            self.feed = feedparser.parse(self.url)
            for entry in self.feed.entries:
                if not entry.link in self.oldnews:
                    self.send(entry.title + " " + entry.link)
                    self.oldnews.append(entry.link)

    def sendall(self):
        while len(self.sendqueue) > 0:
            sleep(1)
            self.send(self.sendqueue.pop())

    def send(self, string):
        if len(string) < 450:
            self.connection.privmsg(self.chan, string)
        else:
            for x in range(math.ceil(len(string)/450)):
                self.connection.privmsg(self.chan, string[x*450:(x+1)*450])
                sleep(1)


    def on_welcome(self, connection, event):
        connection.join(self.chan)

#    def on_privmsg(self, connection, event):
#        print event.source().split('!')[0], event.arguments()

F = open("feeds", "r")
lines = F.readlines()
F.close()

botarray = []
for line in lines:
    lineArray = line.split('|')
    bot = TestBot(lineArray[1], lineArray[0])
    #bot.start()
    botarray.append(bot)

def startall():
    for bot in botarray:
        bot.start()
