#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""The bus class connects the different classes together"""

import abc


class Bus:
    """Basic bus class with interrupt support"""

    def __init__(self):
        self.mapping = dict()
        self.cpu = None

    def __getitem__(self, address):
        if not isinstance(address, range):
            for key in self.mapping:
                if address in key:
                    mapping, offset = self.mapping[key]
                    return mapping[address - offset]
            raise IndexError(address)
        else:
            return self.mapping[address]

    def __setitem__(self, address, data):
        if not isinstance(address, range):
            for key in self.mapping:
                if address in key:
                    mapping, offset = self.mapping[key]
                    mapping[address - offset] = data
                    return
            raise IndexError(address)
        else:
            self.mapping[address] = data

    def register(self, device, min_address):
        if device.absolute_address:
            offset = min_address
        else:
            offset = 0
        self.mapping[range(min_address, min_address + device.size)] = (device, offset)

    def irq(self):
        if self.cpu:
            self.cpu.irq()

    def nmi(self):
        if self.cpu:
            self.cpu.nmi()


class BusDevice(abc.ABC):
    """Abstract base class for bus devices"""

    def __init__(self, bus):
        self.bus = bus

    @property
    @abc.abstractmethod
    def size(self):
        pass

    @property
    @abc.abstractmethod
    def absolute_address(self):
        pass

    def irq(self):
        self.bus.irq()

    def nmi(self):
        self.bus.nmi()
