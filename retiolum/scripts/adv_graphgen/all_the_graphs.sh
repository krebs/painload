#!/bin/sh
echo "`date` begin all graphs" >> /tmp/build_graph
cd $(dirname $(readlink -f $0))
(./anonytize.sh /srv/http/pub/graphs/retiolum/ && echo "`date` anonytize done" >> /tmp/build_graph)&
(./sanitize.sh /srv/http/priv/graphs/retiolum/ && echo "`date` sanitize done" >> /tmp/build_graph)&
