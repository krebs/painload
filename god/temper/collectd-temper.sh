HOSTNAME="${COLLECTD_HOSTNAME:-localhost}"
INTERVAL="${COLLECTD_INTERVAL:-30}"
TEMPERNAME="${TEMPERNAME:-external}"
TEMPERBIN="${TEMPERBIN:-/krebs/temper/temper}"
#while sleep "$INTERVAL"; do
  VALUE=`$TEMPERBIN`
  echo "PUTVAL \"$HOSTNAME/sensors-temper/temperature-$TEMPERNAME\" N:$VALUE" #interval=$INTERVAL
  logger "PUTVAL \"$HOSTNAME/sensors-temper/temperature-$TEMPERNAME\" N:$VALUE" #interval=$INTERVAL
#done
