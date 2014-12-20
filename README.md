# Autowifi
Author: makefu,lassulus

Status: Pre-Alpha - it will most likely break if you try to use it

# Contact

twitter: @krebsbob ,@makefoo 

IRC: freenode #krebs

# Goals
Goal of autowifi is to provide a tool which automatically can connect to
networks in an unknown environment.

This can either be done by connecting to open networks, known networks
(whitelist) or by calculating weak default wpa keys (for example easybox
default passwords).

# Audience
Due to the current status of the project the target audience are 
linux users with technical background .

# Usage
    
    # all as root
    # try to find networks to connect to around you
    usr/bin/autowifi_dryrun quiet

    # start the autowifi daemon which tries to stay in networks all the time
    usr/bin/autowifi

# Plugins
All tests to open up networks are implemented in plugins in
    usr/lib/autowifi/plugins

## Run a single Plugin
This can be used for testing purposes, e.g. test a single plugin against given networks directly
    
    # try out the easybox keygen
    usr/lib/autowifi/plugins/02easybox SSID MAC CHANNEL ENCRYPTION(wpa_cli style)

    #e.g.
    usr/lib/autowifi/plugins/02easybox Easybox-123456 00:11:22:33:44:55 7 "[wpa]"

# Disclaimer
- use at own risk
- only run in lab environment
- you break it, you buy it
