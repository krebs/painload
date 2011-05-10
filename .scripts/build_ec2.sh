#!/bin/sh
set -e
sudo yum install -y gcc openssl-devel 
mkdir build
cd build
curl http://www.oberhumer.com/opensource/lzo/download/lzo-2.04.tar.gz | tar xz
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
