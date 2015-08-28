import sys
from setuptools import setup

setup(
    name='Reaktor',
    version='0.2.3',

    description='an IRC bot based on asyn* libs',
    long_description=open("README.md").read(),
    license='WTFPL',
    url='http://localhost/',
    download_url='http://localhost/',

    author='krebs',
    author_email='spam@krebsco.de',

    packages=['reaktor'],
    # optional non-python Deps:
    #   whatweb in path for 'whatweb'
    #   dnsrecon.py for 'dns
    #   host  for 'taken'
    #   whois for 'whois'
    #   git for 'nag'
    entry_points={
        'console_scripts' : [
            'reaktor = reaktor.core:main'
            ]
        },

    install_requires= [ ],
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)

