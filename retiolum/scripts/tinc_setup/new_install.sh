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
exists() { type "$1" >/dev/null 2>/dev/null; }

if exists hostname ;then SYSHOSTN=${HOSTNAME:-$(hostname)}
elif exists uci    ;then SYSHOSTN=$(uci get system.@system[0].hostname)
elif [ -e /etc/hostname ]   ;then SYSHOSTN=$(cat /etc/hostname)
else                              SYSHOSTN="unknown"
fi

#overwrite `found` hostname
HOSTN=${HOSTN:-$SYSHOSTN}
NETNAME=${NETNAME:-retiolum}
MASK4=${MASK4:-16}
MASK6=${MASK6:-16}
RMASK=${RMASK:-255.255.0.0}
URL=${URL:-http://euer.krebsco.de/retiolum/hosts.tar.gz}
SURL=${SURL:-http://euer.krebsco.de/retiolum/supernodes.tar.gz}

IRCCHANNEL=${IRCCHANNEL:-"#krebs"}
IRCSERVER=${IRCSERVER:-"irc.freenode.net"}
IRCPORT=${IRCPORT:-6667}

OS=${OS:-0}

IP4=${IP4:-0}
IP6=${IP6:-0}

RAND4=1
RAND6=1

#convert hostmask to subnetmask only version 4
host2subnet()
{
    NEEDDOTSINSUB=$(expr 3 - $( echo $SUBNET4 | tr -C -d . | wc -c))
    case $NEEDDOTSINSUB in
        3) FULLSUBNET=$SUBNET4.0.0.0 ;;
        2) FULLSUBNET=$SUBNET4.0.0 ;;
        1) FULLSUBNET=$SUBNET4.0 ;;
        0) FULLSUBNET=$SUBNET4 ;;
        *) echo "cannot read subnet" && exit 1;;
    esac
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
            $((LCOUNTER+=1))
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
    if grep -qe 'Linux' /etc/*release 2>/dev/null || grep -qe 'Linux' /etc/issue 2>/dev/null; then
        OS='linux'
    elif exists getprop ; then
        OS='android'
    elif test -e /etc/openwrt_release; then
        OS='openwrt'
    elif uname -s | grep -qi 'darwin'; then
        OS='osx'
    else
        echo "Cannot determine your operating system, falling back to Linux"
        OS='linux'
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
if ! exists awk ; then
    echo "Please install awk"
    exit 1
fi

if ! exists curl ; then
    if ! exists wget ; then
        echo "Please install curl or wget"
        exit 1
    else
        LOADER='wget -O-'
    fi
else
    LOADER=curl
fi

if ! $(ping -c 1 -W 5 euer.krebsco.de 1>/dev/null) ;then
    echo "Cant reach euer, check if your internet is working"
    exit 1
fi

#check if everything is installed
if [ $OS = 'android' ]; then
    if ! test -e /data/data/org.poirsouille.tinc_gui/files/tincd; then
        echo "Please install tinc-gui"
        exit 1
    else
        TINCBIN=/data/data/org.poirsouille.tinc_gui/files/tincd
        DEV="/dev/tun"
        if [ $TINCDIR = 'auto' ]; then TINCDIR="/usr/local/etc/tinc" ;fi
        if [ $TEMPDIR = 'auto' ]; then TEMPDIR="/storage/sdcard0/tinc-fu" ;fi
        mount -o remount,rw /
        mount -o remount,rw /system
    fi
elif [ $OS = 'osx' ]; then
    if ! exists tincd >/dev/null; then
        echo "Please install tinc"
        exit 1
    else
        TINCBIN=tincd
        DEV="/dev/net/tun"
        if [ $TINCDIR = 'auto' ]; then TINCDIR="/usr/local/etc/tinc" ;fi
        if [ $TEMPDIR = 'auto' ]; then TEMPDIR="/tmp/tinc-install-fu" ;fi
    fi
else
    if ! exists tincd >/dev/null; then
        echo "Please install tinc"
        exit 1
    else
        TINCBIN=tincd
        DEV="/dev/net/tun"
        if [ $TINCDIR = 'auto' ]; then TINCDIR="/etc/tinc" ;fi
        if [ $TEMPDIR = 'auto' ]; then TEMPDIR="/tmp/tinc-install-fu" ;fi
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

if [ $OS = 'openwrt' ]; then
    mkdir hosts
    $LOADER $SURL | tar xz -C hosts/
else
    mv $TEMPDIR/hosts ./
fi

rm -r $TEMPDIR || echo "$TEMPDIR does not exist, skipping removal"

echo "Subnet = $IP4" > hosts/$HOSTN
echo "Subnet = $IP6" >> hosts/$HOSTN

cat>tinc.conf<<EOF
Name = $HOSTN
Device = $DEV

#newer tinc features
LocalDiscovery = yes
AutoConnect = 3

#ConnectTos
ConnectTo = slowpoke
ConnectTo = pigstarter
ConnectTo = pico
EOF

host2subnet $MASK4

#check if ip is installed
if exists ip >/dev/null; then
    echo 'dirname="`dirname "$0"`"' > tinc-up
    echo '' >> tinc-up
    echo 'conf=$dirname/tinc.conf' >> tinc-up
    echo '' >> tinc-up
    echo 'name=$(sed -n "s|^ *Name *= *\([^ ]*\) *$|\\1|p" $conf)' >> tinc-up
    echo '' >> tinc-up
    echo 'host=$dirname/hosts/$name' >> tinc-up
    echo '' >> tinc-up
    echo 'ip link set $INTERFACE up' >> tinc-up
    echo '' >> tinc-up
    echo "addr4=\$(sed -n \"s|^ *Subnet *= *\\($SUBNET4[.][^ ]*\\) *\$|\\\\1|p\" \$host)" >> tinc-up
    echo 'ip -4 addr add $addr4 dev $INTERFACE' >> tinc-up
    echo "ip -4 route add $FULLSUBNET/$MASK4 dev \$INTERFACE" >> tinc-up
    echo '' >> tinc-up
    echo "addr6=\$(sed -n \"s|^ *Subnet *= *\\($SUBNET6[:][^ ]*\\) *\$|\\\\1|p\" \$host)" >> tinc-up
    echo 'ip -6 addr add $addr6 dev $INTERFACE' >> tinc-up
    echo "ip -6 route add $SUBNET6::/$MASK6 dev \$INTERFACE" >> tinc-up
else
    echo 'dirname="`dirname "$0"`"' > tinc-up
    echo '' >> tinc-up
    echo 'conf=$dirname/tinc.conf' >> tinc-up
    echo '' >> tinc-up
    echo 'name=$(sed -n "s|^ *Name *= *\([^ ]*\) *$|\\1|p" $conf)' >> tinc-up
    echo '' >> tinc-up
    echo 'host=$dirname/hosts/$name' >> tinc-up
    echo '' >> tinc-up
    echo "addr4=\$(sed -n \"s|^ *Subnet *= *\\($SUBNET4[.][^ ]*\\) *$|\\\\1|p\" \$host)" >> tinc-up
    echo 'ifconfig $INTERFACE $addr4' >> tinc-up
    echo "route add -net $FULLSUBNET netmask $RMASK dev \$INTERFACE " >> tinc-up
fi

#fix permissions
chmod +x tinc-up
chown -R 0:0 .

#generate keys with tinc
if exists tincctl ; then
    yes | tincctl -n $NETNAME generate-keys
    cat rsa_key.pub >> hosts/$HOSTN
else
    yes | $TINCBIN -n $NETNAME -K
fi

if [ $OS = 'android' ]; then
    mkdir /etc/tinc
    cd /
    mv $TINCDIR/$NETNAME /etc/tinc/
    cd /etc/tinc/$NETNAME
fi
#write to irc-channel
NICK="${HOSTN}_$(head /dev/urandom | tr -dc "0123456789" | head -c3)"

(   echo "NICK $NICK";
    echo "USER $NICK $IRCSERVER bla : $NICK";
    echo "JOIN $IRCCHANNEL";
    sleep 23;
    sed "s/^\(.*\)/PRIVMSG $IRCCHANNEL : \1/" hosts/$HOSTN;
    sleep 5; ) | telnet $IRCSERVER $IRCPORT


# finish what you have begun!
tincd -n $NETNAME
