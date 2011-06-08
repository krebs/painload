#! /bin/sh
# TODO tolower
tr '[:upper:]' '[:lower:]' |
sed -r '
  s/\<dosen?//g
  s/mark//g
'
