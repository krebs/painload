#!/bin/sh

usage()
{
cat << EOF
usage $0 options
This script gets you into the KREBS Darknet
all parameters are optional

Options:
 -h          Show this message(haha)
 -4 \$ipv4   specify an ip(version 4), this also disables random ip mode, default is random
 -t \$DIR    Choose another Temporary directory, default is /tmp/tinc-install-fu
 -o \$HOST   Choose another Hostname, default is your system hostname
 -n \$NET    Choose another tincd netname,this also specifies the path to your tinc config, default is retiolum
 -s \$SUBNET Choose another Subnet(version4), default is 10.243.
 -m \$MASK   Choose another Subnet Mask(version4), default is /16
 -u \$URL    specify another hostsfiles.tar.gz url, default is euer.krebsco.de/retiolum/hosts.tar.gz
EOF
}

#check if ip is valid ipv4 function
check_ip_valid4()
{
    if [ "$(echo $1 | awk -F"\." ' $0 ~ /^([0-9]{1,3}\.){3}[0-9]{1,3}$/ && $1 <=255 && $2 <= 255 && $3 <= 255 && $4 <= 255 ' 2>/dev/null)" == "$1" ] && [ ${1:0:${#SUBNET4}} == $SUBNET4 ]
    then
        return 0
    else
        return 1
    fi
}

#check if ip is taken function
check_ip_taken()
{
    if grep -q -E "$1(#|/)" $TEMPDIR/hosts/* ;then
        echo $1 is taken
        return 1
    else
        echo $1 seems free
        return 0
    fi
}

#if hostname is taken, count upwards until it isn't taken function
check_hostname()
{
    TSTFILE=$TEMPDIR/hosts/$1
    LCOUNTER=0
    if test -e $TSTFILE; then
        while test -e $TSTFILE; do
            let LCOUNTER=LCOUNTER+1
            TSTFILE=$TEMPDIR/hosts/$1$LCOUNTER
        done
        HOSTN=$1$LCOUNTER
    else
        HOSTN=$1
    fi
}

TEMPDIR=/tmp/tinc-install-fu
HOSTN=$(hostname)
NETNAME=retiolum
SUBNET4=10.243.
MASK4=/16
RAND=1
URL=euer.krebsco.de/retiolum/hosts.tar.gz

#check if everything is installed
if $(! test -e "/usr/sbin/tincd"); then
    echo "Please install tinc"
    exit 1
fi

if $(! test -e /usr/bin/awk); then
    echo "Please install awk"
    exit 1
fi

if $(! test -e /usr/bin/curl); then
    echo "Please install curl"
    exit 1
fi

if $(! /bin/ping -c 1 euer.krebsco.de -W 5 &>/dev/null) ;then
    echo "Cant reach euer, check if your internet is working"
    exit 1
fi


#parse options
while getopts "h4:t:o:n:s:m:u:" OPTION
do
    case $OPTION in
        h)
            usage
            exit 1
            ;;
        4)
            IP4=$OPTARG
            RAND=0
            if ! check_ip_valid4 $IP4; then echo "ip is invalid" && exit 1; fi
            ;;
        t)
            TEMPDIR=$OPTARG
            ;;
        o)
            HOSTN=$OPTARG
            ;;
        n)
            NETNAME=$OPTARG
            ;;
        s)
            SUBNET4=$OPTARG
            ;;
        m)
            MASK4=$OPTARG
            ;;
        u)
            URL=$OPTARG
            if $(! curl -s --head $URL | head -n 1 | grep "HTTP/1.[01] [23].." > /dev/null); then
                echo "url not reachable"
                exit 1
            fi
            ;;

    esac
done

#test if tinc directory already exists
if test -e /etc/tinc/$NETNAME; then
    echo "tinc config directory /etc/tinc/$NETNAME does already exist. (backup and) delete config directory and restart"
    exit 1
fi

#get tinc-hostfiles
mkdir -p $TEMPDIR/hosts
curl euer.krebsco.de/retiolum/hosts.tar.gz | tar zx -C $TEMPDIR/hosts/

#check for free ip
until check_ip_taken $IP4; do
    if [ $RAND -eq 1 ]; then
        IP4="10.243.$((RANDOM%255)).$((RANDOM%255))"
    else
        printf 'choose new ip: '
        read IP4
        while !  check_ip_valid4 $IP4; do
            printf 'the ip is invalid, retard, choose a valid ip: '
            read IP4
        done
    fi
done

#check for free hostname
check_hostname $HOSTN

echo "your ip is $IP4"
echo "your hostname is $HOSTN"
