
import base64, binascii
from twisted.python.filepath import FilePath
from twisted.conch.checkers import SSHPublicKeyDatabase


class PublicKeyChecker(SSHPublicKeyDatabase):

    def __init__(self, filename):
        self.filepath = FilePath(filename)

    def getAuthorizedKeysFiles(self, credentials):
        return [self.filepath]

    def checkKey(self, credentials):
        for line in self.filepath.open():
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                if base64.decodestring(parts[1]) == credentials.blob:
                    return True
            except binascii.Error:
                continue
        return False
