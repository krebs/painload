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
    from time import time
    self.sock.send("%s.%s %d %d\r\n"%self.prefix,data,time())
