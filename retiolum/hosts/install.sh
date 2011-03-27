! /bin/sh

set -e
myname="${1:-dummy}"
netname=retiolum
myipv4="${2:-10.7.7.56}"
mynet4=10.7.7.0

# create configuration directory for $netname
mkdir -p /etc/tinc/$netname
cd /etc/tinc/$netname

# get currently known hosts
curl http://dl.dropbox.com/u/8729977/hosts.tar | tar vx ||
curl $GIV_URI_TO_HOSTS_TAR | tar vx


cat>tinc-up<<EOF
#! /bin/sh
ifconfig \$INTERFACE up $myipv4/24
route add -net $mynet4/24 dev \$INTERFACE
EOF

chmod +x tinc-up

cat>tinc.conf<<EOF
Name = $myname
ConnectTo = supernode
Device = /dev/net/tun
EOF
echo "Subnet = $myipv4" > hosts/$myname
tincd -n $netname -K

echo Writing Public Key to irc channel
cat>write_channel.py<<EOF
#!/usr/bin/python
import random, sys, time, socket

CHANNEL = '#tincspasm'
HOST='irc.freenode.net'
FILE="/etc/tinc/retiolum/hosts/$myname"
PORT=6667
NICK= "$myname"+str(random.randint(23,666))

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect((HOST,PORT))
print NICK
sock.send("NICK %s\r\n" % NICK)
sock.send("USER %s %s bla : %s\r\n" %(NICK,HOST,NICK))
sock.send("JOIN %s\r\n" % CHANNEL)
time.sleep(23)
with open(FILE,'r') as f:
        a = [ sock.send("PRIVMSG %s : %s" % ( CHANNEL,line)) for line in f]
        time.sleep(5) #because irc is so lazy
print "closing socket"
sock.close()
EOF
python write_channel.py
# add user tincd
useradd tincd
tincd --user=tincd --chroot -n $netname
