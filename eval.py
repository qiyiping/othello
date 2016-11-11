# -*- coding: utf-8 -*-
from database import TextDb
from value import ModelScorer
from othello import Board

import math
import numpy as np

def eval(db_files, model):
    db = TextDb(*db_files)
    directions = [(False, False), (False, True), (True, False), (True, True)]

    s = 0.0
    n = 0.0
    for d1,d2 in directions:
        for moves, result in db.xgames(d1, d2):
            if np.random.rand() > 0.01:
                continue
            b = Board()
            for p, r, c in moves:
                b.flip(r, c, p)
                s += (model(b) - result) * (model(b) - result)
                n += 1.0
    print "Number of Games:{}, MSE: {}".format(n, math.sqrt(s/n))

if __name__ == '__main__':
    model = ModelScorer()
    model.load("/Users/qiyiping/Projects/qiyiping/othello/model/model.cpt-3")
    eval(["./database/WTH.txt"], model)
