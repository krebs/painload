#!/bin/sh
set -euf
green='\e[0;32m'
red='\e[0;31m'
nc='\e[0m'
black='\e[0;30m'

printf "${green}Add a Reaktor Secret ${nc}\n"
printf "${red}(no spaces in input plox)${nc}\n"

nick=${1:-}
while test -z "${nick:-}" ;do
  printf "provide Nick Name:\n"
  read nick
done

secret=${2:-}
while test -z "${secret:-}" ;do
  printf "provide Secret:$black\n" 
  read secret
done

echo "$nick $secret" >> /krebs/painload/Reaktor/admin.lst
printf "${green}done${nc}"
