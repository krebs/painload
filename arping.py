#!/usr/bin/python2

import logging 
log = logging.getLogger('pingy')
import os
try:
  if (os.geteuid() != 0):
    raise Exception('no root permissions')
  from scapy.all import *

  def arpingy(iprange="10.42.1.0/24",iface='eth0'):
    log.debug("pinging"+ iprange)
    """Arping function takes IP Address or Network, returns nested mac/ip list"""
    try:
      conf.verb=0
      ans,unans=arping(iprange,iface=iface,timeout=1)

      collection = []
      for snd, rcv in ans:
        result = rcv.sprintf(r"%ARP.psrc% %Ether.src%").split()
        log.debug(result)
        collection.append(result)
      return collection   
    except Exception as e:
      print ("something went wrong while arpinging " + str(e))
    return []

  def pingy(ip="10.42.1.0/24",iface='eth0'):
    log.debug("pinging"+ ip)
    """Arping function takes IP Address or Network, returns nested mac/ip list"""
    try:
      conf.verb=0
      ans,unans=srp(Ether()/IP(dst=ip)/ICMP(),timeout=1)

      collection = []
      for snd, rcv in ans:
        result = rcv.sprintf(r"%IP.src% %Ether.src%").split()
        log.debug(result)
        collection.append(result)
      return collection
    except Exception as e:
      print ("something went wrong while arpinging " + str(e))
    return []

except Exception as e:
  log.error("Cannot Arping!" + str(e))
  def pingy(iprange):
    return True 
  def arpingy(iprange):
    return True 
