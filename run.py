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

def save_model(player):
    if type(player) is TDLAgent:
        ts = int(time.time())
        player.save_model("./model/{0}_{1}.ckpt".format(tdl_agent.role, ts))

def tell_game_stat(game, i):
    b,w,t = game.game_stat()
    print "total games: {0}, black wins: {1} {2}, white wins: {3} {4}, ties: {5}".format(i, b, 1.*b/i, w, 1.*w/i, t)

def load_player(player_type, role, **kwags):
    if player_type == "SimpleBot":
        evaluator = SimpleEvaluator(role)
        depth = kwags.get("depth", 3)
        player = SimpleBot(evaluator, depth, role)
    elif player_type == "TDLAgent":
        update = kwags.get("update")
        alpha = kwags.get("alpha")
        epsilon = kwags.get("epsilon")
        model_file = kwags.get("model_file")
        player = TDLAgent(role=role, update=update, alpha=alpha, epsilon=epsilon, model_file=model_file)
    elif player_type == "HumanCmdLine":
        player = human = CmdLineHumanPlayer(role)
    else:
        raise Exception("Unknown player type:{0}".format(player_type))
    return player

def self_play(update, alpha, epsilon, model_file, games, verbose, black_type, white_type):
    black_player = load_player(black_type, Board.BLACK, depth=3, update=update, alpha=alpha, epsilon=epsilon, model_file=model_file)
    white_player = load_player(white_type, Board.WHITE, depth=3, update=update, alpha=alpha, epsilon=epsilon, model_file=model_file)
    game = Game(black_player, white_player, verbose)
    for i in range(0, games):
        game.run()
        if i % 100 == 0 and i > 0:
            save_model(white_player)
            save_model(black_player)
            tell_game_stat(game, i)
    save_model(white_player)
    save_model(black_player)
    tell_game_stat(game, i)

def replay(times, game_book, checkpoint):
    r = Replay(game_book)
    processor = TDLProcessor(Board.WHITE, checkpoint)
    r.replay(processor, times)

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="run.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--replay", default=False, action="store_true", help="replay log book")
    parser.add_argument("--times", default=1, type=int, help="times to replay the log book")
    parser.add_argument("--book", default="./database/skatgame/logbook.gam.gz", help="log book")
    parser.add_argument("--checkpoint", default="./model/logbook.ckpt", help="checkpoint file")
    parser.add_argument("--play", default=False, action="store_true", help="play games")
    player_candidates = ["SimpleBot", "TDLAgent", "HumanCmdLine"]
    parser.add_argument("--black", default="SimpleBot", choices=player_candidates, help="black player")
    parser.add_argument("--white", default="TDLAgent", choices=player_candidates, help="white player")
    parser.add_argument("--verbose", default=1, type=int, help="verbose level")
    parser.add_argument("--update", action="store_true", help="whether to update model")
    parser.add_argument("--alpha", default=1.0, type=float, help="alpha")
    parser.add_argument("--epsilon", default=0.01, type=float, help="e-greedy")
    parser.add_argument("--model", default="./model/logbook.ckpt", help="model file")
    parser.add_argument("--games", default=10000, type=int, help="number of games to play")
    args = parser.parse_args()
    print args
    if args.play:
        self_play(args.update, args.alpha, args.epsilon, args.model, args.games, args.verbose, args.black, args.white)
    if args.replay:
        replay(args.times, args.book, args.checkpoint)
