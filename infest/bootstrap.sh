#!/bin/sh
set -euf
# Can be overwritten before install
KREBSDIR=${KREBSDIR:-/krebs}
[ "`id -u`" -eq "0" ] || { echo "you need to be root!"; exit 1;} || exit 1


# brute force install git, krebs style
command -v git || \
    apt-get install -y git-core || \
    yum install git || \
    opkg install git || \
    ipkg install git || \
    pacman -Sy git || \
    { echo "please install git manually!"; exit 1;} || exit 1

[ -e "$KREBSDIR" ] || git clone https://github.com/krebscode/painload.git "$KREBSDIR" \
    || { echo "cloning failed :(" ; exit 1; } || exit 1

cd $KREBSDIR || { echo "cannot change into $KREBSDIR folder:(" ; exit 1; } || exit 1



PATH=$PATH:$KREBSDIR/punani/bin

# install the rest
punani install make


echo "do 'make infest' in $KREBSDIR"
echo "have a nice day"
