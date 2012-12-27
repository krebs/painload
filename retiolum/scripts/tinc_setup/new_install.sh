#!/bin/sh

#get sudo
if test "${nosudo-false}" != true -a `id -u` != 0; then
  echo "we're going sudo..." >&2
  exec sudo -E "$0" "$@"
  exit 23 # go to hell
fi
set -euf
#
SUBNET4=${SUBNET4:-10.243}
SUBNET6=${SUBNET6:-42}
TEMPDIR=${TEMPDIR:-auto}
TINCDIR=${TINCDIR:-auto}
SYSHOSTN=${HOSTNAME:-$(hostname)}
HOSTN=${HOSTN:-$SYSHOSTN}
NETNAME=${NETNAME:-retiolum}
MASK4=${MASK4:-16}
MASK6=${MASK6:-16}
URL=${URL:-http://euer.krebsco.de/retiolum/hosts.tar.gz}

IRCCHANNEL=${IRCCHANNEL:-"#krebsco"}
IRCSERVER=${IRCSERVER:-"irc.freenode.net"}
IRCPORT=${IRCPORT:-6667}

OS=${OS:-0}

IP4=${IP4:-0}
IP6=${IP6:-0}

RAND4=1
RAND6=1

usage()
{
cat << EOF
usage $0 options
This script gets you into the KREBS Darknet
all parameters are optional

Options:
 -h          Show this message(haha)
 -4 \$ipv4   specify an ip(version 4), this also disables random ip mode, default is random
 -6 \$ipv6   specify an ip(version 6), this also disables random ip mode, default is random
 -s \$SUBNET Choose another Subnet(version4), default is 10.243
 -x \$SUBNET Choose another Subnet(version6), default is 42
 -m \$MASK   Choose another Subnet Mask(version4), default is 16
 -j \$MASK   Choose another Subnet Mask(version6), default is 16
 -t \$DIR    Choose another Temporary directory, default is /tmp/tinc-install-fu
 -o \$HOST   Choose another Hostname, default is your system hostname
 -n \$NET    Choose another tincd netname,this also specifies the path to your tinc config, default is retiolum
 -u \$URL    specify another hostsfiles.tar.gz url, default is http://euer.krebsco.de/retiolum/hosts.tar.gz
 -l \$OS     specify an OS, numeric parameter.0=Automatic 1=Linux 2=Android, disables automatic OS-finding, default is 0
 -r \$ADDR   give the node an reachable remote address, ipv4 or dns
EOF
}

#convert hostmask to subnetmask only version 4
host2subnet()
{
    NEEDDOTSINSUB=$(expr 3 - $( echo $SUBNET4 | tr -C -d . | wc -c))
    FULLSUBNET=$(echo $SUBNET4$(eval "printf '.0'%.0s {1..${#NEEDDOTSINSUB}}"s))
    result=$(($(($((1 << $1)) - 1)) << $((32 - $1))))
    byte=""
    for i in {0..2}; do
        byte=.$(($result % 256))$byte
        result=$(($result / 256))
    done
    RETARDEDMASK=$result$byte
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

#check if ip is valid ipv6 function
check_ip_valid6()
{
    if [ "$(echo $1 | awk -F"." ' $0 ~ /^([0-9a-fA-F]{1,4}\:){7}[0-9a-fA-F]{1,4}$/' 2>/dev/null)" == $1 ] && [ ${1:0:${#SUBNET6}} == $SUBNET6 ]
    then
        return 0
    else
        return 1
    fi
}

#check if ip is taken function
check_ip_taken()
{
    if grep -q -r -E "$1(#|/)" $TEMPDIR/hosts/ ;then
        return 1
    else
        return 0
    fi
}

#if hostname is taken, count upwards until it isn't taken function
get_hostname()
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

#os autodetection
find_os()
{
    if grep -qe 'Linux' /etc/*release 2>/dev/null || grep -qe 'Linux' /etc/issue ; then
        OS=1
    elif type getprop >/dev/null; then
        OS=2
    elif grep -qe 'OpenWrt' /etc/*release 2>/dev/null; then
        OS=3
    fi
}

if [ $IP4 -eq 0 ]; then
    RAND4=1
elif ! check_ip_valid4 $IP4; then
    echo 'ip4 is invalid'
    exit 1
fi
if [ $IP6 -eq 0 ]; then
    RAND6=1
elif ! check_ip_valid6 $IP6; then
    echo 'ip6 is invalid'
    exit 1
fi

#find OS
if [ $OS -eq 0 ]; then
    find_os
fi

#check if everything is installed
if ! type awk >/dev/null; then
    echo "Please install awk"
    exit 1
fi

if ! type curl >/dev/null; then
    if ! type wget >/dev/null; then
        echo "Please install curl or wget"
        exit 1
    else
        LOADER='wget -O-'
    fi
else
    LOADER=curl
fi

if ! $(ping -c 1 euer.krebsco.de -W 5 1>/dev/null) ;then
    echo "Cant reach euer, check if your internet is working"
    exit 1
fi


#parse options
while getopts "h4:6:s:x:m:j:t:o:n:u:l:" OPTION
do
    case $OPTION in
        h)
            usage
            exit 1
            ;;
        4)
            IP4=$OPTARG
            RAND4=0
            if ! check_ip_valid4 $IP4; then echo "ipv4 is invalid" && exit 1; fi
            ;;
        6)
            IP6=$OPTARG
            RAND6=0
            if ! check_ip_valid6 $IP6; then echo "ipv6 is invalid" && exit 1; fi
            ;;
        s)
            SUBNET4=$OPTARG
            ;;
        x)
            SUBNET6=$OPTARG
            ;;
        m)
            MASK4=$OPTARG
            ;;
        j)
            MASK6=$OPTARG
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
        u)
            URL=$OPTARG
            if $(! curl -s --head $URL | head -n 1 | grep "HTTP/1.[01] [23].." > /dev/null); then
                echo "url not reachable"
                exit 1
            fi
            ;;
        l)
            OS=$OPTARG
            if ! [ "$(echo $OS | awk -F"." ' $0 ~ /^[0-2]$/' )" == $OS ]; then
                echo "invalid input for OS"
                exit 1
            fi
            ;;
        r)
            ADDR=$OPTARG
            ;;

    esac
done

#check for OS
if [ $OS -eq 0 ]; then
    find_os
fi

#check if everything is installed
if [ $OS -eq 2 ]; then
    if ! test -e /data/data/org.poirsouille.tinc_gui/files/tincd; then
        echo "Please install tinc-gui"
        exit 1
    else
        TINCBIN=/data/data/org.poirsouille.tinc_gui/files/tincd
        if [ $TINCDIR = 'auto' ]; then TINCDIR=/usr/local/etc/tinc ;fi
        if [ $TEMPDIR = 'auto' ]; then TEMPDIR=/data/secure/data ;fi
    fi
else
    if ! type tincd >/dev/null; then
        echo "Please install tinc"
        exit 1
    else
        TINCBIN=tincd
        if [ $TINCDIR = 'auto' ]; then TINCDIR=/etc/tinc ;fi
        if [ $TEMPDIR = 'auto' ]; then TEMPDIR=/tmp/tinc-install-fu ;fi
    fi
fi

#generate full subnet information for v4

#test if tinc directory already exists
if test -e $TINCDIR/$NETNAME; then
    echo "tinc config directory $TINCDIR/$NETNAME does already exist. (backup and) delete config directory and restart"
    exit 1
fi

#get tinc-hostfiles
mkdir -p $TEMPDIR/hosts
$LOADER $URL | tar zx -C $TEMPDIR/hosts/

#check for free ip
#version 4
until check_ip_taken $IP4; do
    if [ $RAND4 -eq 1 ]; then
        IP4="$SUBNET4.$(( $(head /dev/urandom | tr -dc "123456789" | head -c3) %255)).$(( $(head /dev/urandom | tr -dc "123456789" | head -c3) %255))"
    else
        printf 'choose new ip: '
        read IP4
        while !  check_ip_valid4 $IP4; do
            printf 'the ip is invalid, retard, choose a valid ip: '
            read IP4
        done
    fi
done

#version 6
until check_ip_taken $IP6; do
    if [ $RAND6 -eq 1 ]; then
        NETLENGTH=$(expr $(expr 128 - $MASK6) / 4)
        IP6="$SUBNET6$(head /dev/urandom | tr -dc "0123456789abcdef" | head -c$NETLENGTH | sed 's/..../:&/g')" #todo: generate ip length from hostmask
    else
        printf 'ip taken, choose new ip: '

        read IP6
        while !  check_ip_valid6 $IP6; do
            printf 'the ip is invalid, retard, choose a valid ip: '
            read IP6
        done
    fi
done


#check for free hostname
get_hostname $HOSTN


#create the configs
mkdir -p $TINCDIR/$NETNAME
cd $TINCDIR/$NETNAME

if [ $OS -eq 3 ]; then
    mkdir hosts
    $LOADER http://euer.krebsco.de/retiolum/supernodes.tar.gz | tar xz -C hosts/
else
    mv $TEMPDIR/hosts ./
fi

rm -r $TEMPDIR || echo "$TEMPDIR does not exist, skipping removal"

echo "Subnet = $IP4" > hosts/$HOSTN
echo "Subnet = $IP6" >> hosts/$HOSTN

cat>tinc.conf<<EOF
Name = $HOSTN
Device = /dev/net/tun

#newer tinc features
LocalDiscovery = yes
AutoConnect = 3

#ConnectTos
ConnectTo = supernode
ConnectTo = euer
ConnectTo = pico
EOF

host2subnet $MASK4

#check if ip is installed
if type ip >/dev/null; then
    echo 'dirname="`dirname "$0"`"' > tinc-up
    echo '' >> tinc-up
    echo 'conf=$dirname/tinc.conf' >> tinc-up
    echo '' >> tinc-up
    echo 'name=$(sed -n "s|^ *Name *= *\([^ ]*\) *$|\1|p " $conf)' >> tinc-up
    echo '' >> tinc-up
    echo 'host=$dirname/hosts/$name' >> tinc-up
    echo '' >> tinc-up
    echo 'ip link set $INTERFACE up' >> tinc-up
    echo '' >> tinc-up
    echo "addr4=\$(sed -n \"s|^ *Subnet *= *\\($SUBNET4[.][^ ]*\\) *$|\\1|p\" \$host)" >> tinc-up
    echo 'ip -4 addr add $addr4 dev $INTERFACE' >> tinc-up
    echo "ip -4 route add $FULLSUBNET/$MASK4 dev \$INTERFACE" >> tinc-up
    echo '' >> tinc-up
    echo "addr6=\$(sed -n \"s|^ *Subnet *= *\\($SUBNET6[:][^ ]*\\) *$|\\1|p\" \$host)" >> tinc-up
    echo 'ip -6 addr add $addr6 dev $INTERFACE' >> tinc-up
    echo "ip -6 route add $SUBNET6::/$MASK6 dev \$INTERFACE" >> tinc-up
else
    echo 'dirname="`dirname "$0"`"' > tinc-up
    echo '' >> tinc-up
    echo 'conf=$dirname/tinc.conf' >> tinc-up
    echo '' >> tinc-up
    echo 'name=$(sed -n "s|^ *Name *= *\([^ ]*\) *$|\1|p " $conf)' >> tinc-up
    echo '' >> tinc-up
    echo 'host=$dirname/hosts/$name' >> tinc-up
    echo '' >> tinc-up
    echo "addr4=\$(sed -n \"s|^ *Subnet *= *\\($SUBNET4[.][^ ]*\\) *$|\\1|p\" \$host)" >> tinc-up
    echo 'ifconfig $INTERFACE $addr4' >> tinc-up
    echo "route add -net $FULLSUBNET netmask $RETARDEDMASK dev \$INTERFACE " >> tinc-up
fi

#fix permissions
chmod +x tinc-up
chown -R root:root .

#generate keys with tinc
if type tincctl >/dev/null; then
    yes | tincctl -n $NETNAME generate-keys
    cat rsa_key.pub >> hosts/$HOSTN
else
    yes | $TINCBIN -n $NETNAME -K
fi

#write to irc-channel
NICK="${HOSTN}_$(head /dev/urandom | tr -dc "0123456789" | head -c3)"

(   echo "NICK $NICK";
    echo "USER $NICK $IRCSERVER bla : $NICK";
    echo "JOIN $IRCCHANNEL";
    sleep 23;
    sed "s/^\(.*\)/PRIVMSG $IRCCHANNEL : \1/" hosts/$HOSTN;
    sleep 5; ) | telnet $IRCSERVER $IRCPORT

