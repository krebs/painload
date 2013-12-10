from socket import socket, AF_INET,SOCK_DGRAM,IPPROTO_UDP,SOL_SOCKET,SO_REUSEADDR,IP_MULTICAST_TTL,IP_MULTICAST_LOOP,INADDR_ANY,inet_aton,IP_ADD_MEMBERSHIP,IPPROTO_IP
import struct
import threading 
import logging
log = None
from select import select
GROUP = '224.110.42.23'
PORT  = 42023
log = logging.getLogger('CholerabNet')
class CholerabMulicastNet(threading.Thread):
  def __init__(self,cholerab,group=GROUP,port=PORT):
    threading.Thread.__init__(self)
    self.cholerab=cholerab
    self.group=group
    self.port=port
    self.initSocket()
  def send_char(self,x,y,char):
    """ translates given params into network message """
    self.send_mc("%s %d %d" %(str(ord(char)),x,y))
  def send_mc(self,arg):
    """ Sends message via multicast"""
    try:
      log.debug("Sending '%s' to %s:%d" % (arg,self.group,self.port)) 
      self.ignore_next += 1# we need this to work together correctly with reused sockets
      self.s.sendto("%s" % arg,0,(self.group,self.port))
    except Exception ,e:
      self.ignore_next -=1
      log.error("IN send_mc:%s"%str(e))

  def initSocket (self,rcv=1):
    ''' Initializes a Multicast socket '''
    host = ''
    log.debug("Setting up Multicast Socket")
    self.s = socket(AF_INET,SOCK_DGRAM, IPPROTO_UDP)
    self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    self.s.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 32)
    self.s.setsockopt(IPPROTO_IP,IP_MULTICAST_LOOP,1) # we do not want our own packets to be replayed 
    if rcv==1:
      log.debug("Configuring for Read AND Write")
      self.s.bind((host,PORT))
      mreq = struct.pack("4sl", inet_aton(GROUP), INADDR_ANY)
      self.s.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,mreq)
  def run(self):
    self.running = 1
    self.ignore_next = 0
    while self.running:
      # break if we do not want to loop on
      ready,output,exception = select([self.s],[],[],1) # try every second
      for r in ready:
        if r == self.s:
          log.debug(str(self.ignore_next))
          (data,addr) = self.s.recvfrom(1024)
          if not self.ignore_next:
            log.debug("Received Data from %s, data %s"%(str(addr),str(data)))
            self.receive_net(addr,data)
          else:
            self.ignore_next -= 1 

  def send_stupid(self,addr):
    """ sends YOU ARE MADE OF STUPID to the right host """
    #TODO implement me
    pass

  def receive_net(self,addr,data):
    """ resolves which nick sent the message
    TODO handle user resolution in mulicast """
    try: 
      address,port = addr
      arr = str(data).split()
      char = arr[0]
      x = arr[1]
      y = arr[2]
      self.cholerab.write_char(int(x),int(y),chr(int(char)))
    except Exception, e:
      log.error("Triggered YOU ARE MADE OF STUPID: %s" % str(e))
      self.send_stupid(addr)

  def stop(self):
    '''
    stops the whole treading stuff gracefully
    '''
    self.running=0
