#!/usr/bin/python
import sys
wont_change = [ ' ', '\n']
for line in sys.stdin:
  for char in line:
    if char in wont_change: print char,
    else: print unichr(0xFF00 + ord(char)-32),
