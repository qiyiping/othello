# -*- coding: utf-8 -*-
import numpy as np
from contextlib import contextmanager
import sys
import traceback

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
        self._board = np.zeros((size, size), dtype=np.int)
        i = size / 2
        self._board[i-1][i-1] = Board.WHITE
        self._board[i-1][i] = Board.BLACK
        self._board[i][i] = Board.WHITE
        self._board[i][i-1] = Board.BLACK

    def feasible_pos(self, player):
        pos = []
        sz = self.size
        for i in range(0, sz):
            for j in range(0, sz):
                if self.is_feasible(i, j, player):
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

    @property
    def size(self):
        return self._size


    def is_feasible(self, i, j, player):
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

class Replay(object):
    def __init__(self, database):
        self._database = database

    def _replay_once(self, processor, d1, d2):
        for moves, result in self._database.xgames(d1, d2):
            board = Board()
            for player,i,j in moves:
                processor(player, i, j, result, board)
                board.flip(i, j, player)
            processor.after_one_game()
        processor.after_one_replay()

    def replay(self, processor, times=1):
        for _ in range(0, times):
            self._replay_once(processor, False, False)
            self._replay_once(processor, True, False)
            self._replay_once(processor, False, True)
            self._replay_once(processor, True, True)

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

        if self._verbose > 1:
            print '-'*60
            print 'final result'
            print '-'*60
            board.print_for_player(Board.BLANK)
            print '-'*60

        for p in self._players:
            p.tell_result(board)

        black_score = board.score(Board.BLACK)
        white_score = board.score(Board.WHITE)
        if black_score > white_score:
            self._black_wins += 1
        elif white_score > black_score:
            self._white_wins += 1
        else:
            self._ties += 1
