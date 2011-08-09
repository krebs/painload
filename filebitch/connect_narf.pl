#!/usr/bin/perl
#Please add the following to your proftpd config file 
#ExtendedLog     /var/log/proftpd/ftp_auth.log AUTH auth
#and
#<IfModule mod_exec.c>
#    ExecEngine on
#    ExecOnConnect "/krebs/filebitch/connect_narf.pl"
#</IfModule>

$ip = system("tail -n 1 /var/log/proftpd/ftp_auth.log");
#I'm very sorry for this regex, but i only wanted it to get _real_ IPv4 Adresses of the log file, not any kind of timestamp bullshit
$ip =~ s/\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b//g;
#getting some guys sitting next to the Server pissed :)
system("morse -l 42 -f 2000 $ip");
system("morse -l 42 -f 3000 connected");
