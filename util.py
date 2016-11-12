# -*- coding: utf-8 -*-

import numpy as np
import collections

def epsilon_greedy(epsilon, options, vals, max_player=True):
    r = np.random.rand()
    if r < 1 - epsilon:
        if max_player:
            idx = np.argmax(vals)
        else:
            idx = np.argmin(vals)
    else:
        idx = np.random.randint(low=0, high=len(options))
    return options[idx], vals[idx]

class LRUCache(object):
    def __init__(self, capacity):
        self._cache = collections.OrderedDict()
        self._capacity = capacity

    def contains(self, key):
        return key in self._cache

    def size(self):
        return len(self._cache)

    def get(self, key, default_val = None):
        try:
            v = self._cache.pop(key)
            self._cache[key] = v
        except:
            v = default_val
        return v

    def put(self, key, value):
        try:
            self._cache.pop(key)
        except:
            if len(self._cache) > self._capacity:
                self._cache.popitem(last=False)
        self._cache[key] = value

class Hash(object):
    def __init__(self, positions=64, pieces=2, filename=None):
        self._positions = positions
        self._pieces = pieces
        if filename is None:
            self._table = np.random.randint(0, 2<<60, (positions, pieces))
        else:
            self._table = np.load(filename)
            assert (positions, pieces) == self._table.shape

    def save(self, filename):
        np.save(filename, self._table)

    def __call__(self, board):
        """https://en.wikipedia.org/wiki/Zobrist_hashing
        """
        flatten_board = board.flatten()
        h = 0
        for i,v in enumerate(flatten_board):
            # FIXME: It depends on the way piece value is defined.
            if v != 0:
                h ^= self._table[i][(v+1)/2]
        return h
