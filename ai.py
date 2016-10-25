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

class RandomPlayer(Agent):
    def __init__(self, role, depth=6):
        super(RandomPlayer, self).__init__(role)
        score_evaluator = ScoreEvaluator(role)
        self._final_searcher = AlphaBeta(score_evaluator, depth)
        self._depth = depth

    def play(self, board):
        if board.blanks <= self._depth:
            _, act = self._final_searcher.search(board, self.role)
            return act
        else:
            return self.random_play(board)

    def random_play(self, board):
        p = board.feasible_pos(self.role)
        idx = np.random.randint(0, len(p))
        return p[idx]

class HybirdBot(Agent):
    def __init__(self, role, players, weights):
        super(HybirdBot, self).__init__(role)
        assert len(players) == len(weights)
        for p in players:
            assert p.role == role
        self._players = players
        self._probs = np.zeros(len(players))
        s = sum(weights)
        assert s > 0
        for i,w in enumerate(weights):
            assert w > 0
            self._probs[i] = 1.*w/s

    def play(self, board):
        return self._choose_player().play(board)

    def _choose_player(self):
        r = np.random.rand()
        s = 0.0
        idx = 0
        for i,v in enumerate(self._probs):
            s += v
            if s >= r:
                idx = i
        return self._players[idx]

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



from tdl import OthelloModel

class CmdLineHumanPlayer(Agent):
    def __init__(self, role, help_model_path=None):
        super(CmdLineHumanPlayer, self).__init__(role)
        self._help_model = None
        if help_model_path is not None:
            self._help_model = OthelloModel()
            self._help_model.restore_params(help_model_path)

    def play(self, board):
        pos = board.feasible_pos(self.role)
        p = None
        while True:
            try:
                if self._help_model is not None:
                    scores = []
                    for r,c in pos:
                        with board.flip2(r, c, self.role):
                            stage = board.stage()
                            scores.append(self._help_model.predict([board.board], stage)[0][0])
                    print ", ".join(["%s:%.03f" % (chr(i+ord("A")), scores[i]) for i in range(0, len(pos))])
                l = raw_input("Enter your choise: ").strip().lower()
                if l == "exit":
                    break
                p = pos[ord(l.lower()) - ord("a")]
                break
            except:
                pass
        return p
