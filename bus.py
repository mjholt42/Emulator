#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""The bus class connects the different classes together"""

import abc


class Bus:

    def __init__(self):
        self.mapping = dict()

    def __getitem__(self, item):
        if not isinstance(item, range):
            for key in self.mapping:
                if item in key:
                    return self.mapping[key][item]
            raise KeyError(item)
        else:
            return self.mapping[item]

    def __setitem__(self, address, data):
        self[address][address] = data

    def register(self, device, min_address, max_address, **kwargs):
        self.mapping[range(min_address, max_address)] = device(min_address, max_address,**kwargs)
