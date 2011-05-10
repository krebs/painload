#! /bin/sh
# USE WITH GREAT CAUTION

set -e
myname="${1:-dummy}"
rel_hostsfile=`dirname $0`/hosts
hostsfile=`readlink -f $rel_hostsfile`
netname=retiolum
myipv4="${2:-10.7.7.56}"
mynet4=10.7.7.0
CURR=`pwd`
# create configuration directory for $netname
mkdir -p /etc/tinc/$netname
cd /etc/tinc/$netname

# get currently known hosts
cp -r $hostsfile .
echo "added known hosts:"
ls -1 | LC_ALL=C sort
echo "delete the nodes you do not trust!"


cat>tinc-up<<EOF
#! /bin/sh
ifconfig \$INTERFACE up $myipv4/24
route add -net $mynet4/24 dev \$INTERFACE
EOF

chmod +x tinc-up

cat>tinc.conf<<EOF
Name = $myname
ConnectTo = supernode
ConnectTo = kaah
ConnectTo = pa_sharepoint
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
NICK= "$myname_"+str(random.randint(23,666))

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
EOF
python write_channel.py
# add user tincd
useradd tincd
tincd --user=tincd --chroot -n $netname
