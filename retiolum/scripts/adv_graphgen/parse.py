#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
""" TODO: Refactoring needed to pull the edges out of the node structures again,
it should be easier to handle both structures"""

def write_digraph(nodes):
  """
  writes the complete digraph in dot format
  """
  print ('digraph retiolum {')
  print ('  node[shape=box,style=filled,fillcolor=grey]')
  print ('  overlap=false')
  generate_stats(nodes)
  nodes = delete_unused_nodes(nodes)
  merge_edges(nodes)
  for k,v in nodes.iteritems():
    write_node(k,v)
  print ('}')
def generate_stats(nodes):
  """ Generates some statistics of the network and nodes
  """
  for k,v in nodes.iteritems():
    v['num_conns'] = len(v.get('to',[]))
def delete_unused_nodes(nodes):
  new_nodes = {}
  for k,v in nodes.iteritems():
    if v['external-ip'] == "(null)":
      continue
    if v.get('to',[]):
      new_nodes[k] = v
  for k,v in new_nodes.iteritems():
    if not [ i for i in v['to'] if i['name'] in new_nodes]:
      #del(new_nodes[k])
      del(k)
  return new_nodes
def merge_edges(nodes):
  """ merge back and forth edges into one
  DESTRUCTS the current structure by deleting "connections" in the nodes

  """
  for k,v in nodes.iteritems():
    for con in v.get('to',[]):
      for i,secon in enumerate(nodes.get(con['name'],{}).get('to',[])):
        if k == secon['name']:
          del (nodes[con['name']]['to'][i])
          con['bidirectional'] = True


def write_node(k,v):
  """ writes a single node and its edges 
      edges are weightet with the informations inside the nodes provided by
      tinc
  """

  node = "  "+k+"[label=\""
  node += k+"\\l"
  node += "external:"+v['external-ip']+":"+v['external-port']+"\\l"
  if v.has_key('num_conns'):
    node += "Num Connects:"+str(v['num_conns'])+"\\l"
  for addr in v.get('internal-ip',['¯\\\\(°_o)/¯']):
    node += "internal:"+addr+"\\l"
  node +="\""
  if v['external-ip'] == "MYSELF":
    node += ",fillcolor=steelblue1"
  node +=",group=\""+v['external-ip'].replace(".","")+"\""
  node += "]"
  print node

  for con in v.get('to',[]):
    edge = "  "+k+ " -> " +con['name'] + "[weight="+str(float(con['weight']))
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
        if not nodes[l[2]].get('internal-ip',False):
           nodes[l[2]]['internal-ip'] = []
        nodes[l[2]]['internal-ip'].append(l[0].split('#')[0])
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
