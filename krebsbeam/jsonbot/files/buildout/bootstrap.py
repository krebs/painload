"""Bootstraps the TyphoonAE environment.

Simply run this script in a directory containing a buildout.cfg.
The script accepts buildout command-line options, so you can
use the -c option to specify an alternate configuration file.
"""

import os
import shutil
import sys
import tempfile
import urllib2

tmpeggs = tempfile.mkdtemp()

#try:
#    import pkg_resources
#except ImportError:
if True:
    ez = {}
    exec urllib2.urlopen('http://peak.telecommunity.com/dist/ez_setup.py'
                         ).read() in ez
    ez['use_setuptools'](to_dir=tmpeggs, download_delay=0, version="0.6c9")

    import pkg_resources

cmd = 'from setuptools.command.easy_install import main; main()'
ws  = pkg_resources.working_set

if len(sys.argv) > 2 and sys.argv[1] == '--version':
    VERSION = '==%s' % sys.argv[2]
    args = sys.argv[3:] + ['bootstrap']
else:
    VERSION = ''
    args = sys.argv[1:] + ['bootstrap']

assert os.spawnle(
    os.P_WAIT, sys.executable, sys.executable,
    '-c', cmd, '-mqNxd', tmpeggs, 'zc.buildout' + VERSION,
    dict(os.environ,
        PYTHONPATH=
        ws.find(pkg_resources.Requirement.parse('setuptools')).location
        ),
    ) == 0

ws.add_entry(tmpeggs)
ws.require('zc.buildout' + VERSION)
import zc.buildout.buildout
zc.buildout.buildout.main(args)
shutil.rmtree(tmpeggs)

if not os.path.isdir('var'):
    os.makedirs(os.path.join('var', 'log'))
