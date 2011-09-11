#! /bin/sh
echo 'You are made of stupid!' >&2
exit 23

sleep 5h 19m && while :; do echo $(echo "($(od -tu -An -N 2 /dev/urandom)%1000)+500"|bc) $(echo "($(od -tu -An -N 2 /dev/urandom)%500)+100"|bc) ; done | ./a.out 1
