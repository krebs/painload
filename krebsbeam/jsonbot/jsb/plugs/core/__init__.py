# jsb basic plugins
#
#

""" register all .py files """

import os

(f, tail) = os.path.split(__file__)
__all__ = []

for i in os.listdir(f):
    if i.endswith('.py'):
        __all__.append(i[:-3])
    elif os.path.isdir(f + os.sep + i) and not i.startswith('.'):
        __all__.append(i)

try:
    __all__.remove('__init__')
except:
    pass

__plugs__ = __all__
