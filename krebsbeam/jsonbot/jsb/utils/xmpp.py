# jsb/utils/xmpp.py
#
#

""" XMPP related helper functions. """

def stripped(userhost):
    """ strip resource from userhost. """
    return userhost.split('/')[0]

def resource(userhost):
    """ return resource of userhost. """
    try: return userhost.split('/')[1]
    except ValueError: return ""
