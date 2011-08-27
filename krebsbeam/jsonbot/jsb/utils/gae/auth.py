# jsb/utils/web.py
#
#

""" google auth related functions. """

## jsb imports

from jsb.utils.trace import whichmodule
from jsb.lib.config import getmainconfig

## finduser

def finduser():
    """ try to find the email of the current logged in user. """
    from google.appengine.api import users as gusers
    user = gusers.get_current_user()
    if user: return user.email()
    return "" 

## checkuser

def checkuser(response, request, event=None):
    """
        check for user based on web response. first try google 
        otherwise return 'notath@IP' 

    """
    from google.appengine.api import users as gusers
    userhost = "notauth"
    u = "notauth"
    nick = "notauth"
    user = gusers.get_current_user()
    hostid = request.remote_addr
    if not user:
        try:
            email = request.get('USER_EMAIL')
            if not email: email = "notauth"
            auth_domain = request.get('AUTH_DOMAIN')
            who = request.get('who')
            if not who:who = email
            if auth_domain: userhost = nick = "%s@%s" % (who, auth_domain)
            else: userhost = nick = "%s@%s" % (who, hostid)
        except KeyError: userhost = nick = "notauth@%s" % hostid
    else:
        userhost = user.email() or user.nickname() 
        if not userhost: userhost = nick = "notauth@%s" % hostid
        nick = user.nickname()
        u = userhost
    cfrom = whichmodule()
    if 'jsb' in cfrom: 
        cfrom = whichmodule(1)
        if 'jsb' in cfrom: cfrom = whichmodule(2)
    return (userhost, user, u, nick)
