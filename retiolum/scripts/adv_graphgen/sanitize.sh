#!/bin/sh
set -xeuf
cd $(dirname `readlink -f $0`)
GRAPH_SETTER1=dot
GRAPH_SETTER2=circo
GRAPH_SETTER3='neato -Goverlap=prism '
GRAPH_SETTER4=sfdp
LOG_FILE=/var/log/syslog
TYPE=svg
TYPE2=png
OPENER=/bin/true
DOTFILE=`mktemp`
trap 'rm $DOTFILE' INT TERM
sudo LOG_FILE=$LOG_FILE python tinc_stats.py |\
    python parse_tinc_stats.py > $DOTFILE


i=1
for setter in dot circo 'neato -Goverlap=prism ' sfdp
do
  tmpgraph=`mktemp --tmpdir=$1`
  $setter -T$TYPE -o $tmpgraph $DOTFILE
  chmod go+rx $tmpgraph
  mv $tmpgraph $1retiolum_$i.$TYPE
  i=`expr $i + 1`
done
#convert -resize 20% $1/retiolum_1.$TYPE  $1/retiolum_1.$TYPE2
#convert -resize 20% $1/retiolum_2.$TYPE  $1/retiolum_2.$TYPE2
#convert -resize 20% $1/retiolum_3.$TYPE  $1/retiolum_3.$TYPE2
#convert -resize 20% $1/retiolum_4.$TYPE  $1/retiolum_4.$TYPE2
