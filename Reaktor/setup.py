import sys
from setuptools import setup
import reaktor

setup(
    name='Reaktor',
    version=reaktor.__version__,

    description='an IRC bot based on asyn* libs',
    long_description=open("README.md").read(),
    license='WTFPL',
    url='http://krebsco.de/',
    download_url='https://pypi.python.org/pypi/Reaktor/',

    author='krebs',
    author_email='spam@krebsco.de',
    install_requires = [ 'docopt' ],
    extras_require = {
        # 'all-plugins' : ['dnsrecon']  < not yet in pypi
        },

    packages=['reaktor'],
    # optional non-python Deps:
    #   whatweb in path for 'whatweb'
    #   dnsrecon.py for 'dns
    #   host  for 'taken'
    #   whois for 'whois'
    #   git for 'nag'
    package_data = {'reaktor' : ['commands/*'] },
    entry_points={
        'console_scripts' : [
            'reaktor = reaktor.core:main'
            ]
        },

    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)

