#!/bin/bash
set -x
MYIP=10.0.7.7.55

apt-get install tinc git curl python

git clone https://github.com/makefu/shack-retiolum.git

cd shack-retiolum

./install.sh `hostname` $MYIP

rm shack-retiolum
# for autostart
echo "retiolum" >> /etc/tinc/nets.boot
echo "EXTRA=\"\"" >> /etc/default/tinc
