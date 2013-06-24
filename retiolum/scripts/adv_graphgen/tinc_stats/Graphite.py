#!/usr/bin/python

import socket
from time import time

class GraphiteSender:
  def __init__(self,host,port=2003,prefix="retiolum"):
    self.host = host
    self.port = port
    self.prefix = prefix
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    self.sock.connect((host,port))

  def send(name,data):
    # construct a message for graphite, honor the configured prefix
    self.sock.send("%s.%s %d %d\r\n"%(self.prefix,name,data,time()))

  def send_raw(path,data):
    #ignore the configured prefix, just it to the path given
    self.sock.send("%s %d %d\r\n"%(path,data,time()))
    
if __name__ == "__main__":
  import sys
  GraphiteSender(sys.argv[1]).send_raw(sys.argv[2],sys.argv[3])
