#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np


class Board(object):
    WHITE = 1
    BLACK = -1
    BLANK = 0
    DIRECTIONS = [(1, 0), (-1, 0),
                  (0, 1), (0, -1),
                  (1, 1), (-1, -1),
                  (-1, 1), (1, -1)]

    def __init__(self, size=8):
        assert size % 2 == 0
        self._board = np.zeros((size, size), dtype=np.int)
        i = size / 2
        self._board[i-1][i-1] = Board.WHITE
        self._board[i-1][i] = Board.BLACK
        self._board[i][i] = Board.WHITE
        self._board[i][i-1] = Board.BLACK

    def feasible_pos(self, color):
        pos = []
        sz = self.size
        for i in range(0, sz):
            for j in range(0, sz):
                if self._is_feasible(i, j, color):
                    pos.append((i, j))
        return pos

    def flip(self, i, j, color):
        self._board[i][j] = color
        for di, dj in Board.DIRECTIONS:
            for d in range(1, self.size):
                ii = i + di * d
                jj = j + dj * d
                if not self._is_valid_pos(ii, jj):
                    break
                if self._board[ii][jj] == Board.BLANK:
                    break
                if self._board[ii][jj] == color:
                    for x in range(1, d):
                        self._board[i+di*x][j+dj*x] = color
                    break

    def score(self, color):
        return np.sum(self._board == color)

    @property
    def board(self):
        return self._board

    @property
    def size(self):
        return self._board.shape[0]


    def _is_feasible(self, i, j, color):
        if self._board[i][j] != Board.BLANK:
            return False
        cnt = 0
        for di, dj in Board.DIRECTIONS:
            for d in range(1, self.size):
                ii = i + di * d
                jj = j + dj * d
                if not self._is_valid_pos(ii, jj):
                    break
                if self._board[ii][jj] == Board.BLANK:
                    break
                if self._board[ii][jj] == color:
                    cnt += (d-1)
                    break
        return cnt > 0

    def _is_valid_pos(self, i, j):
        return (i < self.size and i >= 0 and j < self.size and j >= 0)
