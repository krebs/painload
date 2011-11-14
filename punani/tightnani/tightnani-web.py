#!/usr/bin/python

import web
import json

urls = ( 
  '/', 'Index',
  '/dump','Dump',
  '/reload','Reload',
  '/(.+)/(.+)', 'ArchFinder',
)


PDB_FILE="tightnani_db"

pdb= json.load(open(PDB_FILE))

class Index:
  def GET(self):
    ret = """Welcome to the Tightnani API<br/>
Retrieve a package name for your distribution with: /ARCH/PKG"""
    return ret

class Reload:
  def GET(self):
    pdb= json.load(open(PDB_FILE))
    return "DB reloaded"


class Dump:
  def GET(self):
    return json.dumps(pdb,sort_keys=True,indent=4)

class ArchFinder:
  def GET(self,packer,package):
    if not packer or not package: web.BadRequest()
    else:
      packer = pdb['packer-symlinks'].get(packer,packer) #try to resolve similar packers
      ret = pdb.get(package,{}).get(packer,False)
      if not ret: web.NotFound()
      else: return ret



if __name__ == "__main__":
  app = web.application(urls,globals())
  app.internalerror = web.debugerror
  app.run()
