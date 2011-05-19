#!/usr/bin/python2

import sys
""" TODO: Refactoring needed to pull the edges out of the node structures again,
it should be easier to handle both structures"""

def write_digraph(nodes):
  """
  writes the complete digraph in dot format
  """
  print ('digraph retiolum {')
  print ('  node[shape=box,style=filled,fillcolor=grey]')
  generate_stats(nodes)
  merge_edges(nodes)
  for k,v in nodes.iteritems():
    write_node(k,v)
  print ('}')
def generate_stats(nodes):
  """ Generates some statistics of the network and nodes
  """
  for k,v in nodes.iteritems():
    v['num_conns'] = len(v.get('to',[]))

def merge_edges(nodes):
  """ merge back and forth edges into one
  DESTRUCTS the current structure by deleting "connections" in the nodes

  """
  for k,v in nodes.iteritems():
    for con in v.get('to',[]):
      for i,secon in enumerate(nodes[con['name']].get('to',[])):
        if k == secon['name']:
          del (nodes[con['name']]['to'][i])
          con['bidirectional'] = True


def write_node(k,v):
  """ writes a single node and its edges """
  node = "  "+k+"[label=\""
  node += k+"\\l"
  node += "external:"+v['external-ip']+":"+v['external-port']+"\\l"
  if v.has_key('num_conns'):
    node += "Num Connects:"+str(v['num_conns'])+"\\l"
  node += "internal:"+v['internal-ip']+"\\l\""
  if v['external-ip'] == "MYSELF":
    node += ",fillcolor=steelblue1"
  node += "]"
  print (node)
  for con in v.get('to',[]):
    edge = "  "+k+ " -> " +con['name'] + "[weight="+str(10/float(con['weight']))
    if con.get('bidirectional',False):
      edge += ",dir=both"
    edge += "]"
    print edge
def parse_input():
  nodes={}
  for line in sys.stdin:
    line = line.replace('\n','')
    if line == 'Nodes:':
      nodes={}
      for line in sys.stdin:
        if line == 'End of nodes.\n':
          break
        l = line.replace('\n','').split() #TODO unhack me
        nodes[l[0]]= { 'external-ip': l[2], 'external-port' : l[4] }
    if line == 'Subnet list:':
      for line in sys.stdin:
        if line == 'End of subnet list.\n':
          break
        l = line.replace('\n','').split() 
        nodes[l[2]]['internal-ip'] = l[0].split('#')[0]
    if line == 'Edges:':
      edges = {}
      for line in sys.stdin:
        if line == 'End of edges.\n':
          break
        l = line.replace('\n','').split() 

        if not nodes[l[0]].has_key('to') :
          nodes[l[0]]['to'] = []
        nodes[l[0]]['to'].append(
            {'name':l[2],'addr':l[4],'port':l[6],'weight' : l[10] })
  return nodes
nodes = parse_input()
write_digraph(nodes)
