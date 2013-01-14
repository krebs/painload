#!/usr/bin/python

def find_super(path="/etc/tinc/retiolum/hosts"):
  import os
  import re

  needle_addr = re.compile("Address\s*=\s*(.*)")
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

def check_super(path="/etc/tinc/retiolum/hosts"):
  from socket import socket,AF_INET,SOCK_STREAM
  for host,addrs in find_super(path):
    valid_addrs = []
    for addr in addrs:
      try:
        s = socket(AF_INET,SOCK_STREAM)
        s.settimeout(3)
        s.connect(addr)
        #print("success connecting %s:%d"%(addr))
        s.settimeout(None)
        s.close()
        valid_addrs.append(addr)
      except Exception as e:
        pass
        #print("cannot connect to %s:%d"%(addr))
    if valid_addrs: yield (host,valid_addrs)


if __name__ == "__main__":
  """
  usage
  """
  for host,addrs in check_super():
    print host,addrs
