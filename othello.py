# -*- coding: utf-8 -*-
import numpy as np
from contextlib import contextmanager
import sys

class Board(object):
    BLANK = 0
    BLACK = 1
    WHITE = 2
    DIRECTIONS = [(1, 0), (-1, 0),
                  (0, 1), (0, -1),
                  (1, 1), (-1, -1),
                  (-1, 1), (1, -1)]
    @classmethod
    def opponent(cls, player):
        if player == cls.BLACK:
            return cls.WHITE
        else:
            return cls.BLACK

    def __init__(self, size=8):
        assert size % 2 == 0
        self._size = size
        self.reset()

    def reset(self):
        self._board = np.zeros((self._size, self._size), dtype=np.int)
        i = self._size / 2
        self._board[i-1][i-1] = Board.WHITE
        self._board[i-1][i] = Board.BLACK
        self._board[i][i] = Board.WHITE
        self._board[i][i-1] = Board.BLACK

    def feasible_pos(self, player):
        pos = []
        sz = self.size
        for i in range(0, sz):
            for j in range(0, sz):
                if self._is_feasible(i, j, player):
                    pos.append((i, j))
        return pos

    def is_terminal_state(self):
        return len(self.feasible_pos(Board.BLACK)) == 0 and len(self.feasible_pos(Board.WHITE)) == 0

    def flip(self, i, j, player):
        self._board[i][j] = player
        for di, dj in Board.DIRECTIONS:
            for d in range(1, self.size):
                ii = i + di * d
                jj = j + dj * d
                if not self._is_valid_pos(ii, jj):
                    break
                if self._board[ii][jj] == Board.BLANK:
                    break
                if self._board[ii][jj] == player:
                    for x in range(1, d):
                        self._board[i+di*x][j+dj*x] = player
                    break

    @contextmanager
    def flip2(self, i, j, player):
        backup = self._board.copy()
        self.flip(i, j, player)
        yield self
        self._board = backup

    def score(self, player):
        return np.sum(self._board == player)

    def __str__(self):
        return str(self._board)

    def __repr__(self):
        return str(self._board)

    @property
    def board(self):
        return self._board

    @property
    def size(self):
        return self._size


    def _is_feasible(self, i, j, player):
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
                if self._board[ii][jj] == player:
                    cnt += (d-1)
                    break
        return cnt > 0

    def _is_valid_pos(self, i, j):
        return (i < self.size and i >= 0 and j < self.size and j >= 0)

    def print_for_player(self, player):
        prt = sys.stdout.write
        pos = self.feasible_pos(player)
        rows, columns = self.board.shape
        for i in range(0, rows):
            for j in range(0, columns):
                try:
                    idx = pos.index((i,j))
                    prt(chr(ord("A") + idx))
                except:
                    prt(str(self.board[i][j]))
                prt(" ")
            prt("\n")
        prt("\nBlack score: {0}, White score: {1}\n".format(self.score(Board.BLACK), self.score(Board.WHITE)))
        sys.stdout.flush()

class Game(object):
    def __init__(self, black_player, white_player):
        black_player.role = Board.BLACK
        white_player.role = Board.WHITE
        self._players = [black_player, white_player]

    def run(self):
        board = Board()
        turn = 0
        while not board.is_terminal_state():
            if len(board.feasible_pos(self._players[turn].role)) == 0:
                turn = (turn+1) % 2
            board.print_for_player(self._players[turn].role)
            try:
                i,j = self._players[turn].play(board)
                board.flip(i, j, self._players[turn].role)
                turn = (turn+1) % 2
            except:
                print "player {0} failed".format(self._players[turn].role)
                break
