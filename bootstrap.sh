#!/bin/sh
set -x
[ "`id -u`" -eq "0" ] || { echo "you need to be root!"; exit 1;} || exit 1

[ -e '/usr/bin/git' ] || \
apt-get install -y git || \
yum install git || \
pacman -Sy git || \
{ echo "please install git!"; exit 1;} || exit 1

[ -e '/krebs' ] || git clone git://github.com/krebscode/painload.git /krebs \
|| { echo "cloning failed :(" ; exit 1; } || exit 1

cd /krebs || { echo "cannot change into /krebs folder:(" ; exit 1; } || exit 1

read -n1 -p "infest now? [yN]"

[[ $REPLY = [yY] ]] && make infest 
echo $REPLY
echo "have a nice day"

