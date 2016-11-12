# -*- coding: utf-8 -*-
import numpy as np
import ConfigParser

from othello import Board, Game
from ai import HumanPlayer, Bot
from value import ModelScorer, NaiveScorer
import time

def tell_game_stat(game):
    b,w,t = game.game_stat()
    num_of_games = b + w + t
    info_template = "total games: {}, black wins: {} {}, white wins: {} {}, ties: {}"
    print info_template.format(num_of_games,
                               b,
                               1.*b/num_of_games,
                               w,
                               1.*w/num_of_games,
                               t)

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
    if player_type == "Bot":
        evaluator_type = player_config.get_as_str(section, "evaluator")
        model = player_config.get_as_str(section, "model")
        if evaluator_type == "Naive":
            evaluator = NaiveScorer(role)
        elif evaluator_type == "Model":
            evaluator = ModelScorer()
            evaluator.load(model)
        depth = player_config.get_as_int(section, "depth", 1)
        final_depth = player_config.get_as_int(section, "final_depth", 3)
        player = Bot(evaluator, depth, final_depth, role)
    elif player_type == "Human":
        player = HumanPlayer(role)
    else:
        raise Exception("Unknown player type:{0}".format(player_type))
    return player

def play(games, verbose, player_config):
    black_player = load_player(Board.BLACK, player_config)
    white_player = load_player(Board.WHITE, player_config)
    game = Game(black_player, white_player, verbose)
    for i in range(1, games+1):
        game.run()
        if i % 100 == 0 and i > 0:
            tell_game_stat(game)
    tell_game_stat(game)


import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="run.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--player_conf", default="./config/config.ini", help="player config")
    parser.add_argument("--verbose", default=1, type=int, help="verbose level")
    parser.add_argument("--games", default=500000, type=int, help="number of games to play")

    args = parser.parse_args()
    player_config = Config(args.player_conf)

    print '-' * 70
    print "CONFIG"
    print '-' * 70
    player_config.print_config()
    print '-' * 70

    play(args.games, args.verbose, player_config)
