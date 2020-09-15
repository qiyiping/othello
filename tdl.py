# -*- coding: utf-8 -*-

import logging

from othello import Board
from util import epsilon_greedy
from value import ModelScorer
from ai import Bot

def self_play(n, model):
    b = Board()
    black_bot = Bot(model, 4, 6, Board.BLACK)
    white_bot = Bot(model, 4, 6, Board.WHITE)
    eplison = 0.2

    for t in range(1, n+1):
        b.init_board()
        p = Board.BLACK

        while not b.is_terminal_state():
            options = b.feasible_pos(p)
            vals = []

            if len(options) > 0:
                if p == Board.BLACK:
                    gr, (ga0, ga1) = black_bot._play(b)
                else:
                    gr, (ga0, ga1) = white_bot._play(b)
                    gr = -gr
                print(f"{p}: val = {gr}, action = {ga0}, {ga1}")
                for i,j in options:
                    with b.flip2(i, j, p):
                        if b.is_terminal_state():
                            vals.append(b.score(Board.BLACK) - b.score(Board.WHITE))
                        else:
                            vals.append(model(b))
                print(f"options: {options}, vals: {vals}")
                (a0, a1), v = epsilon_greedy(eplison, options, vals, (ga0, ga1), gr)
                model.update(b, v)
                b.flip(a0, a1, p)

            p = Board.opponent(p)

        if t % 100 == 0:
            logging.info("Number of games played: {}".format(t))
            model.save("./model/model.cpt.npy")

    model.save("./model/model.cpt.npy")


if __name__ == '__main__':
    logging.basicConfig(filename='tdl.log',level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

    model = ModelScorer(learning_rate=0.005, gamma=0.001)
    model.load("./model/model.cpt.npy.6")

    self_play(700000, model)
