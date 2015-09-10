#!/usr/bin/python
# TODO: Rewrite this shitty piece of software ...
# -*- coding: utf8 -*-

import sys,json,os
""" TODO: Refactoring needed to pull the edges out of the node structures again,
it should be easier to handle both structures"""
DUMP_FILE = os.environ.get("AVAILABILITY_FILE","tinc-availability.json")
hostpath=os.environ.get("TINC_HOSTPATH", "/etc/tinc/retiolum/hosts")

def get_all_nodes():
  return os.listdir(hostpath)

def generate_stats():
  """ Generates availability statistics of the network and nodes
  """
  import json
  jlines = []
  try:
    f = open(DUMP_FILE,'r+')
    for line in f:
      jlines.append(json.loads(line))
    f.close()
  except Exception as e:
    print("Unable to open and parse Availability DB: {} (override with AVAILABILITY_FILE)".format(DUMP_FILE))
    sys.exit(1)

  all_nodes = {}
  for k in get_all_nodes():
    all_nodes[k] = get_node_availability(k,jlines)
  print (json.dumps(all_nodes))

def get_node_availability(name,jlines):
  """ calculates the node availability by reading the generated dump file
  adding together the uptime of the node and returning the time
	parms:
          name - node name
          jlines - list of already parsed dictionaries node archive
  """
  begin = last = current = 0
  uptime = 0
  for stat in jlines:
    if not stat['nodes']:
      continue
    ts = stat['timestamp']
    if not begin:
      begin = last = ts
    current = ts
    if stat['nodes'].get(name,{}).get('to',[]):
      uptime += current - last
    else:
      pass
    last = ts
  all_the_time = last - begin
  try:
    return uptime/ all_the_time
  except:
    return 1

if __name__ == "__main__":
  generate_stats()
