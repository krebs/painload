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
f = open(PDB_FILE)
pdb= json.load(f)
f.close()

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
  def GET(self,packer,package):
    if not packer or not package: web.BadRequest()
    else:
      packer = pdb['packer-symlinks'].get(packer,packer) #try to resolve similar packers
      super_packer = pdb['super-packer'].get(packer,'')
      ret = pdb.get(package,{}).get(packer,False)
      ret = ret if ret else pdb.get(package,{}).get(super_packer,False)

      if not ret: 
        web.NotFound()
        return "not found. i'm so sorry :("
      else: return ret



if __name__ == "__main__":
  import sys 
  sys.argv.append("9111")
  app = web.application(urls,globals())
  app.internalerror = web.debugerror
  app.run()
