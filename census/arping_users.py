#!/usr/bin/python
import subprocess,re,logging,sys
import json
from arping import arpingy
from multiprocessing import Pool
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("main")
DEV='eth1'
MAC_NAMES='mac_names.lst'
data = []
my_addr = False
my_names = {}
ret = {}
quiet=False

names = {}
if len(sys.argv) > 1 and sys.argv[1] == 'q':
  quiet=True
def get_own_addr():
  data = subprocess.Popen(['/sbin/ifconfig',DEV], 
      stdout=subprocess.PIPE).communicate()[0].replace('\n','')
  return re.sub(r'.*HWaddr ([0-9A-Fa-f:]*).*inet addr:([0-9.]*).*' ,
      r'\1 \2',data).split()

def load_names(mac_file):
  f = open(mac_file)
  for l in f:
    mac,name = l.split(' ',1)
    names[mac] = name.replace('\n','')
  f.close()
  return names

def print_config():
  log.info("My Addr : %s" %str(my_addr))
  log.info("MAC Names file: %s " %MAC_NAMES)
  log.debug("Loaded names : ")
  for mac,name in my_names.iteritems():
    log.debug("%s => %s" %(mac,name))

def init():
  my_addr = get_own_addr()
  my_names = load_names(MAC_NAMES)

def arping_helper(dic):
  log.debug("trying arpingy(%s)" %dic)
  return arpingy(**dic)

def main():
  init()
  print_config()

  for first in range(1,4):
    for second in range(256):
      data.append({'iprange':'10.42.'+str(first)+'.'+str(second),'iface':DEV})
  try:
    log.info("creating new Pool")
    p = Pool(35)
    ret = filter(lambda x:x , p.map(arping_helper, data))
    log.info("killing it")
    p.terminate()

  except Exception as e:
    print 'you fail '+str(e)
    sys.exit(1)
  myip,mymac = get_own_addr()
  ret.append([mymac,myip]) 

  print_json(ret)
  #print_names(ret)

def print_names(ret):
  for p in ret:
    if not quiet:
      print p[0] + " => " + p[1]
    if p[1] in names:
      print names[p[1]]+ " is online"

def print_json(ret):
  from time import time
  output = {}
  output["timestamp"] = time()
  for i in ret:
    mac = i[0]
    ip  = i[1]
    if i[0] not in output:
      output[mac] = []
    output[mac].append(ip)
  print json.dumps(output)

if __name__ == "__main__":
  log.debug("starting arping_users")
  main()
