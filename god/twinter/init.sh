#!/bin/sh
cd $(dirname $(readlink -f $0))
while sleep 120 ;do
  python init.py
done
