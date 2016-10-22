# -*- coding: utf-8 -*-
import logging

import numpy as np
import ConfigParser

from othello import Board, Game
from ai import CmdLineHumanPlayer, SimpleBot, AlphaBeta, RandomPlayer
from tdl import TDLAgent
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
        tp = "WHITE"
        if player.role == Board.BLACK:
            tp = "BLACK"
        player.save_model("./model/{0}_{1}.ckpt".format(tp, ts))

def tell_game_stat(game, i):
    b,w,t = game.game_stat()
    print "total games: {0}, black wins: {1} {2}, white wins: {3} {4}, ties: {5}".format(i, b, 1.*b/i, w, 1.*w/i, t)

class Config(object):
    def __init__(self, filename):
        self._config = ConfigParser.ConfigParser()
        self._config.read(args.player_conf)

    def print_config(self):
        sections = self._config.sections()
        for s in sections:
            print s
            for k,v in self._config.items(s):
                print "\t", k, v

    def get_as_str(self, section, option, default=None):
        try:
            return self._config.get(section, option)
        except:
            return default

    def get_as_int(self, section, option, default=None):
        try:
            return self._config.getint(section, option)
        except:
            return default

    def get_as_float(self, section, option, default=None):
        try:
            return self._config.getfloat(section, option)
        except:
            return default

    def get_as_boolean(self, section, option, default=None):
        try:
            return self._config.getboolean(section, option)
        except:
            return default

def load_player(role, player_config):
    if role == Board.BLACK:
        section = "Black"
    else:
        section = "White"
    player_type = player_config.get_as_str(section, "type")
    if player_type == "SimpleBot":
        evaluator = SimpleEvaluator(role)
        depth = player_config.get_as_int(section, "depth", 3)
        player = SimpleBot(evaluator, depth, role)
    elif player_type == "TDLAgent":
        update = player_config.get_as_boolean(section, "update", False)
        alpha = player_config.get_as_float(section, "alpha", 1.0)
        epsilon = player_config.get_as_float(section, "epsilon", 0.01)
        model_file = player_config.get_as_str(section, "model", None)
        explore = player_config.get_as_str(section, "explore", None)
        temperature = player_config.get_as_float(section, "temperature", 0.1)
        player = TDLAgent(role=role, update=update, alpha=alpha, epsilon=epsilon,
                          model_file=model_file, temperature=temperature, explore_method=explore)
    elif player_type == "HumanCmdLine":
        help_model_path = player_config.get_as_str(section, "help_model")
        player = CmdLineHumanPlayer(role, help_model_path=help_model_path)
    elif player_type == "RandomPlayer":
        player = RandomPlayer(role)
    else:
        raise Exception("Unknown player type:{0}".format(player_type))
    return player

def self_play(games, verbose, player_config):
    black_player = load_player(Board.BLACK, player_config)
    white_player = load_player(Board.WHITE, player_config)
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

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="run.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--player_conf", default="./config/config.ini", help="player config")
    parser.add_argument("--verbose", default=1, type=int, help="verbose level")
    parser.add_argument("--games", default=100000, type=int, help="number of games to play")

    args = parser.parse_args()
    player_config = Config(args.player_conf)

    print '-' * 70
    print "CONFIG"
    print '-' * 70
    player_config.print_config()
    print '-' * 70

    self_play(args.games, args.verbose, player_config)
