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

#    def start(self):
#        self.bot = _thread.start_new_thread(irc.bot.SingleServerIRCBot.start, (self,))

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

    def on_privmsg(self, connection, event):
        args_array = event.arguments[0].split()
        if args_array[0][:-1]==self.name:
            answer = self.read_message(args_array[1:])
            self.send(answer)

    def send(self, string):
        for line in string.split('\n'):
            self.connection.privmsg(self.chan, line)
            sleep(0.5)

    def on_pubmsg(self, connection, event):
        self.on_privmsg(connection, event)

    def read_message(self, args):
        try:
            if args[0] == 'add':
                bot = rssbot.RssBot(args[2], args[1])
                bots[args[1]] = bot
                bot.start()
                return "bot " + args[1] + " added"

            elif args[0] == 'del':
                bots[args[1]].stop()
                del bots[args[1]]
                return "bot " + args[1] + " deleted"

            elif args[0] == 'save':
                output_buffer = ''
                for bot in bots:
                   output_buffer += bot + '|' + bots[bot].url + '\n'

                F = open(feedfile, "w")
                F.writelines(output_buffer)
                F.close()

                return "bots saved to " + feedfile
            elif args[0] == 'caps':
                return "add del save caps list"

            elif args[0] == 'list':
                output_buffer = ''
                for bot in bots:
                    output_buffer += bot + ' url: ' + bots[bot].url + '\n'
                return output_buffer

            elif args[0] == 'info':
                if args[1] in bots:
                    return 'title: ' + bots[args[1]].feed.feed.title + '\n' + 'size: ' + len(bots[args[1]].feed.entries)
                else:
                    return 'bot not found'

            else:
                return "unknown command"
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
