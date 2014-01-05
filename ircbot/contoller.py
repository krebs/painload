from time import sleep
import irc.bot
import _thread
import rssbot

class NewsBot(irc.bot.SingleServerIRCBot):
    def __init__(self, name, server='ire', port=6667, chan='#news', timeout=60):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], name, name)
        self.name = name
        self.server = server
        self.port = port
        self.chan = chan
        self.to = timeout

    def start(self):
        self.bot = _thread.start_new_thread(irc.bot.SingleServerIRCBot.start, (self,))

#   def send(self, string):
#       if len(string) < 450:
#           self.connection.privmsg(self.chan, string)
#       else:
#           space = 0
#           for x in range(math.ceil(len(string)/400)):
#               oldspace = space
#               space = string.find(" ", (x+1)*400, (x+1)*400+50)
#               self.connection.privmsg(self.chan, string[oldspace:space])
#               sleep(1)


    def on_welcome(self, connection, event):
        connection.join(self.chan)

    def send(self, string):
        for line in string.split('\n'):
            self.connection.privmsg(self.chan, line)
            sleep(1)

    def on_privmsg(self, connection, event):
        args_array = event.arguments[0].split()
        if args_array[0][:-1]==self.name:
            answer = self.read_message(args_array[1:])
            self.send(answer)

    def on_pubmsg(self, connection, event):
        self.on_privmsg(connection, event)

    def read_message(self, args):
        try:
            if args[0] in [x for x in commands.__dict__.keys() if x.find('_')]:
                func = getattr(commands, args[0])
                return func(args)
            else:
                return 'command not found'
        except:
            return "mimimimi"

feedfile = 'new_feeds'

bots = {}
knews = NewsBot('knews')

#config file reading
F = open(feedfile, "r")
lines = F.readlines()
F.close()

for line in lines:
    line = line.strip('\n')
    linear = line.split('|')
    bot = rssbot.RssBot(linear[1], linear[0])
    bot.start()
    bots[linear[0]] = bot

knews.start()


class commands():
    def add(args): 
        bot = rssbot.RssBot(args[2], args[1])
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
           output_buffer += bot + '|' + bots[bot].url + '\n'

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
            output_buffer += 'lastpull: ' + bots[args[1]].lastpull.isoformat()
            return output_buffer
        else:
            return 'bot not found'
