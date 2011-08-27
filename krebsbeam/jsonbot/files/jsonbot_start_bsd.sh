#!/bin/sh
# use this in your crontab and copy this script
#
# thnx to Tuxillo of #dragonflybsd EFnet fame
#
#*/2     *       *       *       *       jsb-fleet         /usr/bin/lockf -s -t0 /tmp/.bot /usr/local/bin/jsonbot_start.sh >> /dev/null 2>&;1

PATH=bin:$PATH
PIDFILE=~/.jsb/run/jsb.pid
PID=`cat $PIDFILE` 2>/dev/null

test -n "$PID" && ps auxw | grep -v grep | grep jsb-fleet | grep -q -s " $PID " && return 0
jsb-fleet
