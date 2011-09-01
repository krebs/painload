#!/bin/sh
HERE=$(dirname `readlink -f $0`)
TMP=/tmp
GRAPH_SETTER1=dot
GRAPH_SETTER2=circo
GRAPH_SETTER3='neato -Goverlap=prism '
GRAPH_SETTER4=sfdp
LOG_FILE=/var/log/syslog
OPENER=/bin/true

sudo pkill -USR2 tincd
sudo sed -n '/tinc.retiolum/{s/.*tinc.retiolum\[[0-9]*\]: //gp}' $LOG_FILE |\
    $HERE/parse.py > $TMP/retiolum.dot

$GRAPH_SETTER1 -Tpng -o $1/retiolum_1.png $TMP/retiolum.dot
$GRAPH_SETTER2 -Tpng -o $1/retiolum_2.png $TMP/retiolum.dot
$GRAPH_SETTER3 -Tpng -o $1/retiolum_3.png $TMP/retiolum.dot
$GRAPH_SETTER4 -Tpng -o $1/retiolum_4.png $TMP/retiolum.dot
$OPENER $HERE/retiolum_1.png &>/dev/null 
rm $TMP/retiolum.dot
