#!/bin/bash
set -x
if [ ! "$MYIP" ] 
then
  MYIP=10.0.7.7.55
fi
if [ ! "$MYHOSTNAME" ]
then
  MYHOSTNAME="penis"
fi

if [ "$MYHOSTNAME" = "penis" ];
then 
  read -n1 -p "name is penis, are u sure? [yN]" 
  if [[ "$REPLY" != [yY] ]] 
  then 
    echo "then better RTFC"
    echo "bailing out"  
    exit 0
  fi
fi
apt-get install tinc git curl python

./install.sh "$MYHOSTNAME" "$MYIP"

# for autostart
sed -i '/retiolum/d' /etc/tinc/nets.boot
echo "retiolum" >> /etc/tinc/nets.boot
sed -i '/EXTRA/d' /etc/tinc/nets.boot
echo "EXTRA=\"\"" >> /etc/default/tinc
