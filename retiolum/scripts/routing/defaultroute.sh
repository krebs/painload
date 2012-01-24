#!/bin/bash
usage()
{
    echo "usage:"
    echo "-h,      print this help youre currently reading"
    echo "-a       activate routing"
    echo "-d       deactivate routing"
}

defaultroute=$(ip route show | grep default | awk '{ print $3 }')
tincdir="/etc/tinc/retiolum"

if [[ $(id -u) -gt 0 ]]; then
    echo "This script should be run as root."
    exit 1
fi

case "$1" in
    -h|-help)
        usage
        exit 0;;
    -a)
        command="add"
        ;;
    -d)
        command="del"
        ;;
    -*|*)
        usage
        exit 1;;
esac

cat $tincdir/tinc.conf | grep ConnectTo | cut -b 13- |
while read host
do
    addr=$(cat $tincdir/hosts/$host | grep Address | cut -b 11-)
    route $command $addr gw $defaultroute && echo $command $addr via $defaultroute
done
