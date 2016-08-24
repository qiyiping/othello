# -*- coding: utf-8 -*-
import logging

import numpy as np

from othello import Board, Game, Replay
from ai import CmdLineHumanPlayer, SimpleBot, AlphaBeta
from tdl import TDLAgent, TDLProcessor
import time

class SimpleEvaluator(object):
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


import sys

def self_play():
    evaluator = SimpleEvaluator(Board.BLACK)
    bot = SimpleBot(evaluator, 3, Board.BLACK)
    # human = CmdLineHumanPlayer(Board.WHITE)
    tdl_agent = TDLAgent(role=Board.WHITE, update=True, alpha=1.0, epsilon=0.3)
    game = Game(bot, tdl_agent, 1)
    for i in range(1, 10001):
        game.run()
        if i % 100 == 0:
            ts = int(time.time())
            tdl_agent.save_model("./model/{0}_{1}_{2}.ckpt".format(tdl_agent.role, i, ts))
            b,w,t = game.game_stat()
            print "total games: {0}, black wins: {1} {2}, white wins: {3} {4}, ties: {5}".format(i, b, 1.*b/i, w, 1.*w/i, t)


def replay():
    r = Replay("./database/skatgame/logbook.gam.gz")
    processor = TDLProcessor(Board.WHITE)
    r.replay(processor)
    processor.save_model("./model/logbook.ckpt")

if __name__ == '__main__':
    replay()
