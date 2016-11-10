# -*- coding: utf-8 -*-

import logging

from othello import Board
from util import epsilon_greedy
from value import ModelScorer
# from ai import AlphaBeta


def self_play(n, model):
    for t in xrange(1, n+1):
        b = Board()
        p = Board.BLACK
        while not b.is_terminal_state():
            options = b.feasible_pos(p)
            vals = []
            for i,j in options:
                with b.flip2(i, j, p):
                    vals.append(model(b))
            if len(vals) > 0:
                (a0, a1), v = epsilon_greedy(0.01, options, vals, p == Board.BLACK)
                b.flip(a0, a1, p)
                model.update(b.board, [v])
            p = Board.opponent(p)

        if t % 10 == 0:
            logging.info("number of games played: {}".format(t))

        if t % 1000 == 0:
            model.save("./model/model.cpt")
    model.save("./model/model.cpt")


if __name__ == '__main__':
    logging.basicConfig(filename='tdl.log',level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
    model = ModelScorer()
    self_play(10000, model)
