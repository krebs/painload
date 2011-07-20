#!/usr/bin/python2

from curses import *
import socket
import threading

class CursesView(threading.Thread):
    def stop(self):
        self.running = False
        nocbreak(); self.scr.keypad(0); echo()
        endwin()

    def run(self):
        self.running = True
        def try_move(x,y):
            if x >= self.width: x = 0;y = y+1
            if x < 0 : x = self.width-1; y= y-1
            if y >= self.height : x = x+1;y = 0
            if y < 0 : x = x-1; y = self.height-1
            self.win.move(y,x); return x,y

        while self.running:
            c = self.scr.getch()
            if c == KEY_LEFT : self.x -=1
            elif c == KEY_RIGHT : self.x +=1
            elif c == KEY_UP : self.y -=1
            elif c == KEY_DOWN : self.y +=1
            elif c == ord('q') : self.stop()
            #TODO handle backspace correctly
            else : 
                try: 
                    self.win.addch(c) #TODO UTF8 here
                    #self.cholerab.write_char(self.x,self.y,c)
                except: 
                    pass
                self.x +=1
            self.x,self.y = try_move(self.x,self.y)
            self.refresh()

    def write_char(self,x,y,char):
        self.win.addch(y,x,char)
        self.win.move(self.y,self.x)
        self.refresh()
    def refresh(self):
        self.scr.refresh()
        self.win.refresh()
    def clear(self):
        pass
    def write_field(self,ar):
        """
        writes the whole field with given 2-dimensional array
        """
        self.clear()
        pass


    def __init__(self,height=24,width=80,cholerab=None):
        self.cholerab = cholerab
        threading.Thread.__init__(self)
        self.scr = initscr()
            noecho()
        cbreak()
        self.scr.keypad(1)
        try:
            curs_set(2)
        except: # go home with your non-standard terminals!
            pass

        begin_x = 0;begin_y = 0
        self.height = height
        self.width = width
        self.x = 0 ; self.y = 0

        self.win = newwin(height,width,begin_y,begin_x)

