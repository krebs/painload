#!/usr/bin/python3
# -*- coding: utf8 -*-
import sys,json,os
from .Graph import delete_unused_nodes,resolve_myself
GEODB=os.environ.get("GEODB","GeoLiteCity.dat")

def copy_map():
    from shutil import copy
    from os.path import dirname,join,realpath
    if len(sys.argv) != 2 or sys.argv[1] == "--help" :
        print("usage: {} <destination>".format(sys.argv[0]))
        print("  copies the map.html file to the <destination>")
        sys.exit(1)
    dstdir=sys.argv[1]
    copy(realpath(join(dirname(__file__),'static/map.html')),dstdir)


def add_geo(nodes):
  from pygeoip import GeoIP
  gi = GeoIP(GEODB)

  for k,v in nodes.items():
    try:
      nodes[k].update(gi.record_by_addr(v["external-ip"]))
    except Exception as e:
      sys.stderr.write(str(e))
      sys.stderr.write("Cannot determine GeoData for %s\n"%k)
  return nodes

def add_coords_to_edges(nodes):
  from pygeoip import GeoIP
  gi = GeoIP(GEODB)

  for k,v in nodes.items():
    for i,j in enumerate(v.get("to",[])):
      data=gi.record_by_addr(j["addr"])
      try:
        j["latitude"]=data["latitude"]
        j["longitude"]=data["longitude"]
      except Exception as e: pass

  return nodes

def add_jitter(nodes):
  from random import random
  #add a bit of jitter to all of the coordinates
  max_jitter=0.005
  for k,v in nodes.items():
    jitter_lat= max_jitter -random()*max_jitter*2
    jitter_long= max_jitter -random()*max_jitter*2
    try:
      v["latitude"]= v["latitude"] + jitter_lat
      v["longitude"]= v["longitude"] + jitter_long
      for nodek,node in nodes.items():
        for to in node['to']:
          if to['name'] == k:
            to['latitude'] = v["latitude"]
            to['longitude'] = v["longitude"]
    except Exception as e: pass
  return nodes

def main():
  import json
  try:
      with open(GEODB,'rb') as f: f.read()
  except Exception as e:
      print("cannot open {} (GEODB in env)".format(GEODB))
      print(e)
      sys.exit(1)
  try:
    nodes = add_jitter(add_coords_to_edges(add_geo(resolve_myself(delete_unused_nodes(json.load(sys.stdin))))))
    print (json.dumps(nodes))
  except Exception as e:
      print("cannot parse data received via stdin")
      print(e)

if __name__ == "__main__":
    main()
