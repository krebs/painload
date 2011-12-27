#!/bin/bash
usage()
{
    echo "usage:"
    echo "-h,      print this help youre currently reading"
    echo "-a       activate routing"
    echo "-d       deactivate routing"
}

defaultroute=$(route -n | grep 'UG[ \t]' | awk '{print $2}')
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


cat $tincdir/hosts/* | grep Address | cut -b 11- |
while read host
do
    if [ "$(echo $host | sed 's/[0-9]*//g' | sed 's/\.//g')" = '' ]; then
        route $command $host gw $defaultroute
    else
        host -4 $host | grep "has address" | awk '{ print $4 }' |
        while read addr
        do
            route $command $addr gw $defaultroute && echo "$command routing to $addr via $defaultroute"
        done
    fi
done
