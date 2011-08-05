#!/usr/bin/python2
# -*- coding: utf-8 -*-
import curses,time
from view import CursesView
from chol_net import CholerabMulicastNet
import logging
logging.basicConfig(filename='here.log',level=logging.DEBUG)
log = logging.getLogger('main')
class Cholerab:
  def __init__(self):
    self.view = CursesView(cholerab=self)
    self.transport = CholerabMulicastNet(cholerab=self)
  def send_char(self,x,y,char):
    log.info("Sending %s at (%d,%d) to connected peers" %(char,x,y))
    self.transport.send_char(x,y,char)

  def write_char(self,x,y,char):
    log.info("Writing %s at (%d,%d) to view" %(char,x,y))
    self.view.write_char(x,y,char,user=2)
  def stop(self):
    self.view.stop()
    self.transport.stop()
  def main(self):
    self.view.start()
    self.transport.start()
    self.view.join()
    #after view dies, kill the transport as well
    self.transport.stop() 
    self.transport.join()
def main():
  log.debug('started main')
  chol = Cholerab()
  chol.main()

if __name__ == "__main__":
  main()
