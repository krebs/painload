#!/usr/bin/python

import web
import json
import os
from bot import *
urls = ( 
  '/', 'Index',
  '/dump','Dump',
#  '/reload','Reload',
  '/(.+)/(.+)', 'ArchFinder',
)


PDB_FILE="db/punani"
PORT="9111"
CHANNEL="#retiolum"
f = open(PDB_FILE)
pdb = json.load(f)
f.close()
polite = os.environ.get("polite",False)
from socket import *

def local_announce(msg):
  s = socket(AF_INET,SOCK_STREAM)
  s.connect(('localhost',5555))
  s.send(msg)
  s.close()
class Index:
  def GET(self):
    ret = """Welcome to the Tightnani API<br/>
Retrieve a package name for your distribution with: /PACKER/PKG"""
    return ret

class Reload:
  def GET(self):
    f = open(PDB_FILE)
    pdb= json.load(f)
    f.close()
    return "DB reloaded"


class Dump:
  def GET(self):
    return json.dumps(pdb,sort_keys=True,indent=4)

class ArchFinder:
  def GET(self,request_packer,package):
    if not request_packer or not package: web.BadRequest()
    else:
      packer = pdb['packer-symlinks'].get(request_packer,request_packer) #try to resolve similar packers
      super_packer = pdb['super-packer'].get(packer,'')
      ret = pdb.get(package,{}).get(packer,False)
      ret = ret if ret else pdb.get(package,{}).get(super_packer,False)

      if not ret:
        try:
          if polite:
            local_announce("Client `%s` asked for the tool `%s` in packer `%s` but i do not have it in my Database. Please update me!" %(web.ctx.ip, package,packer))
          else:
            local_announce("404: no %s/%s for %s" % (request_packer,package,gethostbyaddr(web.ctx.ip)[0]))
        except Exception,e:
          print ("Got Exception %s: %s" % (str(Exception),(e)))
        web.NotFound()
        return "not found. i'm so sorry :("
      else: return ret



if __name__ == "__main__":
  import sys 
  # Set IRC connection parameters.
  irc_servers = [('supernode', 6667)]
  irc_channels = [('#retiolum','')]

  # Prepare and start IRC bot.
  bot = PunaniBot(irc_servers, irc_channels)
  t = Thread(target=bot.start)
  t.daemon = True
  t.start()
  announce = bot.say

  receiver = PunaniReceiveServer()
  t = Thread(target=receiver.serve_forever)
  t.daemon = True
  t.start()

  t = Thread(target=process_queue,args=(announce,receiver.queue))
  t.daemon = True
  t.start()


  sys.argv.append(PORT)
  app = web.application(urls,globals())
  app.internalerror = web.debugerror
  app.run()
