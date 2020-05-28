#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Memory devices are stored here"""

import array


class RAM:

    def __init__(self, minimum_address, maximum_address, startlocation=None, data=None):
        self.offset = minimum_address
        self._data = array.array('B', (0 for _ in range(minimum_address, maximum_address+1)))
        if startlocation and data:
            for idx, val in enumerate(data):
                self._data[(startlocation - self.offset) + idx] = val

    def __getitem__(self, address):
        return self._data[address - self.offset]

    def __setitem__(self, address, data):
        self._data[address - self.offset] = data

    def __iter__(self):
        return iter(self._data)

    def __str__(self):
        return f'RAM [{self.offset:0X}:{self.offset + len(self._data) -1:0X}]'

    def print_contents(self):
        for idx, val in enumerate(self):
            idx = idx + self.offset
            if idx % 0x0010 == 0xF:
                end = "\n"
            else:
                end = "\t"
            print(f'{idx:0X}: {val:0X}', end=end)





