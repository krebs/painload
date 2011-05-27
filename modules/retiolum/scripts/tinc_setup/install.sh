#! /bin/sh
# USE WITH GREAT CAUTION

make -C ../../ update

set -e


CURR=`pwd`
MYBIN=../../bin
netname=penisland
# create configuration directory for $netname
mkdir -p /etc/tinc/$netname/hosts
cd /etc/tinc/$netname

echo "added known hosts:"
ls -1 hosts | LC_ALL=C sort
echo "delete the nodes you do not trust!"

myname="${1:-}"
if [ ! "$myname" ] 
then
  echo "select username: "
  read myname
fi
if [ ! -e "hosts/$myname" ]
then
  myipv4="${2:-}"
  mynet4=10.7.7.0
  
  if [ ! "$myipv4" ] 
  then
    echo "select v4 subnet ip (1-255) :"
    read v4num
    if [  "$v4num" -gt 0 -a "$v4num" -lt "256" ];
    then 
      echo "check"
    else
      echo "you are made of stupid. bailing out" 
      exit 1
    fi
    myipv4=10.7.7.$v4num
  fi
  echo "Subnet = $myipv4" > hosts/$myname

  myipv6=`${CURR}/../../bin/fillxx 42:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx`/128
  echo "Subnet = $myipv6" >> hosts/$myname
else
  echo "own host file already exists! will not write again!"
fi


myipv6=${myipv6:-`sed -rn 's|^Subnet *= *(42:[0-9A-Fa-f:]*/128)|\1|p' /etc/tinc/$netname/hosts/$myname`}

cat>tinc-up<<EOF
#! /bin/sh
ifconfig \$INTERFACE up $myipv4/24
route add -net $mynet4/24 dev \$INTERFACE
ip -6 addr add ${myipv6} dev \$INTERFACE
ip -6 route add 42::/16 dev \$INTERFACE
EOF

chmod +x tinc-up

cat>tinc.conf<<EOF
Name = $myname
ConnectTo = supernode
ConnectTo = kaah
ConnectTo = pa_sharepoint
Device = /dev/net/tun
EOF

if [ ! -e rsa_key.priv ] 
then
  echo "creating new keys"
  tincd -n $netname -K 
  python ${CURR}/write_channel.py || \
  echo "cannot write public key to IRC, you are on your own. Good Luck"
else
  echo "key files already exist, skipping"
  echo "if you know what you are doing, remove rsa_key.priv"
fi
# add user tincd
# this is what the setup scripts for the distribution has to do
#useradd tincd
