Census (formerly known as ARPING Users)
==========

This is a simplified python script which checks the available subnet for computers online and returns a list of users which are online based on their mac-address

The initial idea was to find known users in the given network, now it finds and stores everyone in the given network and might try to resolve these addresses into names. This is why the name `census` is coined for the project.

Return Data
----------
after trying to reach all hosts in the selected subnets the script spits out th e following data:
<pre>
    { "timestamp" : 12345678, "data" : { "ip1" : ["mac1","mac2","macn"] } 
</pre>

Census is meant to be put into a cronjob or some kind of wrapper scripts as it is currently really really (2-3 minutes) slow.

SNMPWALK Command
===============

For historic reasons, this is the snmpwalk command to pull the currently  registered mac-addresses on the firewall:
<pre>
snmpwalk -c shammunity 10.42.0.1 1.3.6.1.2.1.3.1.1.2
</pre>
