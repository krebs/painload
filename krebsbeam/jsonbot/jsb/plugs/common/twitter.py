# jsb/plugs/common/twitter.py
#
#

""" a twitter plugin for the JSONBOT, currently post only .. uses tweepy oauth. """

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.utils.pdol import Pdol
from jsb.utils.textutils import html_unescape
from jsb.utils.generic import waitforqueue, strippedtxt, splittxt
from jsb.lib.persist import PlugPersist
from jsb.utils.twitter import twitterapi, twittertoken
from jsb.lib.datadir import getdatadir
from jsb.lib.jsbimport import _import_byfile

## tweppy imports

from jsb.contrib.tweepy.auth import OAuthHandler
from jsb.contrib.tweepy.api import API
from jsb.contrib.tweepy import oauth
from jsb.contrib.tweepy.error import TweepError
from jsb.contrib.tweepy.models import Status, User
from jsb.contrib import tweepy


## basic imports

import os
import urllib2
import types
import logging

## credentials

def getcreds(datadir):
    try:
        mod = _import_byfile("credentials", datadir + os.sep + "config" + os.sep + "credentials.py")
    except (IOError, ImportError):
        logging.info("the twitter plugin needs the credentials.py file in the %s/config dir. see %s/examples" % (datadir, datadir))
        return (None, None)
    return mod.CONSUMER_KEY, mod.CONSUMER_SECRET

## defines

auth = None
go = True

def getauth(datadir):
    """ get auth structure from datadir. """
    global auth
    if auth: return auth
    key, secret = getcreds(datadir)
    auth = OAuthHandler(key, secret)
    return auth

## postmsg function

def postmsg(username, txt):
    """ post a message on twitter. """
    try:
        result = splittxt(txt, 139)
        twitteruser = TwitterUsers("users")
        key, secret = getcreds(getdatadir())
        token = twittertoken(key, secret, twitteruser, username)
        if not token:
            raise TweepError("Can't get twitter token")
        twitter = twitterapi(key, secret, token)
        for txt in result:
            status = twitter.update_status(txt)
        logging.info("logged %s tweets for %s" % (len(result), username))
    except TweepError, ex: logging.error("twitter - error: %s" % str(ex))
    return len(result)
    
## TwitterUsers class

class TwitterUsers(PlugPersist):

    """ manage users tokens. """

    def add(self, user, token):
        """ add a user with his token. """
        user = user.strip().lower()
        self.data[user] = token
        self.save()

    def remove(self, user):
        """ remove a user. """
        user = user.strip().lower()
        if user in self.data:
            del self.data[user]
            self.save()

    def size(self):
        """ return size of twitter users. """
        return len(self.data)

    def __contains__(self, user):
        """ check if user exists. """
        user = user.strip().lower()
        return user in self.data


## twitter command

def handle_twitter(bot, ievent):
    """ arguments: <txt> - send a twitter message. """
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the .jsb/data/config dir. see .jsb/data/examples") ; return
    if not ievent.rest: ievent.missing('<txt>') ; return
    else:
        try: nritems = postmsg(ievent.user.data.name, ievent.rest) ; ievent.reply("%s tweet posted" % nritems)
        except TweepError, ex:
             if "token" in str(ex): ievent.reply("you are not registered yet.. use !twitter-auth")
        except (TweepError, urllib2.HTTPError), e: ievent.reply('twitter failed: %s' % (str(e),))
 
cmnds.add('twitter', handle_twitter, ['USER', 'GUEST'])
examples.add('twitter', 'posts a message on twitter', 'twitter just found the http://jsonbot.org project')

## twitter-cmnd command

