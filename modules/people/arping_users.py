#!/usr/bin/python
import subprocess,re,logging,sys

from arping import arpingy
from multiprocessing import Pool
DEV='eth0'
MAC_NAMES='mac_names.lst'
data = []
ret = {}
verb = False

if len(sys.argv) > 1 and sys.argv[1] == 'v':
  verb = True
def get_own_addr():
  data = subprocess.Popen(['/sbin/ifconfig',DEV], 
      stdout=subprocess.PIPE).communicate()[0].replace('\n','')
  return re.sub(r'.*HWaddr ([0-9A-Fa-f:]*).*inet addr:([0-9.]*).*' ,
      r'\1 \2',data).split()

def load_names(MAC_NAMES):
  names = {}
  f = open(MAC_NAMES)
  for l in f:
    mac,name = l.split()
    names[mac] = name.replace('\n','')
  f.close()
  return names

def arping_helper(dic):
  return arpingy(**dic)

for first in range(4):
  for second in range(255):
    data.append({'iprange':'10.42.'+str(first)+'.'+str(second),'iface':DEV})

names = load_names(MAC_NAMES)
try:
  p = Pool(20)
  ret = filter(lambda x:x , p.map(arping_helper, data))
  myip,mymac = get_own_addr()
  ret.append([mymac,myip])
  p.terminate()
except Exception as e:
  print 'you fail '+str(e)



for p in ret:
  if verb:
    print p[0] + " => " + p[1]
  if p[1] in names:
    print names[p[1]]+ " is online"


