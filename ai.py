# -*- coding: utf-8 -*-

import numpy as np

from othello import Board
from util import Hash

import sys
import logging

class AlphaBeta(object):
    MAX_VAL = float("inf")
    MIN_VAL = float("-inf")
    def __init__(self, evaluator, depth):
        """https://en.wikipedia.org/wiki/Alpha-beta_pruning
        http://web.cs.ucla.edu/~rosen/161/notes/alphabeta.html
        """
        self._evaluator = evaluator
        self._depth = depth

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, val):
        self._depth = val

    def search(self, board, player):
        alpha = AlphaBeta.MIN_VAL
        beta = AlphaBeta.MAX_VAL
        return self._alpha_beta_search(board, player,
                                       alpha, beta,
                                       self._depth, True)

    def _alpha_beta_search(self, board, player, alpha, beta, depth, is_maximizing_player):
        if board.is_terminal_state() or depth == 0:
            return self._evaluator(board), None

        act = None
        if is_maximizing_player:
            r = AlphaBeta.MIN_VAL
        else:
            r = AlphaBeta.MAX_VAL

        actions = board.feasible_pos(player)
        opponent = Board.opponent(player)
        if len(actions) > 0:
            for i,j in actions:
                with board.flip2(i, j, player):
                    v, _ = self._alpha_beta_search(board, opponent,
                                                   alpha, beta,
                                                   depth-1, not is_maximizing_player)
                if is_maximizing_player:
                    if r < v:
                        act = (i, j)
                    alpha = max(v, alpha)
                    r = max(r, v)
                else:
                    if r > v:
                        act = (i, j)
                    beta = min(v, beta)
                    r = min(r, v)

                if alpha >= beta:
                    break
        else:
            r, _ = self._alpha_beta_search(board, opponent,
                                           alpha, beta,
                                           depth, not is_maximizing_player)
        return r, act


class ScoreEvaluator(object):
    def __init__(self, role):
        self._role = role
    def __call__(self, board):
        return board.score(self._role)

class Agent(object):
    def __init__(self, role):
        self._role = role

    def play(self, board):
        pass

    def begin_of_game(self, board):
        pass

    def end_of_game(self, board):
        pass

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value):
        self._role = value

class SimpleBot(Agent):
    def __init__(self, evaluator, depth, role):
        super(SimpleBot, self).__init__(role)
        self._one_step_searcher = AlphaBeta(evaluator, 1)
        score_evaluator = ScoreEvaluator(role)
        self._final_searcher = AlphaBeta(score_evaluator, depth)
        self._depth = depth

    def play(self, board):
        if board.blanks <= self._depth:
            _, action = self._final_searcher.search(board, self.role)
        else:
            _, action = self._one_step_searcher.search(board, self.role)
        return action



class CmdLineHumanPlayer(Agent):
    def __init__(self, role):
        super(CmdLineHumanPlayer, self).__init__(role)

    def play(self, board):
        pos = board.feasible_pos(self.role)
        p = None
        while True:
            try:
                l = raw_input("Enter your choise: ").strip().lower()
                if l == "exit":
                    break
                p = pos[ord(l.lower()) - ord("a")]
                break
            except:
                pass
        return p
