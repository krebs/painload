#!/usr/bin/env python
import os.path
import sys
import tweepy
import re
from socket import *
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY= ''
ACCESS_SECRET = ''
printer = ""

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
mention = api.mentions()[0]
mention_stripped = mention.text.replace("@shacktwinter","").lstrip().rstrip()
mention_stripped = re.sub(r'[^\w _|@\[\]{}()<>:;!#$%^&+=-]+','',mention_stripped)[:32]
f = open(os.path.dirname(os.path.abspath(sys.argv[0]))+"/msg_file","r+")
last = f.read()
#sys.exit(23)
if last == mention_stripped:
  print "received old message"
  sys.exit(23)
else:
  print "received new message: %s" % mention_stripped
  
  s = socket(AF_INET, SOCK_STREAM)
  send_message = \
    '\x1b%%-12345X@PJL JOB\n@PJL RDYMSG DISPLAY="%s"\n@PJL EOJ\n\x1b%%-12345X' % (mention_stripped, )
  s.connect((printer, 9100))
  s.send(send_message)
  s.close()
  f.seek(0)
  f.truncate(0)
  f.write(mention_stripped)
  f.close()
  if not mention.user.following:
          mention.user.follow()
  api.update_status("@%s i appreciate your message '%s' for twinter! Ready Message updated." %(mention.user.screen_name,mention_stripped.upper()),in_reply_to_status_id=mention.id)
