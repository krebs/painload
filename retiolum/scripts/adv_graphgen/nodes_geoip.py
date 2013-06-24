#!/usr/bin/python3
# -*- coding: utf8 -*-
import sys,json

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

if __name__ == "__main__":
  from pygeoip import GeoIP
  gi = GeoIP("GeoLiteCity.dat")
  for node,data in delete_unused_nodes(json.load(sys.stdin)).items():
    
    try:
      print ("%s in %s"%(node,gi.record_by_addr(data["external-ip"])["city"]))
    except:
      print ("%s myself"%node)
