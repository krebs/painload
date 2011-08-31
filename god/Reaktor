#! /usr/bin/env python2
# coding=UTF-8

location = 'shackspace'
host = '0.0.0.0'
port = 2342

map = {
  'shackspace': {
    'device': {
      0: 'Licht0, Zickenzone; Fenster',
      1: 'Licht1, Sofaecke; Fenster', 
      2: 'Licht2, Zickenzone; Ghetto',
      3: 'Licht3, Sofaecke; Ghetto',
      4: 'Licht4, Richtung Getränkelager',
      5: 'Licht5, Porschekonsole',
      6: 'Licht6, Tomatenecke',
      7: 'Licht7, Ghetto',
      10: 'Hauptschalter'
    },
    'state': {
      0: 'aus',
      1: 'an',
      2: 'aus in T-10s'
    },
    '->': 'ist'
  }
}

import socket
from string import join
from struct import unpack

# create udp socket
mysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# allow send/recieve from broacast address
mysocket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)

# allow the socket to be re-used
mysocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
mysocket.bind((host, port))

map = map[location]

while True:
  did, sid = unpack('BB', mysocket.recv(2))
  device, state = map['device'][did], map['state'][sid]
  arrow = map['->']
  print join([device, arrow, state], ' ')
