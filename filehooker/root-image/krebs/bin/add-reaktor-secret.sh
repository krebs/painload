#!/bin/sh
set -euf
green='\e[0;32m'
red='\e[0;31m'
nc='\e[0m'
black='\e[0;30m'

printf "${green}Add a Reaktor Secret${nc}\n"

printf "provide Nick Name:\n"
nick=${1:-}
test -z "${nick:-}" && read nick
printf "provide Secret:$black\n" 
secret=${2:-}
test -z "${secret:-}" && read secret
echo "$nick $secret" >> /krebs/painload/Reaktor/admin.lst
printf "${green}done${nc}"
