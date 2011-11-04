import sys
import os
import string

class BackwardsReader:
  """ Stripped and stolen from : http://code.activestate.com/recipes/120686-read-a-text-file-backwards/ """
  def readline(self):
    while len(self.data) == 1 and ((self.blkcount * self.blksize) < self.size):
      self.blkcount = self.blkcount + 1
      line = self.data[0]
      try:
        self.f.seek(-self.blksize * self.blkcount, 2) 
        self.data = string.split(self.f.read(self.blksize) + line, '\n')
      except IOError:  
        self.f.seek(0)
        self.data = string.split(self.f.read(self.size - (self.blksize * (self.blkcount-1))) + line, '\n')

    if len(self.data) == 0:
      return ""

    line = self.data[-1]
    self.data = self.data[:-1]
    return line + '\n'

  def __init__(self, file, blksize=4096):
    """initialize the internal structures"""
    self.size = os.stat(file)[6]
    self.blksize = blksize
    self.blkcount = 1
    self.f = open(file, 'rb')
    if self.size > self.blksize:
      self.f.seek(-self.blksize * self.blkcount, 2) 
    self.data = string.split(self.f.read(self.blksize), '\n')
    if not self.data[-1]:
      self.data = self.data[:-1]
