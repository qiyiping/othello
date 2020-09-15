# -*- coding: utf-8 -*-
from __future__ import print_function

from database import TextDb
from value import ModelScorer
from othello import Board

import math
import numpy as np

def evaluate(db, models):
    error_sum = [0.0] * len(models)
    n = 0.0
    for moves, result in db.games:
        if np.random.rand() > 0.1:
            continue
        b = Board()
        steps = 0
        for p, r, c in moves:
            steps += 1
            b.flip(r, c, p)
            if steps > 10:
                for i, m in enumerate(models):
                    error = m(b) - result
                    error_sum[i] += error * error
                n += 1.0
    return [ math.sqrt(err/n) for err in error_sum ]

if __name__ == '__main__':
    model1 = ModelScorer()
    model1.load("/Users/qiyiping/Projects/qiyiping/othello/model/model.cpt.npy.6")
    model2 = ModelScorer()
    model2.load("/Users/qiyiping/Projects/qiyiping/othello/model/model.cpt.npy")
    db = TextDb("./database/validate.small.txt")
    res = evaluate(db, [model1, model2])
    for i, mse in enumerate(res):
        print(f"Model Index:{i}, MSE: {mse}")
