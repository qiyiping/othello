# -*- coding: utf-8 -*-
from othello import Board
from util import Hash, LRUCache
import numpy as np

class BaseModelScorer(object):
    def __call__(self, board):
        return 0.0

    def update(self, xs, ys):
        pass

    def load(self, path):
        pass

    def save(self, path):
        pass


def _m0(r, c):
    return (r, c)
def _m1(r, c):
    return (r, 7-c)
def _m2(r, c):
    return (c, r)
def _m3(r, c):
    return (c, 7-r)
def _m4(r, c):
    return (7-r, c)
def _m5(r, c):
    return (7-r, 7-c)
def _m6(r, c):
    return (7-c, r)
def _m7(r, c):
    return (7-c, 7-r)

_m = [ _m0, _m1, _m2, _m3, _m4, _m5, _m6, _m7 ]

class ModelScorer(BaseModelScorer):
    def __init__(self, path=None):
        directions = [(0, 1), [1, 1]]
        corners = []
        num_of_weights = 0
        s = set()
        for x, y in directions:
            pt = []
            for r in range(0, 8):
                for c in range(0, 8):
                    r1, c1 = r+x, c+y
                    if r1 < 8 and c1 < 8 and ((r,c),(r1,c1)) not in s and ((r1,c1), (r,c)) not in s:
                        pt.append((r,c))
                        for m in _m:
                            s.add((m(r,c), m(r1,c1)))
            corners.append(pt)
            num_of_weights += len(pt)

        self._weights = np.random.randn(num_of_weights * 9)
        self._patterns = zip(directions, corners)

        self._hash = Hash()
        self._feature_cache = LRUCache(300000)

        if path is not None:
            self.load(path)

    def _feature_extract(self, b):
        h = self._hash(b)
        if self._feature_cache.contains(h):
            return self._feature_cache.get(h)
        feature = np.zeros(len(self._weights))
        idx = 0
        for (x, y), corners in self._patterns:
            for r, c in corners:
                for m in _m:
                    r0,c0 = m(r,c)
                    r1,c1 = m(r+x, c+y)
                    v0 = b[r0][c0]
                    v1 = b[r1][c1]
                    feature[v0*3 + v1 + idx * 9] += 1.0
                idx += 1
        self._feature_cache.put(h, feature)
        return feature

    def __call__(self, board):
        return np.inner(self._feature_extract(board.board), self._weights)

    def _value(self, feature):
        return np.inner(self._weights, feature)

    def update(self, board, y):
        f = self._feature_extract(board.board)
        self._weights += (0.001 * (y - self._value(f)) * f)
        assert np.nan not in self._weights, "\n{}\n{}\n{}".format(self._weights, f, y)
        assert np.nan not in f, "\n{}\n{}\n{}".format(self._weights, f, y)

    def load(self, path):
        self._weights = np.load(path)

    def save(self, path):
        np.save(path, self._weights)

class NaiveScorer(object):
    def __init__(self, role):
        w = np.ones((8,8))*-1
        w[0][0] = 100
        w[0][1] = -20
        w[0][2] = 10
        w[0][3] = 5
        w[0][4] = 5
        w[0][5] = 10
        w[0][6] = -20
        w[0][7] = 100
        w[1][0] = -20
        w[1][1] = -50
        w[1][2] = -2
        w[1][3] = -2
        w[1][4] = -2
        w[1][5] = -2
        w[1][6] = -50
        w[1][7] = -20
        w.T[0:2] = w[0:2]
        w[6] = w[1]
        w[7] = w[0]
        w.T[6:8] = w[6:8]
        self._w = w
        self._role = role

    def __call__(self, board):
        return np.sum(self._w * (board.board == self._role))
