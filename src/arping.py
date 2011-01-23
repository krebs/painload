#!/usr/bin/python2

import logging 
log = logging.getLogger('arpingy')
import os
try:
  if (os.geteuid() != 0):
    raise Exception('no root permissions')
  from scapy.all import * #might throws "no such module"

  def arpingy(iprange="10.42.1.0/24",iface='eth0'):
    log.debug("pinging"+ str(iprange))
    """Arping function takes IP Address or Network, returns nested mac/ip list"""
    try:
      conf.verb=0
      ans,unans=arping(iprange,iface=iface,timeout=1)

      collection = []
      for snd, rcv in ans:
        result = rcv.sprintf(r"%ARP.psrc% %Ether.src%").split()
        log.debug(result)
        return result # take just the first arp reply
    except Exception as e:
      print ("something went wrong while arpinging " + str(e))
    return []

except Exception as e:
  log.error("Cannot load arping functions!" + str(e))
  def arpingy(iprange='',iface=''):
    raise Exception ('arping not available')
