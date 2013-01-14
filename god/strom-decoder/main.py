#! /usr/bin/python
# -*- coding utf-8 -*-

from __future__ import division

import re


class Reader(object):
    _re = re.compile(r'^(?P<field>\d-\d:\d+\.\d+\.\d+\*\d+)\((?P<value>\S+?)(?:\*[VAW])?\)$')

    def _convert_periode(value):
        return int(value, 16) / 100

    fields = {
            '1-0:1.8.0*255': ('overall', float),
            '1-0:31.7.0*255': ('l1_strom', float),
            '1-0:32.7.0*255': ('l1_spannung', float),
            '1-0:51.7.0*255': ('l2_strom', float),
            '1-0:52.7.0*255': ('l2_spannung', float),
            '1-0:71.7.0*255': ('l3_strom', float),
            '1-0:72.7.0*255': ('l3_spannung', float),
            '1-0:96.50.0*1': ('periode', _convert_periode),
    }

    def __init__(self, f):
        self._file = f

    def __iter__(self):
        data = {}
        for line in self._file:
            line = line.strip()
            if line == '!':
                yield data
                data = {}
                continue
            r = self._re.match(line)
            if not r:
                continue
            field = self.fields.get(r.group('field'))
            if field:
                data[field[0]] = field[1](r.group('value'))
            #uncomment to print unmapped values
            #else:
            #    print r.groups()

        
data_file = open('testdata')
for data in Reader(data_file):
    print data
