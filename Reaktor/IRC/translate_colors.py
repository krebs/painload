

COLOR_MAP = {
    "\x1b[0m" :  "\x0F", # reset
    "\x1b[37m" : "\x0300",
    "\x1b[30m" : "\x0301",
    "\x1b[34m" : "\x0302",
    "\x1b[32m" : "\x0303",
    "\x1b[31m" : "\x0304",
    "\x1b[33m" : "\x0305",
    "\x1b[35m" : "\x0306",
    "\x1b[33m" : "\x0307",
    "\x1b[33m" : "\x0308",
    "\x1b[32m" : "\x0309",
    "\x1b[36m" : "\x0310",
    "\x1b[36m" : "\x0311",
    "\x1b[34m" : "\x0312",
    "\x1b[31m" : "\x0313",
    "\x1b[30m" : "\x0314",
    "\x1b[37m" : "\x0315",
    "\x1b[1m" :  "\x02", # bold on
    "\x1b[22m" : "\x02" # bold off
  }
def translate_colors (line):
  for color,replace in COLOR_MAP.items():
    line = line.replace(color,replace)
  return line

if __name__ == "__main__":
  import sys
  print (translate_colors(sys.stdin.read()))
