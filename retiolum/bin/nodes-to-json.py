#!/usr/bin/python

def parse_hosts_path(path="/etc/tinc/retiolum/hosts"):
  import os
  import re

  needle_addr = re.compile("Subnet\s*=\s*(.*)/[0-9]+")
  needle_port = re.compile("Port\s*=\s*(.*)")
  for f in os.listdir(path):
    with open(path+"/"+f) as of:
      addrs = []
      port = "655"

      for line in of.readlines():

        addr_found = needle_addr.match(line)
        if addr_found:
          addrs.append(addr_found.group(1))

        port_found = needle_port.match(line)
        if port_found:
          port = port_found.group(1)
      
      if addrs : yield (f ,[(addr ,int(port)) for addr in addrs])



if __name__ == "__main__":
  """
  usage
  """
  import json
  import sys
  db={}
  for host,addrs in parse_hosts_path(sys.argv[1] if len(sys.argv) > 2 else "/etc/tinc/retiolum/hosts"):
    db[host] = addrs
  print(json.dumps(db))
