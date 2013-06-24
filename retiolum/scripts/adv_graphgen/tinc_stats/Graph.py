#!/usr/bin/python

def generate_stats(nodes):
  """ Generates some statistics of the network and nodes
  """
  for k,v in nodes.iteritems():
    conns = v.get('to',[])
    for c in conns: #sanitize weights
      if float(c['weight']) > 9000: c['weight'] = str(9001)
      elif float(c['weight']) < 0: c['weight'] = str(0)
    v['num_conns'] = len(conns)
    v['avg_weight'] = get_node_avg_weight(conns)

def get_node_avg_weight(conns):
  """ calculates the average weight for the given connections """
  if not conns:
    sys.syderr.write("get_node_avg_weight: connection parameter empty")
    return 9001
  else:
    return sum([float(c['weight']) for c in conns])/len(conns)

def delete_unused_nodes(nodes):
  """ Deletes all the nodes which are currently not connected to the network"""
  new_nodes = {}
  for k,v in nodes.iteritems():
    if v['external-ip'] == "(null)":
      continue
    if v.get('to',[]):
      new_nodes[k] = v
  for k,v in new_nodes.iteritems():
    if not [ i for i in v['to'] if i['name'] in new_nodes]:
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
