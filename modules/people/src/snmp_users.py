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

  def __init__(self,MODULE_NAME,config=None):
    self.NAME=MODULE_NAME
    newConf = { MODULE_NAME : DEFAULT_CONFIG }
    Configurable.__init__(self,newConf)
    self.load_conf(config)

  def call_external(self):
    """returns an array of lines produced by snmpwalk """
    conf = self.config[self.NAME]['snmp']

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
    self.update_results(arp_data)

  def get_own_addr(self):
    data = subprocess.Popen(['/sbin/ifconfig',self.config[self.NAME]['arping']['dev']],
        stdout=subprocess.PIPE).communicate()[0].replace('\n','')
    return re.sub(r'.*HWaddr ([0-9:A-F]*).*inet addr:([0-9.]*).*' ,r'\1 \2',data).split()


  def arping_parallel(self,data):
    conf = self.config[self.NAME]['arping']
    if conf['active']:
      tmp = [ {'iprange':dat[0],'iface':conf['dev']} for dat in data]
      try:
        p = Pool(10)
        ret = filter(lambda x:x , p.map(arping_helper, tmp))

        myip,mymac = self.get_own_addr() #append self to list
        ret.append([mymac,myip ] )
        p.terminate()
        return ret
      except Exception as e:
        log.warning("Something happened,falling back to original data: "+ str(e))
        return data

  def collect(self):
    output = self.call_external()
    data = self.parse_output(output)
    if not data:
      raise Exception('External tool had not returned any parsable output')
    log.debug('Got following output from snmpwalk program: ' +str(data))
    macs = self.verify(data)
    #self.print_results(self.mac_list)
    return self.mac_list

  def print_results(self,macs):
    log.debug('printing results:')
    print '\n'.join([ mac + " => %s" %
      str(ips) for mac,ips in macs.items() ])
    print '%d *unique* nodes in network' % len(macs)

  def populate_parser(self,parser):
    parser.add_argument('--repeat',type=int,dest='repeat',default=30,help='Seconds between Scans',metavar='SECS') #TODO add this to configuration

  def eval_parser(self,parsed):
    self.repeat = parsed.repeat

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  a = snmp_users()
  print a.get_own_addr()
  a.collect()
  a.print_results(a.mac_list)
