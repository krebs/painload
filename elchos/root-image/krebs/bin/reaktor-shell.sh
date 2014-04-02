#!/bin/sh
echo "IP Addresses:"
/krebs/painload/Reaktor/commands/ips || echo "no IPs!"
/krebs/bin/add-reaktor-secret.sh
