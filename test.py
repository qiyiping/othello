# -*- coding: utf-8 -*-
import logging

import numpy as np

from othello import Board, Game
from ai import CmdLineHumanPlayer, SimpleBot, AlphaBeta

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





def main():
    logging.basicConfig(filename='test.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    evaluator = SimpleEvaluator(Board.BLACK)
    bot = SimpleBot(evaluator, 10, Board.BLACK)
    human = CmdLineHumanPlayer(Board.WHITE)
    game = Game(bot, human)
    game.run()

if __name__ == '__main__':
    main()
