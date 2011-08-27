# jsb/utils/web.py
#
#

""" web related functions. """

## jsb imports

from jsb.utils.generic import fromenc
from jsb.version import getversion
from jsb.lib.config import Config, getmainconfig
from jsb.utils.lazydict import LazyDict

## gaelib imports

from auth import finduser

## basic imports

import os
import time
import socket
import urlparse

## create_openid_url

def create_openid_url(continue_url):
    continue_url = urlparse.urljoin(self.request.url, continue_url)
    return "/_ah/login?continue=%s" % urllib.quote(continue_url)

## mini

def demo(response, input={}):
    """ display start html so that bot output can follow. """
    try: host = socket.gethostname()
    except AttributeError:
         if os.environ.get('HTTP_HOST'): host = os.environ['HTTP_HOST']
         else: host = os.environ['SERVER_NAME']
    print host
    if 'localhost' in host:  url = 'http://%s/demo' % host
    else: url = 'https://%s/demo' % host
    template = LazyDict({'url': url, 'version': getversion(), 'host': host, 'color': getmainconfig().color or "#4b7cc6"})
    if input: template.update(input)
    temp = os.path.join(os.getcwd(), 'templates/console.html')
    outstr = template.render(temp)
    response.out.write(outstr)

## start

def start(response, input={}):
    """ display start html so that bot output can follow. """
    try: host = socket.gethostname()
    except AttributeError:
         if os.environ.get('HTTP_HOST'): host = os.environ['HTTP_HOST']
         else: host = os.environ['SERVER_NAME']
    if 'localhost' in host:  url = 'http://%s/dispatch' % host
    else: url = 'https://%s/dispatch' % host
    template = LazyDict({'url': url, 'version': getversion(), 'host': host, 'color': getmainconfig().color or "#4b7cc6"})
    if input: template.update(input)
    temp = os.path.join(os.getcwd(), 'templates/console.html')
    outstr = template.render(temp)
    response.out.write(outstr)

## login

def login(response, input={}):
    """ display start html so that bot output can follow. """
    try: host = socket.gethostname()
    except AttributeError:
         if os.environ.get('HTTP_HOST'): host = os.environ['HTTP_HOST']
         else: host = os.environ['SERVER_NAME']
    if 'localhost' in host:  url = 'http://%s/dispatch' % host
    else: url = 'https://%s/dispatch' % host
    template = LazyDict({'url': url, 'version': getversion(), 'host': host, 'color': getmainconfig().color or "#4b7cc6"})
    if input: template.update(input)
    temp = os.path.join(os.getcwd(), 'templates/login.html')
    outstr = template.render(temp)
    response.out.write(outstr)

## commandbox (testing purposes)

def commandbox(response, url="/dispatch/"):
    """ write html data for the exec box. """
    response.out.write("""
          <form action="%s" method="post">
            <div><b>enter command:</b> <input type="commit" name="content"></div>
          </form>
          """ % url)

## execdbox (testing purposes)

def execbox(response, url="/exec/"):
    """ write html data for the exec box. """
    response.out.write("""
      <form action="" method="GET">
        <b>enter command:</b><input type="commit" name="input" value="">
        // <input type="button" value="go" onClick="makePOSTRequest(this.form)"
      </form>
          """)

## closer

def closer(response):
    """ send closing html .. comes after the bot output. """
    response.out.write('</div><div class="footer">')
    response.out.write('<b>%4f seconds</b></div>' % (time.time() - response.starttime))
    response.out.write('</body></html>')

## loginurl

def loginurl(request, response):
    """ return google login url. """
    from google.appengine.api import users as gusers
    urls = {}
    for p in openIdProviders:
        p_name = p.split('.')[-2]
        p_url = p.lower()
        try:
            url = gusers.create_login_url(federated_identity=p_url)
            if not url: url = create_openid_url(p_url)
        except TypeError: continue
        urls[p_name] = url
    return urls

## logouturl

def logouturl(request, response):
    """ return google login url. """
    from google.appengine.api import users as gusers
    return gusers.create_logout_url("/_ah/login_required")
