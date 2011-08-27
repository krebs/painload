# jsb/utils/popen.py
#
#

""" popen helper functions. """

## defines

go = False

## basic imports

try:
    from subprocess import Popen, PIPE
    from locking import lockdec
    import thread, StringIO, logging, types
    go = True
except: go = False

if go:

    ## locks

    popenlock = thread.allocate_lock()
    popenlocked = lockdec(popenlock)

    ## exceptions

    class PopenWhitelistError(Exception):

        def __init__(self, item):
            Exception.__init__(self)
            self.item = item
        
        def __str__(self):
            return self.item

    class PopenListError(Exception):

        def __init__(self, item):
            Exception.__init__(self)
            self.item = item
        
        def __str__(self):
            return str(self.item)

    ## GozerStringIO class

    class GozerStringIO(StringIO.StringIO):

        """ provide readlines support on a StringIO object. """

        def readlines(self):
            """ read multiple lines. """
            return self.read().split('\n')

    ## GozerPopen4 class

    class GozerPopen4(Popen):

        """ extend the builtin Popen class with a close method. """

        def __init__(self, args):
            Popen.__init__(self, args, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            self.fromchild = self.stdout
            self.tochild   = self.stdin
            self.errors    = self.stderr

        def close(self):
            """ shutdown. """
            self.wait()
            try: self.stdin.close()
            except: pass
            try: self.stdout.close()
            except: pass
            try: self.errors.close()
            except: pass
            return self.returncode

    ## gozerpopen function

    def gozerpopen(args, userargs=[]):
        """ do the actual popen .. make sure the arguments are passed on as list. """
        if type(args) != types.ListType: raise PopenListError(args)
        if type(userargs) != types.ListType: raise PopenListError(args)
        for i in userargs:
            if i.startswith('-'): raise PopenWhitelistError(i)
        proces = GozerPopen4(args + userargs)
        return proces
