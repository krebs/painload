#!/usr/bin/python
# -*- coding: utf8 -*-
from tinc_stats.BackwardsReader import BackwardsReader
from tinc_stats.Graph import generate_stats,delete_unused_nodes,merge_edges
import sys,json
#supernodes= [ "kaah","supernode","euer","pa_sharepoint","oxberg" ]
try:
  import socket
  from time import time
  import os
  host = os.environ.get("GRAPHITE_HOST","localhost")
  port = 2003
  g_path =  os.environ.get("GRAPHITE_PATH","retiolum")
  begin = time()
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
  sys.stderr.write("connecting to %s:%d"%(host,port))
  s.connect((host,port))
except Exception as e:
  sys.stderr.write( "Cannot connect to graphite: " + str(e))
""" TODO: Refactoring needed to pull the edges out of the node structures again,
it should be easier to handle both structures"""
DUMP_FILE = "/krebs/db/availability"

def write_digraph(nodes):
  """
  writes the complete digraph in dot format
  """
  print ('digraph retiolum {')
  #print ('  graph [center rankdir=LR packMode="clust"]')
  print ('  graph [center packMode="clust"]')
  print ('  node[shape=circle,style=filled,fillcolor=grey]')
  print ('  overlap=false')
  generate_stats(nodes)
  merge_edges(nodes)
  nodes = anon_nodes(nodes)
  for k,v in nodes.iteritems():
    write_node(k,v)
  write_stat_node(nodes)
  print ('}')

def anon_nodes(nodes):
  #anonymizes all nodes
  i = "0"
  newnodes = {}
  for k,v in nodes.iteritems():
    for nodek,node in nodes.iteritems():
      for to in node['to']:
        if to['name'] == k:
          to['name'] = i
    newnodes[i] = v
    i = str(int(i)+1)
  return newnodes

def write_stat_node(nodes):
  ''' Write a `stats` node in the corner
      This node contains infos about the current number of active nodes and connections inside the network
  '''
  from time import localtime,strftime
  num_conns = 0
  num_nodes = len(nodes)
  for k,v in nodes.iteritems():
    num_conns+= len(v['to'])
  node_text = "  stats_node [shape=box,label=\"Statistics\\l"
  node_text += "Build Date  : %s\\l" % strftime("%Y-%m-%d %H:%M:%S",localtime())
  node_text += "Active Nodes: %s\\l" % num_nodes
  node_text += "Connections : %s\\l" % num_conns
  node_text += "\""
  node_text += ",fillcolor=green"
  node_text += "]"
  print(node_text)



def write_node(k,v):
  """ writes a single node and its edges 
      edges are weightet with the informations inside the nodes provided by
      tinc
  """
  
  node = "  "+k #+"[label=\""
  print node

  for con in v.get('to',[]):
    label  = con['weight']
    w = int(con['weight'])
    weight = str(1000 - (((w - 150) * (1000 - 0)) / (1000 -150 )) + 0)

    length = str(float(w)/1500)
    if float(weight) < 0 :
      weight= "1"

    edge = "  "+k+ " -> " +con['name'] + " [label="+label + " weight="+weight 
    if con.get('bidirectional',False):
      edge += ",dir=both"
    edge += "]"
    print edge
if __name__ == "__main__":
  nodes = delete_unused_nodes(json.load(sys.stdin))
  write_digraph(nodes)
  try: 
    end = time()
    msg = '%s.graph.anon_build_time %d %d\r\n' % (g_path,((end-begin)*1000),end)
    s.send(msg)
    s.close()
  except Exception as e: pass
