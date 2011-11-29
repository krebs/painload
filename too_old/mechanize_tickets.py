#!/usr/bin/python
import mechanize
import cookielib
import time,sys
USERNAME = 'momo'
PASSWORD = ''


def main():
  try:
    br = init_browser()
    while not do_login(br):
      print ("Could Not Login, retrying!")
    while not fetch_ticket(br):
      time.sleep(0.2)
      print ("Could not fetch ticket, retrying!")
  except Exception,e:
    print ("Caught Exception: %s" % str(e))
    exit (1)
  print ("We won? yay")
  exit(0)

def init_browser():
  br = mechanize.Browser()
  br.open("https://presale.events.ccc.de/order")
  cj = cookielib.LWPCookieJar()
  br.set_cookiejar(cj)
  br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
  return br
def do_login(br):
  br.select_form(nr=0)
  br.form['account[username]'] = USERNAME
  br.form['account[password]'] = PASSWORD
  br.submit()
  ret = br.response().read()
  if 'Signed in successfully.' in ret:
    if not "Confirm Order" in ret:
      print("Something else is wrong, cannot find 'Confirm Order' button!")
      raise Exception("Cannot find Confirm Order button")
    return True
  else: return False

def fetch_ticket(br):
  br.select_form(nr=0)
  br.submit()
  ret = br.response().read()
  if not 'There are currently not enough tickets available.' in ret:
    print ("we won? Better sleep some time to be sure")
    return True
  else: return False

if __name__ == "__main__":
  main()
