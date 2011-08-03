#! /bin/sh
set -euf

tty="${TMPDIR-/tmp}/ttycnser.$LOGNAME.tty"

case "${mode-server}" in
  (server)
    host=0.0.0.0
    port=8080
    export mode=client
    echo "ttycnser @ $host $port" >&2
    exec tcpserver $host $port "$0"
  ;;
  (client)
    line="`read line && echo "$line"`"
    echo -n '7[2;1H[2K[33;1m>>>> '"$line"'8' > "$tty"
  ;;
  (install)
    # TODO tell the user to do something like
    # PROMPT_COMMAND="`mode=install ~/p/krebscode/painload/cholerab/ttycnser`"
    echo "ln -snf '`tty`' '$tty'"
  ;;
  (*)
    echo 'Error 1: You are made of stupid!' >&2
    exit 23
  ;;
esac
