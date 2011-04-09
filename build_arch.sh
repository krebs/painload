#!/bin/sh
set -e
sudo pacman -S openssl gcc lzo
curl http://www.tinc-vpn.org/packages/tinc-1.0.13.tar.gz | tar xz
cd tinc-1.0.13
./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var
make
sudo make install
cd ..

echo "overwriting python to python2"
sed 's/\/usr\/bin\/python/\/usr\/bin\/python2/g' install.sh >install2.sh
mv install2.sh install.sh

