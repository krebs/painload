#!/bin/bash
set -xe
MYIP=10.7.7.66

apt-get install -y install tinc git curl python git-core

./install.sh `hostname` $MYIP

# for autostart
echo "retiolum" >> /etc/tinc/nets.boot
echo "EXTRA=\"\"" >> /etc/default/tinc
