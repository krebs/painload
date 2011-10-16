#! /bin/python
from libavg import *

#This function is a slightly modified version of cmiles code from dev.c-base.org/c_leuse/c_leuse.git
#It takes a bunch of word nodes an slides them from left to right just as the HTML <marquee> function
line = 16
def welcomeScroll():
    global line
    line += 1
    textNode = player.getElementByID("welcometext")
    if line >= textNode.getNumChildren():
        line = 0
    node = textNode.getChild(line)
    LinearAnim(node, "x", 11500, 1200, -1400, -1000, None, welcomeScroll).start()
#
def start_lightcontrol(event):
    mainwindow = player.getElementByID("mainwindow")
    lightcontrolwindow = player.getElementByID("lightcontrol")
    mainwindow.active =False
    lightcontrolwindow.active =True


player = avg.Player.get()
player.loadFile("main.avg")

player.setTimeout(10, welcomeScroll)
player.getElementByID("light").setEventHandler(avg.CURSORDOWN, avg.MOUSE, start_lightcontrol)
#player.getElementByID("roster").setEventHandler(avg.CURSORDOWN, avg.MOUSE, buttondown)
#player.getElementByID("blank").setEventHandler(avg.CURSORDOWN, avg.MOUSE, buttondown)
player.play()

