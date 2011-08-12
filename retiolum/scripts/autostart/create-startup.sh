#!/bin/sh

if test "${nosudo-false}" != true -a `id -u` != 0; then
  echo "we're going sudo..." >&2
  exec sudo "$0" "$@"
  exit 23 # go to hell
fi

if [ -e /etc/init.d ];then
  INIT_FOLDER=/etc/init.d 
	update-rc.d tinc defaults #TODO debian specific
else
	echo "add tinc to DAEMONS in /etc/rc.conf" #TODO archlinux specific
fi

echo "retiolum" > /etc/tinc/nets.boot
cp -a tinc $INITFOLDER
