#getconf = make_getconf("dateiname.json") 
#getconf(key) -> value                    
#oder error                               

import json

def make_getconf(filename):
    def getconf(prop):
        prop_split = prop.split('.')
        string = ''
        file = open(filename)
        for line in file.readlines():
            string+=line
        parsed = json.loads(string)
        tmp = parsed
        for pr in prop_split:
            tmp = tmp[pr]

        return tmp
    return getconf