def handle_twittercmnd(bot, ievent):
    """ arguments: <API cmnd> - do a twitter API cmommand. """
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the .jsb/data//config dir. see .jsb/data/examples") ; return
    if not ievent.args: ievent.missing('<API cmnd>') ; return
    target =  strippedtxt(ievent.args[0])
    try:
        twitteruser = TwitterUsers("users")
        token = twitteruser.data.get(ievent.user.data.name)
        if not token: ievent.reply("you are not logged in yet .. run the twitter-auth command.") ; return 
        key, secret = getcreds(getdatadir())
        token = oauth.OAuthToken(key, secret).from_string(token)
        twitter = twitterapi(key, secret, token)
        cmndlist = dir(twitter)
        cmnds = []
        for cmnd in cmndlist:
            if cmnd.startswith("_") or cmnd == "auth": continue
            else: cmnds.append(cmnd)
        if target not in cmnds: ievent.reply("choose one of: %s" % ", ".join(cmnds)) ; return
        try: method = getattr(twitter, target)
        except AttributeError: ievent.reply("choose one of: %s" % ", ".join(cmnds)) ; return
        result = method()
        res = []
        for item in result:
            try: res.append("%s - %s" % (item.screen_name, item.text))
            except AttributeError:
                try: res.append("%s - %s" % (item.screen_name, item.description))
                except AttributeError:
                    try: res.append(unicode(item.__getstate__()))
                    except AttributeError: res.append(dir(i)) ; res.append(unicode(item))
        ievent.reply("result of %s: " % target, res) 
    except KeyError: ievent.reply('you are not logged in yet. see the twitter-auth command.')
    except (TweepError, urllib2.HTTPError), e: ievent.reply('twitter failed: %s' % (str(e),))

cmnds.add('twitter-cmnd', handle_twittercmnd, 'OPER')
examples.add('twitter-cmnd', 'do a cmnd on the twitter API', 'twitter-cmnd home_timeline')

## twitter-confirm command

def handle_twitter_confirm(bot, ievent):
    """ arguments: <PIN code> - confirm auth with PIN. """
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the %s/config dir. see .jsb/data/examples" % getdatadir()) ; return
    pin = ievent.args[0]
    if not pin: ievent.missing("<PIN> .. see the twitter-auth command.") ; return
    try: access_token = getauth(getdatadir()).get_access_token(pin)
    except (TweepError, urllib2.HTTPError), e: ievent.reply('twitter failed: %s' % (str(e),)) ; return
    twitteruser = TwitterUsers("users")
    twitteruser.add(ievent.user.data.name, access_token.to_string())
    ievent.reply("access token saved.")

cmnds.add('twitter-confirm', handle_twitter_confirm, ['OPER', 'USER', 'GUEST'])
examples.add('twitter-confirm', 'confirm your twitter account', 'twitter-confirm 6992762')

## twitter-auth command

def handle_twitter_auth(bot, ievent):
    """ no arguments - get url to get the auth PIN needed for the twitter-confirm command. """
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the .jsb/data/config dir. see .jsb/data/examples") ; return
    try: auth_url = getauth(getdatadir()).get_authorization_url()
    except (TweepError, urllib2.HTTPError), e: ievent.reply('twitter failed: %s' % (str(e),)) ; return
    if bot.type == "irc":
        bot.say(ievent.nick, "sign in at %s" % auth_url)
        bot.say(ievent.nick, "use the provided code in the twitter-confirm command.")
    else:
        ievent.reply("sign in at %s" % auth_url)
        ievent.reply("use the provided code in the twitter-confirm command.")

cmnds.add('twitter-auth', handle_twitter_auth, ['OPER', 'USER', 'GUEST'])
examples.add('twitter-auth', 'adds your twitter account', 'twitter-auth')

## twitter-friends command

def handle_twitterfriends(bot, ievent):
    """ no arguments - show friends timeline (your normal twitter feed). """
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the .jsb/data/config dir. see .jsb/data/examples") ; return
    try:
        twitteruser = TwitterUsers("users")
        token = twitteruser.data.get(ievent.user.data.name)
        if not token: ievent.reply("you are not logged in yet .. run the twitter-auth command.") ; return 
        key , secret = getcreds(getdatadir())
        token = oauth.OAuthToken(key, secret).from_string(token)
        twitter = twitterapi(key, secret, token)
        method = getattr(twitter, "friends_timeline")
        result = method()
        res = []
        for item in result:
            try: res.append("%s - %s" % (item.author.screen_name, item.text))
            except Exception, ex: handle_exception()
        ievent.reply("results: ", res) 
    except KeyError: ievent.reply('you are not logged in yet. see the twitter-auth command.')
    except (TweepError, urllib2.HTTPError), e: ievent.reply('twitter failed: %s' % (str(e),))

cmnds.add('twitter-friends', handle_twitterfriends, ['OPER', 'USER', 'GUEST'])
examples.add('twitter-friends', 'show your friends_timeline', 'twitter-friends')
