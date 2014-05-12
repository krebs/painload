#!/bin/sh
echo "IP Addresses:"
/krebs/painload/Reaktor/elchos/commands/ips || echo "no IPs!"
/krebs/bin/add-reaktor-secret.sh
