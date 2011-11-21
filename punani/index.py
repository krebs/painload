#!/usr/bin/python

import web
import json

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
bot = False

try:
  from threading import Thread
  from ircbot import SingleServerIRCBot
  class QuickBot(SingleServerIRCBot):
    def on_welcome(self,conn,event): conn.join(CHANNEL)
    def announce(self,msg): self.connection.privmsg(CHANNEL,"superballs")
    #def on_pubmsg(self,conn,e): conn.privmsg(CHANNEL,"superaidsballs")

  bot = QuickBot([("supernode",6667)],"punani","punani")
  try:
    t = Thread(target=bot.start)
    t.setDaemon(1)
    t.start()
  except (KeyboardInterrupt, SystemExit):
    print("Got Interrupt!")
    sys.exit()
except Exception,e:
  print("Cannot connect to IRC %s" %str(e))

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
          bot.announce("%s asked for %s for the packer %s but i failed to find it. Please help me!" %(web.ctx.ip, packer, package))
        except Exception,e:
          print ("Got Exception %s: %s" % (str(Exception),(e)))
        web.NotFound()
        return "not found. i'm so sorry :("
      else: return ret



if __name__ == "__main__":
  import sys 
  sys.argv.append(PORT)
  app = web.application(urls,globals())
  app.internalerror = web.debugerror
  app.run()
