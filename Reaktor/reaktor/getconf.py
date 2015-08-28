#getconf = make_getconf("dateiname.json")
#getconf(key) -> value
#oder error

import imp
import os


def make_getconf(filename):
    def getconf(prop, default_value=None):
        prop_split = prop.split('.')
        string = ''
        config = load_config(filename)
        #imp.reload(config)
        tmp = config.__dict__
        for pr in prop_split:
            if pr in tmp:
                tmp = tmp[pr]
            else:
                return default_value
        return tmp

    return getconf


def load_config(filename):
    dirname = os.path.dirname(filename)
    modname, ext = os.path.splitext(os.path.basename(filename))
    file, pathname, description = imp.find_module(modname, [ dirname ])
    try:
        ret = imp.load_module(modname, file, pathname, description)
    finally:
        if file: file.close()
    return ret
