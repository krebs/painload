The folder contains a number of scripts which provide a convenient way to
generate advanced graphs from the SIGUSR2 output of tinc.

it currently contains the following files:

sanitize.sh:
    wrapper arond parse.py which filters the syslog file for all tinc
    related lines and removes the status informations: 
    this means that
    <code>
    May 19 20:40:44 servarch dnsmasq[5382]: reading /etc/resolv.conf
    May 19 20:41:38 servarch tinc.retiolum[4780]: Error looking up pa-sharepoint.informatik.ba-stuttgart.de port 655: Name or service not known
    </code>
    becomes
    <code>
    Error looking up pa-sharepoint.informatik.ba-stuttgart.de port 655: Name or service not known
    </code>
    and so on.
    It also provides a wrapper around graphviz which automagically
    generates graphs from the produced graph file

parse.py:
    reads from stdin the sanitized syslog file and prints a valid dot file
    from the given output.
    The parser module may also produce any other output (e.g. for dns
    entries and so on) you will need to actually read and modify the source
    in order to be able to do this. ~May the source be with you~
    
