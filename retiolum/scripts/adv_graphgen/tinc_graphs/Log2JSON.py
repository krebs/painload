#!/usr/bin/python
import subprocess
import os
import re
import sys
import json


TINC_NETWORK =os.environ.get("TINC_NETWORK","retiolum")

# is_legacy is the parameter which defines if the tinc config files are handled old fashioned (parse from syslog), 
# or if the new and hip tincctl should be used


# Tags and Delimiters
TINC_TAG="tinc.%s" % TINC_NETWORK
BEGIN_NODES = "Nodes:"
END_NODES = "End of nodes."
BEGIN_SUBNET = "Subnet list:"
END_SUBNET = "End of subnet list"
BEGIN_EDGES = "Edges:"
END_EDGES = "End of edges."
def usage():
  from sys import argv,exit
  print("""usage: %s
This tool dumps all tinc node informations as json

ENVIRONMENT VARIABLES:
  TINC_NETWORK   The tinc network to dump
                      (default: retiolum)
""" % argv[0])
  exit(1)

def debug(func):
  from functools import wraps
  @wraps(func)
  def with_debug(*args,**kwargs):
    print( func.__name__ + " (args: %s | kwargs %s)"% (args,kwargs))
    return func(*args,**kwargs)
  return with_debug


def parse_tinc_stats():
  import subprocess
  from time import sleep
  from distutils.spawn import find_executable as which
  #newest tinc
  if which("tinc"):
    return parse_new_input("tinc")
  #new tinc
  elif which("tincctl"):
    return parse_new_input("tincctl")
  #old tinc
  elif which("tincd"):
      print("old tincd not supported")
      sys.exit(1)
  else:
    raise Exception("no tinc executable found!")


def parse_new_input(tinc_bin):
  nodes = {}
  pnodes = subprocess.Popen(
          [tinc_bin,"-n",TINC_NETWORK,"dump","reachable","nodes"],
          stdout=subprocess.PIPE).communicate()[0].decode()
  for line in pnodes.split('\n'):
    if not line: continue
    l = line.split()
    n = l[0]

    token = l[1]
    if token == 'id':
        # new format
        # <name> id <ident> at <ip> port <port>
        ident = l[1]
        l = l[2:]  #shift over 'id <ident>'
    # else: # token = 'at'
        # old format:
        # <name> at <ip> port <port>
    _,_,ip,_,port = l[:5]
    nodes[n]= { 'external-ip': ip, 'external-port' : l[4] }

  psubnets = subprocess.check_output(
          [tinc_bin,"-n",TINC_NETWORK,"dump","subnets"]).decode()
  for line in psubnets.split('\n'):
    if not line: continue
    l = line.split()
    try:
      if not nodes[l[2]].get('internal-ip',False):
         nodes[l[2]]['internal-ip'] = []
      nodes[l[2]]['internal-ip'].append(l[0].split('#')[0])
    except KeyError:
      pass # node does not exist (presumably)

  pedges = subprocess.check_output(
          [tinc_bin,"-n",TINC_NETWORK,"dump","edges"]).decode()
  for line in pedges.split('\n'):
    if not line: continue
    l = line.split()
    # TODO: tokenize this and parse the line
    n = l[0]
    try:
      if not 'to' in nodes[l[0]] :
        nodes[n]['to'] = []
      nodes[n]['to'].append(
          {'name':l[2],'addr':l[4],'port':l[6],'weight' : l[-1] })
    except KeyError:
      pass #node does not exist
  return nodes

def main():
  from sys import argv
  if len(argv) > 1:
    usage()
  else:
    print (json.dumps(parse_tinc_stats()))

if __name__ == '__main__':
    main()
