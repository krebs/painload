#!/bin/sh
HOSTS_SRV=pigstarter.krebsco.de
HOSTS_PORT=5432
curl $HOSTS_SRV:$HOSTS_PORT | grep -q "Thank you for your patience"
