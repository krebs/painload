from ircasy import asybot
import threading
from asyncore import loop
import logging
import os
import subprocess

import feedparser
import math
import re
import subprocess
from datetime import datetime
from time import sleep
#testbot = NewsBot('ire', 6667, 'crabman23', ['#retiolum'], loglevel=logging.DEBUG)



## Newsbot Controller Class
class NewsBot(asybot):
    def __init__(self, name, channels=['#test'], server='ire', port=6667, timeout=60, loglevel=logging.ERROR, url_shortener='http://wall'):
        asybot.__init__(self, server, port, name, channels, loglevel=loglevel)
        self.to = timeout
        self.url_shortener = url_shortener
        self.ctrl_chan = channels[0]

    def send_msg(self, target, msg):
        for line in msg.split('\n'):
            self.PRIVMSG(target, line)

    def on_privmsg(self, prefix, command, params, rest):
        args_array = rest.split()
        if params[0] == self.nickname:
            answer = self.read_message(args_array)
            self.send_msg(prefix.split('!')[0], answer)
        elif args_array[0].strip(':') == self.nickname:
            answer = self.read_message(args_array[1:])
            self.send_msg([params[0]], answer)

    def on_invite(self, prefix, command, params, rest):
        for chan in rest.split():
            self.push('JOIN ' + chan)

    def read_message(self, args):
        try:
            if args[0] in [x for x in commands.__dict__.keys() if x.find('_')]:
                func = getattr(commands, args[0])
                return func(self, args)
            else:
                return 'command not found'
        except Exception as e:
            return 'mimimi: ' + str(e)

#Commands of NewsBot
class commands():
    def add(self, args): 
        if args[1] not in bots and args[1] != self.nickname:
            try:
                bot = RssBot(args[2], args[1], [self.ctrl_chan], url_shortener=self.url_shortener)
            except Exception as e:
                return 'add_mimi: ' + str(e)
                sleep
            bots[args[1]] = bot
            bot.start_rss()
            return "bot " + args[1] + " added"
        else:
            return args[1] + ' does already exist'

    def delete(self, args):
        bots[args[1]].stop()
        del bots[args[1]]
        return "bot " + args[1] + " deleted"

    def rename(self, args):
        if args[1] in bots:
            if args[2] in bots:
                return args[2] + ' already taken'
            else:
                bots[args[1]].connection.nick(args[2])
                bots[args[1]].name = args[2]
                bots[args[2]] = bots[args[1]]
                del bots[args[1]]
                return 'renamed ' + args[1] + ' in ' + args[2]
        else:
            return args[1] + ' does not exist'

    def save(self, args):
        output_buffer = ''
        for bot in bots:
            if bots[bot].loop:
                output_buffer += bot + '|' + bots[bot].url + '|' + ' '.join(bots[bot].channels) + '\n'

        F = open(feedfile, "w")
        F.writelines(output_buffer)
        F.close()

        return "bots saved to " + feedfile

    def caps(self, args):
        return ' '.join([x for x in commands.__dict__.keys() if x.find('_')])

    def list(self, args):
        output_buffer = ''
        for bot in bots:
            output_buffer += bot + ' url: ' + bots[bot].url + '\n'
        return output_buffer

    def info(self, args):
        if args[1] in bots:
            output_buffer = ''
            for data in ['title', 'link', 'updated']:
                if data in bots[args[1]].feed.feed:
                    output_buffer += data + ': ' + bots[args[1]].feed.feed[data] + '\n'
            output_buffer += 'lastnew: ' + bots[args[1]].lastnew.isoformat() + '\n'
            output_buffer += 'rssurl: ' + bots[args[1]].url
            return output_buffer
        else:
            return 'bot not found'

    def search(self, args):
        output = subprocess.check_output(['./GfindFeeds4bot', args[1]]).decode()
        return output

    def uptime(self, args):
        output = subprocess.check_output(['uptime']).decode()
        return output


##RssBot Class
class RssBot(asybot):
    def __init__(self, rss, name, chans=['#news'], url_shortener="http://localhost", server='ire', port=6667, timeout=60):
        try:
            asybot.__init__(self, server, port, name, chans)
        except Exception as e:
            print(e)
        self.url = rss
        self.to = timeout
        self.oldnews = []
        self.loop = True
        self.lastnew = datetime.now()
        self.url_shortener = url_shortener

    def start_rss(self):
        self.upd_loop = threading.Thread(target=self.updateloop)
        self.upd_loop.start()

    def stop(self):
        self.disconnect()
        self.loop = False

    def updateloop(self):
        failcount=0
        while True:
          try:
              self.feed = feedparser.parse(self.url)
              for entry in self.feed.entries:
                  self.oldnews.append(entry.link)
              break
          except:
              print(self.nickname + ': rss timeout occured')
              failcount+=1
              if failcount>20:
                  print(self.nickname + ' is broken, going to die')
                  self.stop()
                  return
        while self.loop:
            try:
                self.feed = feedparser.parse(self.url)
                for entry in self.feed.entries:
                    if not entry.link in self.oldnews:
                        #try:
                        #    self.send_msg(entry.title + " " + entry.link + " com: " + entry.comments)
                        #except AttributeError:
                        shorturl = self.shortenurl(entry.link)
                        self.sendall(entry.title + ' ' + shorturl)
                        self.oldnews.append(entry.link)
                        self.lastnew = datetime.now()
            except:
                print(self.nickname + ': rss timeout occured')
            sleep(self.to)

    def shortenurl(self, url):
      while True:
          try:
              shorturl = subprocess.check_output(["curl", "-sS", "-F", "uri=" + url, self.url_shortener]).decode().strip('\n').strip('\r') + '#' + url.partition('://')[2].partition('/')[0]
              return shorturl
          except:
              print('url shortener error')
              sleep(1)

    def last(self, target, num):
        for feed in [x for x in self.feed.entries][:num]:
            self.send_msg(target, feed.title + ' ' + self.shortenurl(feed.link))

    def sendall(self, string):
        self.send_msg(self.channels, string)

    def send_msg(self, target, string):
        if self.connected:
            for line in string.split('\n'):
                if len(line) < 450:
                    self.PRIVMSG(target, line)
                else:
                    space = 0
                    for x in range(math.ceil(len(line)/400)):
                        oldspace = space
                        space = line.find(" ", (x+1)*400, (x+1)*400+50)
                        self.PRIVMSG(target, line[oldspace:space])
        else:
            self.reconnect()
            while not self.connected:
               sleep(3)
               print('waiting for reconnect')
            self.send_msg(string)

    def on_invite(self, prefix, command, params, rest):
        for chan in rest.split():
            self.push('JOIN ' + chan)

feedfile = 'new_feeds'
url_shortener = 'http://wall'
init_channels = ['#news']

bots = {}
knews = NewsBot('knews', init_channels)

#config file reading
F = open(feedfile, "r")
lines = F.readlines()
F.close()

for line in lines:
    line = line.strip('\n')
    linear = line.split('|')
    bot = RssBot(linear[1], linear[0], init_channels + linear[2].split(), url_shortener=url_shortener)
    bot.start_rss()
    bots[linear[0]] = bot

th = threading.Thread(target=loop)
th.start()
