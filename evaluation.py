# -*- coding: utf-8 -*-
from __future__ import print_function

from database import TextDb
from value import ModelScorer
from othello import Board

import math
import numpy as np

def evaluate(db, model):
    s = 0.0
    n = 0.0
    for moves, result in db.games:
        if np.random.rand() > 0.1:
            continue
        b = Board()
        for p, r, c in moves:
            b.flip(r, c, p)
            s += (model(b) - result) * (model(b) - result)
            n += 1.0
    return (n, math.sqrt(s/n))

if __name__ == '__main__':
    model = ModelScorer()
    model.load("/Users/qiyiping/Projects/qiyiping/othello/model/model.cpt.npy")
    db = TextDb("./database/validate.small.txt")
    n, mse = evaluate(db, model)
    print("Number of Games:{}, MSE: {}".format(n, mse))
