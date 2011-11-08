#!/usr/bin/python
# -*- coding: utf8 -*-

import sys,json
""" TODO: Refactoring needed to pull the edges out of the node structures again,
it should be easier to handle both structures"""
DUMP_FILE = "/krebs/db/availability"

def get_all_nodes():
  import os
  return os.listdir("/etc/tinc/retiolum/hosts")
def generate_stats():
  """ Generates some statistics of the network and nodes
  """
  import json
  jlines = []
  try:
    f = open(DUMP_FILE,'r')
    for line in f:
      jlines.append(json.loads(line))
    f.close()
  except Exception,e:
    pass
  all_nodes = {}
  for k in get_all_nodes():
    all_nodes[k] = get_node_availability(k,jlines)
  print ( json.dumps(all_nodes))

def get_node_availability(name,jlines):
  """ calculates the node availability by reading the generated dump file
  adding together the uptime of the node and returning the time
	parms:
          name - node name
          jlines - list of already parsed dictionaries node archive
  """
  begin = last = current = 0
  uptime = 0
  #sys.stderr.write ( "Getting Node availability of %s\n" % name)
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
      #sys.stderr.write("%s offline at timestamp %f\n" %(name,current))
    last = ts
  all_the_time = last - begin
  try:
    return uptime/ all_the_time
  except:
    return 1


generate_stats()
