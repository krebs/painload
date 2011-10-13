#!/usr/bin/python
import random, sys, time, socket
try:
  myname=sys.argv[1]
except:
  print "you are made of stupid"
  exit (23)

CHANNEL = '#krebsco'
HOST='irc.freenode.net'
FILE="/etc/tinc/retiolum/hosts/"+myname
PORT=6667
NICK= myname+"_"+str(random.randint(23,666))

print "Connecting..."
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect((HOST,PORT))
print NICK
sock.send("NICK %s\r\n" % NICK)
sock.send("USER %s %s bla : %s\r\n" %(NICK,HOST,NICK))
sock.send("JOIN %s\r\n" % CHANNEL)
time.sleep(23)
f = open(FILE,'r') 
a = [ sock.send("PRIVMSG %s : %s" % ( CHANNEL,line)) for line in f]
time.sleep(5) #because irc is so lazy
print "closing socket"
sock.close()
