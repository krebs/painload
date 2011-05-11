#!/usr/bin/python2

import sys

def write_digraph(nodes):
  print ('digraph retiolum {')
  print ('  node[shape=box,style=filled,fillcolor=grey]')
  for k,v in nodes.iteritems():
    write_node(k,v)
  print ('}')
def write_node(k,v):
  node = "  "+k+"[label=\""
  node += k+"\\l"
  node += "external:"+v['external-ip']+":"+v['external-port']+"\\l"
  node += "internal:"+v['internal-ip']+"\\l\""
  if v['external-ip'] == "MYSELF":
    node += ",fillcolor=steelblue1"
  node += "]"
  print (node)
  for con in v.get('to',[]):
    print "  "+k+ "->" +con['name'] + "[weight="+str(10/float(con['weight']))+"]"

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
