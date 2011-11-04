#!/usr/bin/python
from BackwardsReader import BackwardsReader
import os
import re
import sys
import json


TINC_NETWORK = os.environ.get("TINC_NETWORK","retiolum")
SYSLOG_FILE = "/var/log/everything.log"


# Tags and Delimiters
TINC_TAG="tinc.%s" % TINC_NETWORK
BEGIN_NODES = "Nodes:"
END_NODES = "End of nodes."
BEGIN_SUBNET = "Subnet list:"
END_SUBNET = "End of subnet list"
BEGIN_EDGES = "Edges:"
END_EDGES = "End of edges."

def get_tinc_block(log_file):
  """ returns an iterateable block from the given log file (syslog) """
  tinc_block = []
  in_block = False
  bf = BackwardsReader(log_file)
  BOL = re.compile(".*tinc.retiolum\[[0-9]+\]: ")
  while True:
    line = bf.readline()
    if not line:
      raise Exception("end of file at log file? This should not happen!")
    line = BOL.sub('',line).strip()

    if END_SUBNET in line:
      in_block = True

    if not in_block:
      continue

    tinc_block.append(line)

    if BEGIN_NODES in line:
      break
  return reversed(tinc_block)

def parse_input(log_data):
  nodes={}
  for line in log_data:
    if BEGIN_NODES in line :
      nodes={}
      for line in log_data:
        if END_NODES in line :
          break
        l = line.replace('\n','').split() #TODO unhack me
        nodes[l[0]]= { 'external-ip': l[2], 'external-port' : l[4] }
    if BEGIN_SUBNET in line :
      for line in log_data:
        if END_SUBNET in line :
          break
        l = line.replace('\n','').split() 
        if not nodes[l[2]].get('internal-ip',False):
           nodes[l[2]]['internal-ip'] = []
        nodes[l[2]]['internal-ip'].append(l[0].split('#')[0])
    if BEGIN_EDGES in line :
      edges = {}
      for line in log_data:
        if END_EDGES in line :
          break
        l = line.replace('\n','').split() 

        if not nodes[l[0]].has_key('to') :
          nodes[l[0]]['to'] = []
        nodes[l[0]]['to'].append(
            {'name':l[2],'addr':l[4],'port':l[6],'weight' : l[10] })
  return nodes


if __name__ == '__main__':
  print json.dumps(parse_input((get_tinc_block(SYSLOG_FILE))))
