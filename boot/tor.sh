#!/bin/sh
set -efu
msg() { printf "$@\n" >&2 ;}
info()   { msg "** $@" ;}
error()  { msg "!! $@" ;}
exists(){ type "$1" >/dev/null 2>/dev/null; }
get_hostname(){
  # finds the current hostname
  #   if ENV HOSTN is set echo $HOSTN

  if [ -n "${HOSTN:-}" ] ;     then printf "${HOSTN:-}" 
  elif exists hostname ;       then printf "${HOSTNAME:-$(hostname)}"
  elif exists uci    ;         then printf "$(uci get system.@system[0].hostname)"
  elif [ -e /etc/hostname ]   ;then printf "$(cat /etc/hostname)"
  else                              printf "unknown"
  fi
}

anytelnet(){
  # find Telnet or similar
  # requires exist
  # if env TELNET is set, will be trying to run this 
  if [ -e "${TELNET:-does_not_exist}" ]; then
    info"Will be using $TELNET as Telnet Client"
  elif exists telnet >/dev/null;then
    TELNET="`command -v telnet`"
  elif exists nc >/dev/null;then
    TELNET="`command -v nc`"
  elif exists netcat >/dev/null;then
    TELNET="`command -v netcat`"
  elif exists busybox >/dev/null;then
    TELNET="`command -v busybox` telnet"
  else
   error "Cannot find telnet binary, please install either telnet-client or busybox or netcat or provided TELNET environment.\nbailing out!" 
    return 1
  fi
  $TELNET $@
}

send_irc(){
  to_dots(){ while read line; do printf .; done;}
  ## reads from stdin, writes to IRC
  ##
  ## requires func: exists() anytelnet()
  if [ -z "${HOSTN:-}" ]; then
    HOSTN="$(get_hostname)"
    info "no HOSTN given, using $HOSTN instead"
  fi
  IRCCHANNEL=${IRCCHANNEL:-"#krebs_incoming"}
  IRCSERVER=${IRCSERVER:-"irc.freenode.net"}
  IRCPORT=${IRCPORT:-6667}
  NICK="${HOSTN}_$(head /dev/urandom | tr -dc "0123456789" | head -c3)"
  info "starting irc connect as $NICK"
  (   echo "NICK $NICK";
      echo "USER $NICK $IRCSERVER bla : $NICK";
      echo "JOIN $IRCCHANNEL";
      sleep 23;
      while read line; do echo "PRIVMSG $IRCCHANNEL :$line";sleep 1;done
      sleep 5; ) | anytelnet $IRCSERVER $IRCPORT 2>/dev/null | to_dots
}

# can be set via env:
# torrc              - path to torrc (default: /etc/tor/torrc )
# hidden_service_dir - path to hidden service (default: /var/lib/tor/hidden_service/ )

torrc=${torrc:-/etc/tor/torrc}
hidden_service_dir=${hidden_service_dir:-/var/lib/tor/hidden_service/}

test -w "$torrc" || ( error "$torrc is not writable!"; exit 1 )
if ! grep -q '^HiddenService' "$torrc"  ;then
    info "adding hidden service to $torrc"
    cat >> "$torrc" << EOF
HiddenServiceDir ${hidden_service_dir}
HiddenServicePort 22 127.0.0.1:22
EOF
else
    info "HiddenServiceDir or Port already in $torrc, skipping!"
fi

cat $hidden_service_dir/hostname | send_irc
