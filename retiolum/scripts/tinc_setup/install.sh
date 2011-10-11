#! /bin/sh
# USE WITH GREAT CAUTION
set -eu

if test "${nosudo-false}" != true -a `id -u` != 0; then
  echo "we're going sudo..." >&2
  exec sudo "$0" "$@"
  exit 23 # go to hell
fi

#make -C ../../ update
set -e
DIRNAME=`dirname $0`
CURR=`readlink -f ${DIRNAME}`
MYBIN=${CURR}/../../bin
netname=retiolum
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
    if ! $MYBIN/check-free-retiolum-v4 $v4num;then
      exit 1
    fi
    myipv4="10.7.7.$v4num"
  fi
  echo "Subnet = $myipv4" > hosts/$myname

  myipv6=`$MYBIN/fillxx 42:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx`/128
  echo "Subnet = $myipv6" >> hosts/$myname
else
  echo "own host file already exists! will not write again!"
fi

cp $CURR/tinc-up /etc/tinc/$netname/

cat>tinc.conf<<EOF
Name = $myname
ConnectTo = supernode
ConnectTo = kaah
ConnectTo = pa_sharepoint
ConnectTo = EUcancER
Device = /dev/net/tun
EOF

if [ ! -e rsa_key.priv ] 
then
  echo "creating new keys"
  tincd -n $netname -K 
  python ${CURR}/write_channel.py $myname || \
  echo "cannot write public key to IRC, you are on your own. Good Luck"
else
  echo "key files already exist, skipping"
  echo "if you know what you are doing, remove rsa_key.priv"
fi
# add user tincd
# this is what the setup scripts for the distribution has to do
#useradd tincd
