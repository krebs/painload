#!/usr/bin/perl
use XML::Simple;
system("w3m -dump \"http://www.google.com/ig/api?weather=70327-stuttgart&hl=de\" > weather.xml");
my $xml = new XML::Simple;
my $data = $xml->XMLin("weather.xml");
print "Die Wetterkondition ist: $data->{weather}->{current_conditions}->{condition}->{data}\n bei $data->{weather}->{current_conditions}->{temp_c}->{data} Grad Celsius\n";
