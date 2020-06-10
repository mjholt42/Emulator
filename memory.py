#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Memory devices are stored here"""

import array

from bus import BusDevice


class RAM(BusDevice):
    """Emulates an 8bit ram"""

    def __init__(self, bus, size, start_location=0, data=None):
        super().__init__(bus)
        self._data = array.array('B', (0 for _ in range(size)))
        if data:
            for idx, val in enumerate(data):
                address = start_location + idx
                if address > size:
                    raise OverflowError(f'{address:04X} is outside of allowed range')
                self._data[address] = val

    def __getitem__(self, address):
        return self._data[address]

    def __setitem__(self, address, data):
        if (address < 0) or (address > self.size):
            raise IndexError
        self._data[address] = data

    def __iter__(self):
        return iter(self._data)

    def __str__(self):
        return f'{self.__class__} [size = {self.size:d}]'

    @property
    def size(self):
        return len(self._data)

    @property
    def absolute_address(self):
        return False

    def print_contents(self, offset=0):
        """Lists the contents of the RAM"""
        for idx, val in enumerate(self):
            idx = idx + offset
            if idx % 0x0010 == 0xF:
                end = "\n"
            else:
                end = "\t"
            print(f'{idx:0X}: {val:0X}', end=end)

    def load_from_file(self, file, start_index=0):
        """Load the ram from a binary file"""
        with open(file, 'rb') as fid:
            data = fid.read()
        index = start_index
        for byte in data:
            self._data[index] = byte  # Cannot use __setitem__ to let ROM load from file
            index += 1


class ROM(RAM):
    """ROM class. Same as ram but with write disabled"""

    def __setitem__(self, address, data):
        raise TypeError(f"'{self.__class__}' object does not support item assignment")
