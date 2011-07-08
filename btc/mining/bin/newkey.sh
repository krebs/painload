#!/bin/sh

auth=$HOME/.Xauthority
cp /dev/null $auth

if [ "$1" = "-md5" ]; then
  key=`pstat -pfS | md5`
else
  key=`perl -e 'srand; printf int(rand(10000000000000))'`
  key=$key$key
fi

xauth add unix:0 . $key

xauth add ${HOST}:0 . $key
