#!/bin/bash
set -xe
MYIP=10.0.7.7.55

apt-get install tinc git curl gcc gcc-dev build-essential libssl-dev python

git clone https://github.com/makefu/shack-retiolum.git

mkdir build
cd build
curl http://www.oberhumer.com/opensource/lzo/download/lzo-2.04.tar.gz | tar
xz
cd lzo-2.04
./configure --prefix=/usr
make
sudo make install
cd ..
curl http://www.tinc-vpn.org/packages/tinc-1.0.13.tar.gz | tar xz
cd tinc-1.0.13
./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var
make
sudo make install
cd ../..

cd shack-retiolum
./install.sh `hostname` $MYIP

rm shack-retiolum
# for autostart
echo "retiolum" >> /etc/tinc/nets.boot
echo "EXTRA=\"--user=tincd --chroot\"" >> /etc/default/tinc
