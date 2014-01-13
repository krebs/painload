#!/bin/bash

(
  echo "`date` begin all graphs" >> /tmp/build_graph
  cd $(dirname $(readlink -f $0))
  PATH=$PATH:../../../util/bin/
  EXTERNAL_FOLDER=/var/www/euer.krebsco.de/graphs/retiolum
  INTERNAL_FOLDER=/var/www/euer/graphs/retiolum
  begin=`timer`
  export GEOCTIYDB="$PWD/GeoLiteCity.dat"
  (python tinc_stats/Log2JSON.py | python tinc_stats/Geo.py > $INTERNAL_FOLDER/marker.json)&
  (./anonytize.sh $EXTERNAL_FOLDER && echo "`date` anonytize done" >> /tmp/build_graph)&
  (./sanitize.sh $INTERNAL_FOLDER && echo "`date` sanitize done" >> /tmp/build_graph)&
#  wait
  echo "`date` end all graphs" >> /tmp/build_graph
)&
