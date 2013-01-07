#!/bin/bash

(
  echo "`date` begin all graphs" >> /tmp/build_graph
  cd $(dirname $(readlink -f $0))
  PATH=$PATH:../../../util/bin/
  export LOG_FILE=/var/log/syslog
  export TINC_LEGACY=true
  EXTERNAL_FOLDER=/var/www/euer.krebsco.de/graphs/retiolum
  INTERNAL_FOLDER=/var/www/euer/graphs/retiolum
  begin=`timer`
  export GRAPHITE_HOST="no_omo"
  (./anonytize.sh $EXTERNAL_FOLDER && echo "`date` anonytize done" >> /tmp/build_graph)&
  (./sanitize.sh $INTERNAL_FOLDER && echo "`date` sanitize done" >> /tmp/build_graph)&
#  wait
  graphitec "retiolum.graph.buildtime" "$(timer $begin)"   >> /tmp/build_graph
  echo "`date` end all graphs" >> /tmp/build_graph
)&
