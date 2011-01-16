#!/usr/bin/python2
import subprocess,re
import logging
from arping import arpingy,pingy
log = logging.getLogger('snmp_users')

class snmp_users:
  mac_list = {}

  def __init__(self,server='10.42.0.1',community='shammunity'):
    self.server = server
    self.community = community

  def call_external(self):
    """ creates a list of lines produced by snmpwal
    """
    out = subprocess.Popen(
        ['snmpwalk',
          '-v2c',
          '-c',self.community,
          self.server,
          '1.3.6.1.2.1.3.1.1.2'],
        stdout=subprocess.PIPE).communicate()[0]
    return out.split('\n')

  def parse_output(self,output):
    """ parses output lines produced by snmpwalk"""
    for i in output:
      if i == '':
        continue

      ip,mac = re.sub(r'.*\.(\d+\.\d+\.\d+\.\d+) = Hex-STRING: ([ 0-9A-F]*) ',
          r'\1 : \2',i).split(' : ')

      verified = False
      if self.verify_data(mac,ip,arpingy(ip)):
        log.info("verfied by arping %s => %s" % (mac,ip))
        verified = True
      
      #elif self.verify_data(mac,ip,pingy(ip) ): builds up onto arp'ing...
      #  log.info("verfied by fallback ping %s => %s" % (mac,ip))
      #  verfied = True

      if verified:
        if mac in self.mac_list.keys():
          log.info( "%s already assigned for ip %s (new IP %s) " %
              ( mac ,self.mac_list[mac], ip))
          self.mac_list[mac]['counter'] +=1
          continue
        else:
          log.debug("%s => %s" % (mac,ip))
          self.mac_list[mac] = { 'ip' : ip, 'counter' : 1}
      else:
        log.warning("Verification failed %s => %s" % (mac,ip))

  def verify_data(self,mac,ip,ret):
    """ Verifies ip and mac via ARP Scan """ 
    mac = ':'.join(mac.split())
    log.debug(ret)

    if type(ret) == type(True):
      return True
    elif ret != []:
      ret = ret[0]
      ret_mac = ret[1].upper()
      if ret_mac == mac:
        return True
      else:
        log.info('return mac not equal to expected, %s != %s' % (ret_mac,mac))
    else:
      return False

  def collect(self):
    output = self.call_external()
    self.parse_output(output)
    self.print_results()
  def print_results(self):
    print '\n'.join([ mac + " => " + ip['ip'] + " ( %d active leases )" %
      ip['counter'] for mac,ip in self.mac_list.items() ])
    print '%d *unique* nodes in network' % len(self.mac_list)


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  a = snmp_users()
  a.collect()

