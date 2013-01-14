# Heckenkrebs
Heckenkrebs is the automatic internet-establish and gateway provider for the
krebs darknet.

This profile will automatically establish wireless connections to shared wireless networks. If you want the Krebs to connect to your wlan you need to add your wireless credentials to /etc/wifipw. Syntax is $SSID;$PW
W-Lans can be blacklisted by adding the ssid to /etc/wifiblack

run infest on the system to get into the retiolum darknet (requires internet)
hostsfiles for tinc can be updated with tinc-update

the LED will turn off after 60 seconds of working internet connection to save power

# Functionality
The Heckenkrebs will use the aap tool to connect randomly to wireless networks
which are unprotected in some ways.

aap is patched to calculate default easybox keys in addition to try open
networks. It also provides a blacklist and access-point password list.

