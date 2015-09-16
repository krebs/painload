#!/usr/bin/python
from .BackwardsReader import BackwardsReader
import sys,json,os
from .Supernodes import check_all_the_super
from .Services import add_services
from .Availability import get_node_availability
import sys,json
from time import time
DUMP_FILE = os.environ.get("AVAILABILITY_FILE", "tinc-availability.json")
hostpath=os.environ.get("TINC_HOSTPATH", "/etc/tinc/retiolum/hosts")

# will be filled later
supernodes= []

def resolve_myself(nodes):
  #resolve MYSELF to the real ip
  for k,v in nodes.items():
    if v["external-ip"] == "MYSELF":
      for nodek,node in nodes.items():
         for to in node['to']:
           if to['name'] == k:
             v["external-ip"] = to["addr"]
  return nodes


def dump_graph(nodes):
  from time import time
  graph = {}
  graph['nodes'] = nodes
  graph['timestamp'] = time()
  f = open(DUMP_FILE,'a')
  json.dump(graph,f)
  f.write('\n')
  f.close()

def generate_availability_stats(nodes):
  """ generates stats of from availability
  """
  jlines = []
  # try:
  #   f = BackwardsReader(DUMP_FILE)
  #   lines_to_use = 1000
  #   while True:
  #     if lines_to_use == 0: break
  #     line = f.readline()
  #     if not line: break
  #     jline = json.loads(line)
  #     if not jline['nodes']: continue

  #     jlines.append(jline)
  #     lines_to_use -=1
  # except Exception as e: sys.stderr.write(str(e))

  for k,v in nodes.items():
    # TODO: get this information in a different way
    v['availability'] = get_node_availability(k,[])


def generate_stats(nodes):
  """ Generates some statistics of the network and nodes
  """
  for k,v in nodes.items():
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
  for k,v in nodes.items():
    if v['external-ip'] == "(null)":
      continue
    if v.get('to',[]):
      new_nodes[k] = v
  for k,v in new_nodes.items():
    if not [ i for i in v['to'] if i['name'] in new_nodes]:
      del(k)
  return new_nodes

def merge_edges(nodes):
  """ merge back and forth edges into one
  DESTRUCTS the current structure by deleting "connections" in the nodes
  """
  for k,v in nodes.items():
    for con in v.get('to',[]):
      for i,secon in enumerate(nodes.get(con['name'],{}).get('to',[])):
        if k == secon['name']:
          del (nodes[con['name']]['to'][i])
          con['bidirectional'] = True


def print_head():
  print ('digraph retiolum {')
  print ('  graph [center=true packMode="clust"]')
  print ('  node[shape=box,style=filled,fillcolor=grey]')
  print ('  overlap=false')

def print_stat_node(nodes):
  ''' Write a `stats` node in the corner
      This node contains infos about the current number of active nodes and connections inside the network
  '''
  from time import localtime,strftime
  num_conns = 0
  num_nodes = len(nodes)
  try: 
    msg = '%s.num_nodes %d %d\r\n' %(g_path,num_nodes,begin)
    s.send(msg)
  except Exception as e: pass
  for k,v in nodes.items():
    num_conns+= len(v['to'])
  node_text = "  stats_node [label=\"Statistics\\l"
  node_text += "Build Date  : %s\\l" % strftime("%Y-%m-%d %H:%M:%S",localtime())
  node_text += "Active Nodes: %s\\l" % num_nodes
  node_text += "Connections : %s\\l" % num_conns
  node_text += "\""
  node_text += ",fillcolor=green"
  node_text += "]"
  print(node_text)

def print_node(k,v):
  """ writes a single node and its edges 
      edges are weightet with the informations inside the nodes provided by
      tinc
  """

  node = "  "+k+"[label=<<TABLE border='0' title='%s' cellborder='1' >" %k
  node += "<TR><TD colspan='2'><B>%s</B></TD></TR>"%k
  if 'availability' in v:
    node += "<TR><TD>availability:</TD><TD>%f</TD></TR>" % v['availability'] 

  if 'num_conns' in v:
    node += "<TR><TD>Num Connects:</TD><TD>%s</TD></TR>"%str(v['num_conns'])

  node += "<TR><TD>external:</TD><TD>"+v['external-ip']+":"+v['external-port']+"</TD></TR>"
  for addr in v.get('internal-ip',['dunno lol']): 
    node += "<TR><TD>internal:</TD><TD>%s</TD></TR>"%addr

  if 'services' in v:
    node +="<TR><TD colspan='2'><B>Services:</B></TD></TR>"
    for service in v['services']:
      try:uri,comment = service.split(" ",1)
      except: 
        uri = service
        comment =""
      node +="<TR >"
      uri_proto=uri.split(":")[0]
      uri_rest = uri.split(":")[1] 
      if not uri_rest:
        node +="<TD title='{0}' align='left' colspan='2' \
href='{0}'><font color='darkred'>{0}</font>".format(uri)
      else:
        node +="<TD title='{0}' align='left' colspan='2' \
href='{0}'><U>{0}</U>".format(uri)
      if comment:
        node += "<br align='left'/>    <I>{0}</I>".format(comment)
      node +="</TD></TR>"
  # end label
  node +="</TABLE>>"

  if v['num_conns'] == 1:
    node += ",fillcolor=red"
  elif k in supernodes:
    node += ",fillcolor=steelblue1"
  node += "]"

  print(node)

def print_anonymous_node(k,v):
  """ writes a single node and its edges 
      edges are weightet with the informations inside the nodes provided by
      tinc
  """
  
  node = "  "+k #+"[label=\""
  print(node)

def print_edge(k,v):
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
    print(edge)

def anonymize_nodes(nodes):
  #anonymizes all nodes
  i = "0"
  newnodes = {}
  for k,v in nodes.items():
    for nodek,node in nodes.items():
      for to in node['to']:
        if to['name'] == k:
          to['name'] = i
    newnodes[i] = v
    i = str(int(i)+1)
  return newnodes

def main():
  if len(sys.argv) != 2 or  sys.argv[1] not in ["anonymous","complete"]: 
    print("usage: %s (anonymous|complete)")
    sys.exit(1)

  nodes = json.load(sys.stdin)
  nodes = delete_unused_nodes(nodes)
  print_head()
  generate_stats(nodes)
  merge_edges(nodes)


  if sys.argv[1] == "anonymous":
    nodes = anonymize_nodes(nodes)

    for k,v in nodes.items():
      print_anonymous_node(k,v)
      print_edge(k,v)

  elif sys.argv[1] == "complete":
    try:
      for supernode,addr in check_all_the_super(hostpath):
        supernodes.append(supernode)
    except FileNotFoundError as e:
      print("!! cannot load list of supernodes ({})".format(hostpath))
      print("!! Use TINC_HOSTPATH env to override")
      sys.exit(1)

    generate_availability_stats(nodes)
    add_services(nodes)
    for k,v in nodes.items():
      print_node(k,v)
      print_edge(k,v)

    #TODO: get availability somehow else
    # try:
    #   dump_graph(nodes)
    # except Exception as e:
    #   sys.stderr.write("Cannot dump graph: %s" % str(e))
  else:
    pass

  print_stat_node(nodes)
  print ('}')

if __name__ == "__main__":
  main()

# vim: set sw=2:ts=2
