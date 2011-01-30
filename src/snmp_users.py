#!/usr/bin/python2

import logging, subprocess,re
from multiprocessing import Pool
from genericore import Configurable
from arping import arpingy
log = logging.getLogger('snmp_users')

DEFAULT_CONFIG= {
  "snmp" : {
      "server" : "127.0.0.1",
      "community" : "community",
      "tree" : "1.3.6.1.2.1.3.1.1.2"
    },
  "arping" : {
    "active" : True,
    "dev" : "eth0"
    }
}

def arping_helper(dic):
  return arpingy(**dic)

class snmp_users(Configurable):
  mac_list = {}

  def __init__(self,config={}):
    Configurable.__init__(self,DEFAULT_CONFIG)
    self.load_conf(config)

  def call_external(self):
    """returns an array of lines produced by snmpwalk """
    conf = self.config['snmp']

    out = subprocess.Popen(
        ['snmpwalk',
          '-v2c',
          '-c',conf['community'],
          conf['server'],
          conf['tree']],
        stdout=subprocess.PIPE).communicate()[0]
    return out.split('\n')

  def parse_output(self,output):
    """ parses output lines produced by snmpwalk """
    data = []
    for i in output: 
      if i == '':
        continue
      data.append(re.sub(r'.*\.(\d+\.\d+\.\d+\.\d+) = Hex-STRING: ([ 0-9A-F]*) ', r'\1 : \2',i).split(' : '))
    data = [ [ip,':'.join(mac.split()).lower()] for ip,mac in data] #sanitize

    return data

  def update_results(self,new):
    """ Verifies ip and mac via ARP Scan 
        in addition it adds the correct ip to the mac_list """ 
    macl = self.mac_list = {}
     
    for ip,mac in new: # fill the mac_list
      if not macl.get(mac,None):
        macl[mac] = []
      macl[mac].append(ip)

    return True

  def verify(self,snmp_data):
    """ verifies retrieved data where data is an array of arrays where
    [0] is the ip and [1] is the mac (space-delimited)"""
    arp_data = self.arping_parallel(snmp_data)
    print arp_data
    self.update_results(arp_data)

  def arping_parallel(self,data):
    conf = self.config['arping']
    if conf['active']:
      p = Pool(10)
      tmp = [ {'iprange':dat[0],'iface':conf['dev']} for dat in data]
      try:
        return  filter(lambda x:x , p.map(arping_helper, tmp))
      except Exception as e:
        log.warning("Something happened,falling back to original data: "+ str(e))
        return data

  def collect(self):
    output = self.call_external()
    data = self.parse_output(output)
    macs = self.verify(data)
    #self.print_results(self.mac_list)
    return self.mac_list
  def print_results(self,macs):
    log.debug('printing results:')
    print '\n'.join([ mac + " => %s" %
      str(ips) for mac,ips in macs.items() ])
    print '%d *unique* nodes in network' % len(macs)

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  a = snmp_users()
  a.collect()
  a.print_results(a.mac_list)
