#! /usr/bin/env python

from os import environ as env

authorized_keys_file = env.get('authorized_keys_file', '/dev/null')
services_file = env.get('services_file', '/dev/null')
host_key_file = env.get('host_key_file', '/dev/null')
host_key_pub_file = host_key_file + '.pub'


from checkers import PublicKeyChecker
from twisted.conch.avatar import ConchUser
from twisted.conch.ssh.connection import SSHConnection
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.conch.ssh.session import SSHSession, ISession, wrapProtocol
from twisted.conch.ssh.userauth import SSHUserAuthServer
from twisted.cred.error import UnauthorizedLogin
from twisted.cred.portal import IRealm, Portal
from twisted.internet.protocol import Protocol
from twisted.internet.reactor import listenTCP, run
from twisted.python.components import registerAdapter
from zope.interface import implements

from twisted.python.log import startLogging
from sys import stderr
startLogging(stderr)


class MyRealm:
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        return interfaces[0], MyUser(), lambda: None


class MyUser(ConchUser):
    def __init__(self):
        ConchUser.__init__(self)
        self.channelLookup.update({ 'session': SSHSession })


class MySession:
    
    def __init__(self, avatar):
        pass

    def getPty(self, term, windowSize, attrs):
        pass
    
    def execCommand(self, proto, cmd):
        raise Exception("no executing commands")

    def openShell(self, trans):
        ep = MyProtocol()
        ep.makeConnection(trans)
        trans.makeConnection(wrapProtocol(ep))

    def eofReceived(self):
        pass

    def closed(self):
        pass


registerAdapter(MySession, MyUser, ISession)


def slurpTextfile(filename):
    file = open(filename, 'r')
    try:
        return file.read()
    finally:
        file.close()

class MyProtocol(Protocol):
    def connectionMade(self):
        data = slurpTextfile(services_file).replace('\n', '\r\n')
        self.transport.write(data)
        self.transport.loseConnection()

    #def dataReceived(self, data):
    #    if data == '\r':
    #        data = '\r\n'
    #    elif data == '\x03': #^C
    #        self.transport.loseConnection()
    #        return
    #    self.transport.write(data)


class MyFactory(SSHFactory):
    privateKeys = {
    'ssh-rsa': Key.fromFile(filename=host_key_file)
    }
    publicKeys = {
    'ssh-rsa': Key.fromFile(filename=host_key_pub_file)
    }
    services = {
        'ssh-userauth': SSHUserAuthServer,
        'ssh-connection': SSHConnection
    }

if __name__ == '__main__':
    portal = Portal(MyRealm())
    portal.registerChecker(PublicKeyChecker(authorized_keys_file))
    MyFactory.portal = portal
    listenTCP(1337, MyFactory())
    run()
