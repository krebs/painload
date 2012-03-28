import pygame
import os
from pygame import locals
import json
CFG_FILE = "config.json"
cfg = json.load(open(CFG_FILE))

pygame.init()
pygame.joystick.init()
try:
    j = pygame.joystick.Joystick(0)
    j.init()
    print 'Enabled joystick: ' + j.get_name()
except pygame.error:
    print 'no joystick found.'


while 1:
    for e in pygame.event.get():
        #print 'event : ' + str(e.type)
        #print 'data  : ' + str(e.dict)
        if e.type == pygame.locals.JOYAXISMOTION:
            x, y = j.get_axis(0), j.get_axis(1)
            if (x > 0):
                direction = "right"
            elif(x < 0):
                direction = "left"
            if (y > 0):
                direction = "up"
            elif(y < 0):
                direction = "down"
            if (y == x == 0):
                pass
            else:
                try:
                    os.system(cfg["direction"][direction])
                except Exception as balls:
                    print "direction not defined?", balls

        elif e.type == pygame.locals.JOYBUTTONDOWN:
            try:
                os.system(cfg["button"][str(e.button)])
            except Exception as balls:
                print "button not defined: ", balls
        #elif e.type == pygame.locals.JOYBUTTONUP:
        #    print 'button up', e.joy, e.button
