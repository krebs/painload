# Elch
This builds the elch sharing distribution.

# Usage 

    # create a new iso
    ./refresh
    # creates:
    #   out/elchos.iso 

# Requirements
Both development environment and Final Distro are based on a heavily remastered
version of the Arch Linux Install Stick. On Arch you need archiso to build the
distro.

    pacman -Sy archiso

# Configured URLs
- elchstats.nsupdate.info -> the graphite stats receiver
- elchirc.nsupdate.info   -> the irc to be used 
                               irc.freenode.net currently hardcoded 
                               in root-image/krebs/etc/Reaktor/config.py
- elchhub.nsupdate.info   -> the dcpp hub to be used
