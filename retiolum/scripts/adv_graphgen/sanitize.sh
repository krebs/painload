#!/bin/sh
HERE=$(dirname `readlink -f $0`)
GRAPH_SETTER1=dot
GRAPH_SETTER2=circo
GRAPH_SETTER3='neato -Goverlap=prism '
GRAPH_SETTER4=sfdp
LOG_FILE=/var/log/syslog
TYPE=svg
TYPE2=png
OPENER=/bin/true
DOTFILE=`mktemp`
trap 'rm $DOTFILE' SIGINT SIGTERM
sudo pkill -USR2 tincd
sudo sed -n '/tinc.retiolum/{s/.*tinc.retiolum\[[0-9]*\]: //gp}' $LOG_FILE |\
    $HERE/parse.py > $DOTFILE

$GRAPH_SETTER1 -T$TYPE -o $1/retiolum_1.$TYPE $DOTFILE
$GRAPH_SETTER2 -T$TYPE -o $1/retiolum_2.$TYPE $DOTFILE
$GRAPH_SETTER3 -T$TYPE -o $1/retiolum_3.$TYPE $DOTFILE
$GRAPH_SETTER4 -T$TYPE -o $1/retiolum_4.$TYPE $DOTFILE
#convert -resize 20% $1/retiolum_1.$TYPE  $1/retiolum_1.$TYPE2
#convert -resize 20% $1/retiolum_2.$TYPE  $1/retiolum_2.$TYPE2
#convert -resize 20% $1/retiolum_3.$TYPE  $1/retiolum_3.$TYPE2
#convert -resize 20% $1/retiolum_4.$TYPE  $1/retiolum_4.$TYPE2
#$OPENER $1/retiolum_1.$TYPE &>/dev/null 
