#!/usr/bin/python

import logging 
log = logging.getLogger('arpingy')
logging.disable(logging.WARNING)

import os,sys
try:
  if (os.geteuid() != 0):
    raise Exception('no root permissions')
  from scapy.all import * #might throws "no such module"

  def arpingy(iprange="10.42.1.0/24",iface='eth0'):
    log.debug("pinging "+ str(iprange))
    """Arping function takes IP Address or Network, returns nested mac/ip list"""
    try:
      conf.verb=0
      ans,unans=arping(iprange,iface=iface,timeout=0.4,retry=1)

      collection = []
      for snd, rcv in ans:
        result = rcv.sprintf(r"%ARP.psrc% %Ether.src%").split()
        log.debug(result)
        return result # take just the first arp reply
    except Exception as e:
      print ("something went wrong while arpinging " + str(e))
    return []

except Exception as e:
  raise Exception("Cannot load arping functions!" + str(e))


if __name__ =='__main__':
  logging.basicConfig(level=logging.DEBUG)
  arpingy(sys.argv[1],sys.argv[2])
