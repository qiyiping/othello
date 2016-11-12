# -*- coding: utf-8 -*-
import numpy as np
from contextlib import contextmanager
import sys
import traceback
from util import Hash, LRUCache

class Board(object):
    BLANK = 0
    BLACK = 1
    WHITE = -1
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
        self.init_board()
        self._feasible_pos_cache = LRUCache(200000)
        self._board_state_cache = LRUCache(2500000)
        self._hash = Hash()

    def init_board(self):
        self._board = np.zeros((self._size, self._size), dtype=np.int)
        i = self._size / 2
        self._board[i-1][i-1] = Board.WHITE
        self._board[i-1][i] = Board.BLACK
        self._board[i][i] = Board.WHITE
        self._board[i][i-1] = Board.BLACK

    def cache_status(self):
        return "position cache: {}, state cache: {}".format(self._feasible_pos_cache.size(),
                                                            self._board_state_cache.size())

    def feasible_pos(self, player, enable_cache=True):
        h = self._hash(self._board) + player
        if enable_cache and self._feasible_pos_cache.contains(h):
            return self._feasible_pos_cache.get(h)

        pos = []
        xs, ys = np.where(self._board == Board.BLANK)
        for i,j in zip(xs, ys):
            if self.is_feasible(i, j, player):
                pos.append((i, j))

        self._feasible_pos_cache.put(h, pos)
        return pos

    def is_terminal_state(self):
        h = self._hash(self._board)
        if self._board_state_cache.contains(h):
            return self._board_state_cache.get(h)

        xs, ys = np.where(self._board == Board.BLANK)
        for i,j in zip(xs, ys):
            for di, dj in Board.DIRECTIONS:
                black, white = False, False
                for d in range(1, self._size):
                    ii = i + di * d
                    jj = j + dj * d
                    if not (ii < self._size and ii >= 0 and jj < self._size and jj >= 0):
                        break
                    piece = self._board[ii][jj]
                    if piece == Board.BLANK:
                        break
                    if piece == Board.WHITE:
                        white = True
                    else:
                        black = True
                    if black and white:
                        self._board_state_cache.put(h, False)
                        return False

        self._board_state_cache.put(h, True)
        return True

    def flip(self, i, j, player):
        assert self._board[i][j] == Board.BLANK
        cnt = 0
        for di, dj in Board.DIRECTIONS:
            for d in range(1, self._size):
                ii = i + di * d
                jj = j + dj * d
                if not (ii < self._size and ii >= 0 and jj < self._size and jj >= 0):
                    break
                if self._board[ii][jj] == Board.BLANK:
                    break
                if self._board[ii][jj] == player:
                    for x in range(1, d):
                        self._board[i+di*x][j+dj*x] = player
                        cnt += 1
                    break
        assert cnt > 0
        self._board[i][j] = player

    @contextmanager
    def flip2(self, i, j, player):
        backup = self._board.copy()
        self.flip(i, j, player)
        yield self
        self._board = backup

    def score(self, player):
        return np.sum(self._board == player)


    @classmethod
    def _wins(cls, b, player):
        s1 = np.sum(b == player)
        s2 = np.sum(b == Board.opponent(player))
        return s1 > s2

    def wins(self, player):
        s1 = self.score(player)
        s2 = self.score(Board.opponent(player))
        return s1 > s2

    @property
    def blanks(self):
        return np.sum(self.board == Board.BLANK)

    def __str__(self):
        return str(self._board)

    def __repr__(self):
        return str(self._board)

    @property
    def board(self):
        return self._board

    # NUMBER_OF_STAGES = 11

    # def stage(self):
    #     return self.blanks // 6

    # @classmethod
    # def _stage(cls, bd):
    #     return np.sum(bd == Board.BLANK) // 6

    @property
    def size(self):
        return self._size

    def is_feasible(self, i, j, player):
        cnt = 0
        for di, dj in Board.DIRECTIONS:
            for d in range(1, self._size):
                ii = i + di * d
                jj = j + dj * d
                if not (ii < self._size and ii >= 0 and jj < self._size and jj >= 0):
                    break
                if self._board[ii][jj] == Board.BLANK:
                    break
                if self._board[ii][jj] == player:
                    cnt += (d-1)
                    break
        return cnt > 0

    def _is_valid_pos(self, i, j):
        return (i < self._size and i >= 0 and j < self._size and j >= 0)

    def _cmd_symbol(self, i, j):
        if self._board[i][j] == Board.BLANK:
            return '-'
        elif self._board[i][j] == Board.BLACK:
            return "*"
        else:
            return "o"

    def print_for_player(self, player):
        prt = sys.stdout.write

        if player not in (Board.BLACK, Board.WHITE):
            pos = []
        else:
            pos = self.feasible_pos(player)

        rows, columns = self.board.shape
        for i in range(0, rows):
            for j in range(0, columns):
                try:
                    idx = pos.index((i,j))
                    prt(chr(ord("A") + idx))
                except:
                    prt(self._cmd_symbol(i, j))
                prt(" ")
            prt("\n")
        prt("\nBlack score: {0}, White score: {1}\n".format(self.score(Board.BLACK),
                                                            self.score(Board.WHITE)))
        sys.stdout.flush()

class Game(object):
    def __init__(self, black_player, white_player, verbose=0):
        assert black_player.role == Board.BLACK
        assert white_player.role == Board.WHITE
        self._players = [black_player, white_player]
        self._verbose = verbose
        self._black_wins = 0
        self._white_wins = 0
        self._ties = 0

    def game_stat(self):
        return self._black_wins, self._white_wins, self._ties

    def run(self):
        board = Board()
        turn = 0

        for p in self._players:
            p.begin_of_game(board)


        while not board.is_terminal_state():
            pos = board.feasible_pos(self._players[turn].role)
            if len(pos) > 0:
                if self._verbose > 1:
                    board.print_for_player(self._players[turn].role)
                try:
                    i,j = self._players[turn].play(board)
                    board.flip(i, j, self._players[turn].role)
                    idx = pos.index((i,j))
                    if self._verbose > 1:
                        print "player {0}: {1}".format(self._players[turn].role, chr(ord("A") + idx))
                except:
                    if self._verbose > 0:
                        print "player {0} failed".format(self._players[turn].role)
                        print "-"*60
                        traceback.print_exc()
                        print "-"*60
                    break
            turn = (turn+1) % 2

        for p in self._players:
            p.end_of_game(board)

        if self._verbose > 1:
            print '-'*60
            print 'final result'
            print '-'*60
            board.print_for_player(Board.BLANK)
            print '-'*60

        black_score = board.score(Board.BLACK)
        white_score = board.score(Board.WHITE)
        if black_score > white_score:
            self._black_wins += 1
        elif white_score > black_score:
            self._white_wins += 1
        else:
            self._ties += 1
