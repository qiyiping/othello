# -*- coding: utf-8 -*-

import logging

from othello import Board
from util import epsilon_greedy
from value import ModelScorer
from evaluation import evaluate
from database import TextDb

def self_play(n, model, db):
    b = Board()
    for t in xrange(1, n+1):
        b.init_board()
        p = Board.BLACK

        while not b.is_terminal_state():
            options = b.feasible_pos(p)
            vals = []

            if len(options) > 0:
                for i,j in options:
                    with b.flip2(i, j, p):
                        if b.is_terminal_state():
                            vals.append(b.score(Board.BLACK) - b.score(Board.WHITE))
                        else:
                            vals.append(model(b))
                (a0, a1), v = epsilon_greedy(0.03, options, vals, p == Board.BLACK)
                model.update(b, v)
                b.flip(a0, a1, p)

            p = Board.opponent(p)

        if t % 100 == 0:
            logging.info("Number of games played: {}".format(t))
            logging.info(b.cache_status())

        if t % 1000 == 0:
            model.save("./model/model.cpt")

        if t % 5000 == 0:
            n, mse = evaluate(db, model)
            logging.info("Number of Games:{}, MSE: {}".format(n, mse))

    model.save("./model/model.cpt")


if __name__ == '__main__':
    logging.basicConfig(filename='tdl.log',level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

    model = ModelScorer(alpha=0.001, gamma=0.05)

    validate_db = TextDb("./database/validate.small.txt")
    logging.info("Validate database state: {}".format(validate_db.db_stat()))

    self_play(100000, model, validate_db)
