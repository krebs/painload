SNMP Users
==========

asks an snmp-router for its arp-list and tries to verify this list via
ARPING. The snmping is done via snmp-net and command line parsing,
the arping uses 'scapy'.

This script needs superuser rights and otherwise will just skip the
verification

SNMPWALK Command
===============

snmpwalk -c shammunity 10.42.0.1 1.3.6.1.2.1.3.1.1.2
