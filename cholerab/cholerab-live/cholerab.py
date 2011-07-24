#!/usr/bin/python2
# -*- coding: utf-8 -*-
import curses,time
from view import CursesView
import logging
logging.basicConfig(filename='here.log',level=logging.DEBUG)
log = logging.getLogger('main')
def main(scr):
  log.debug('started main')
  a = CursesView(scr=scr)
  a.start()
  log.debug
  a.write_char(5,5,'p')
  a.write_char(6,5,'e')
  a.write_char(7,5,'n')
  a.write_char(8,5,'i')
  a.write_char(9,5,'s')
  a.write_str(5,6,'¯\(°_o)/¯',user=2)
  for i in range(7,11):
    time.sleep(2)
    a.write_str(5,i,'¯\(°_o)/¯',user=3)
  a.join()
curses.wrapper(main)
