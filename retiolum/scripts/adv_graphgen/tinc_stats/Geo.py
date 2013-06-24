#!/usr/bin/python3
# -*- coding: utf8 -*-
import sys,json
from Graph import delete_unused_nodes

if __name__ == "__main__":
  from pygeoip import GeoIP
  gi = GeoIP("GeoLiteCity.dat")
  for node,data in delete_unused_nodes(json.load(sys.stdin)).items():
    try:
      print ("%s in %s"%(node,gi.record_by_addr(data["external-ip"])["city"]))
    except:
      print ("%s myself"%node)
