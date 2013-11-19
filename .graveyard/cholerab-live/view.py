#!/usr/bin/python2

from curses import *
import socket
import threading
import logging
log = logging.getLogger('cholerab-curses')

class CursesView(threading.Thread):
  def addch(self,char):
    """
    adds a char at the current cursor position
    abstraction to the curses win.addch()
    """
    try: self.win.addch(char)
    except: pass
    self.cholerab.send_char(self.x,self.y,chr(char))
  def stop(self):
    #TODO setting back the whole terminal currently does not work correctly, fix me harder
    self.running = False
    self.clear()
    self.win.refresh()
    nocbreak(); self.scr.keypad(0); echo()
    #endwin()

  def run(self):
    """
    input loop

    TODO add Unicode Input Support
    """
    self.running = True
    def try_move(x,y):
      if x >= self.width: x = 0;y = y+1
      if x < 0 : x = self.width-1; y= y-1
      if y >= self.height : x = x+1;y = 0
      if y < 0 : x = x-1; y = self.height-1
      self.win.move(y,x); return x,y

    while self.running:
      c = self.scr.getch() #get_char(self.scr) 
                           #TODO UTF8 here, get_wch not yet implemented
      log.debug("Pressed : %d" % c)
      if c == KEY_LEFT : self.x -=1
      elif c == KEY_RIGHT : self.x +=1
      elif c == KEY_UP : self.y -=1
      elif c == KEY_DOWN : self.y +=1
      elif c == ord('q') : self.stop()
      elif c == 127 or c == KEY_BACKSPACE: 
        log.info('backspace pressed')
        self.x -=1; 
        self.x,self.y = try_move(self.x,self.y)
        self.addch(ord(' '))
      elif c == ord('\n'): 
        log.info('enter pressed')
        self.y +=1; 
        self.x,self.y = try_move(self.x,self.y)
      else : 
        self.addch(c) 
        self.x +=1
      self.x,self.y = try_move(self.x,self.y)
      self.refresh()

  def write_char(self,x,y,char,user=1):
    user = user % 3 + 1
    self.win.addch(y,x,char,color_pair(user))
    self.win.move(self.y,self.x)
    self.refresh()
  def write_str(self,x,y,string,user=1):
    self.win.addstr(y,x,string,color_pair(user))
    self.win.move(self.y,self.x)
    self.refresh()
  def refresh(self):
    self.scr.refresh()
    self.win.refresh()
  def clear(self):
    self.win.clear()
    pass
  def write_field(self,ar):
    """
    writes the whole field with given 2-dimensional array
    """
    self.clear()
    pass

  def __init__(self,height=24,width=80,cholerab=None,scr=None):
    # TODO handle sessions somehow
    if scr:
     self.scr = scr
    else:
     self.scr = initscr()
    start_color()
    init_pair(1,COLOR_WHITE,COLOR_BLACK)
    init_pair(2,COLOR_RED,COLOR_BLACK)
    init_pair(3,COLOR_GREEN,COLOR_BLACK)
    init_pair(3,COLOR_CYAN,COLOR_BLACK)
    threading.Thread.__init__(self)
    self.cholerab = cholerab

    noecho()
    cbreak()
    self.scr.keypad(1)
    try: curs_set(2)
    except: pass # go home with your non-standard terminals!

    begin_x = 0;begin_y = 0
    self.height = height
    self.width = width
    self.x = 0 ; self.y = 0

    self.win = newwin(height,width,begin_y,begin_x)
    self.clear()
