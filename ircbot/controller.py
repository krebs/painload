from time import sleep
import irc.bot
import _thread
import rssbot
import os
import subprocess

class NewsBot(irc.bot.SingleServerIRCBot):
    def __init__(self, name, chans=['#news'], server='ire', port=6667, timeout=60):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], name, name)
        self.name = name
        self.server = server
        self.port = port
        self.chans = chans
        self.to = timeout

    def start(self):
        self.bot = _thread.start_new_thread(irc.bot.SingleServerIRCBot.start, (self,))

    def on_welcome(self, connection, event):
        for chan in self.chans:
            connection.join(chan)

    def send(self, target, string):
        for line in string.split('\n'):
            self.connection.privmsg(target, line)
            sleep(1)

    def on_privmsg(self, connection, event):
        args_array = event.arguments[0].split()
        answer = self.read_message(args_array)
        self.send(event.source.nick, answer)

    def on_pubmsg(self, connection, event):
        args_array = event.arguments[0].split()
        if len(args_array[0]) > 0 and args_array[0][:-1]==self.name:
            answer = self.read_message(args_array[1:])
            self.send(event.target, answer)

    def on_invite(self, connection, event):
        for chan in event.arguments:
            connection.join(chan)

    def read_message(self, args):
        try:
            if args[0] in [x for x in commands.__dict__.keys() if x.find('_')]:
                func = getattr(commands, args[0])
                return func(args)
            else:
                return 'command not found'
        except:
            return "mimimimi"



class commands():
    def add(args): 
        bot = rssbot.RssBot(args[2], args[1], url_shortener=url_shortener)
        bots[args[1]] = bot
        bot.start()
        return "bot " + args[1] + " added"

    def delete(args):
        bots[args[1]].stop()
        del bots[args[1]]
        return "bot " + args[1] + " deleted"

    def rename(args):
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

    def save(args):
        output_buffer = ''
        for bot in bots:
            if bot.loop:
                output_buffer += bot + '|' + bots[bot].url + '|' + ' '.join(bots[bot].channels) + '\n'

        F = open(feedfile, "w")
        F.writelines(output_buffer)
        F.close()

        return "bots saved to " + feedfile

    def caps(args):
        return ' '.join([x for x in commands.__dict__.keys() if x.find('_')])

    def list(args):
        output_buffer = ''
        for bot in bots:
            output_buffer += bot + ' url: ' + bots[bot].url + '\n'
        return output_buffer

    def info(args):
        if args[1] in bots:
            output_buffer = ''
            for data in ['title', 'link', 'updated']:
                if data in bots[args[1]].feed.feed:
                    output_buffer += data + ': ' + bots[args[1]].feed.feed[data] + '\n'
            output_buffer += 'lastnew: ' + bots[args[1]].lastnew.isoformat()
            return output_buffer
        else:
            return 'bot not found'

    def search(args):
        output = subprocess.check_output(['./GfindFeeds4bot', args[1]]).decode()
        return output

feedfile = 'new_feeds'
url_shortener = 'http://wall'
init_channels = ['#news']

if 'FEEDFILE' in os.environ:
    feedfile = os.environ['FEEDFILE']

if 'URLSHORT' in os.environ:
    url_shortener = os.environ['URLSHORT']

bots = {}
knews = NewsBot('knews')

#config file reading
F = open(feedfile, "r")
lines = F.readlines()
F.close()

for line in lines:
    line = line.strip('\n')
    linear = line.split('|')
    bot = rssbot.RssBot(linear[1], linear[0], init_channels + linear[2].split(), url_shortener)
    bot.start()
    bots[linear[0]] = bot

knews.start()

