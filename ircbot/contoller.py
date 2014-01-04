import irc.bot
import _thread
import rssbot
#
#def startall():
#    for bot in botarray:
#        bot.start()

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

    def on_privmsg(self, connection, event):
        print(event.source)
        args_array = event.arguments[0].split()
        print(args_array)
        if args_array[0][:-1]==self.name:
            answer = self.read_message(args_array[1:])
            self.connection.privmsg(self.chan, answer)
        

    def on_pubmsg(self, connection, event):
        self.on_privmsg(connection, event)

    def read_message(self, args):
        print('reading message')
        try:
            if args[0] == 'add':
                bot = rssbot.RssBot(args[2], args[1])
                bots[args[1]] = bot
                bot.start()
                return "bot " + args[1] + " added"
            elif args[0] == 'del':
                bots[args[1]].die()
                del bots[args1]
                return "bot " + args[1] + " deleted"
            elif args[0] == 'save':
                output_buffer = ''
                for bot in bots:
                   output_buffer += bot + '|' + bots[bot].url + '\n'

                F = open(feedfile, "w")
                F.writelines(output_buffer)
                F.close()

                return "bots saved to " + feedfile


            else:
                return "unknown command"
        except:
            return "mimimimi"

feedfile = 'new_feeds'

bots = {}
knews = NewsBot('knews')
knews.start()

#config file reading
F = open(feedfile, "r")
lines = F.readlines()
F.close()

for line in lines:
    linear = line.split('|')
    bot = rssbot.RssBot(linear[1], linear[0])
    bot.start()
    bots[linear[0]] = bot
