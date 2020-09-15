# -*- coding: utf-8 -*-
from __future__ import print_function

import numpy as np

from othello import Board, Game
from ai import HumanPlayer, Bot
from value import ModelScorer, NaiveScorer
from util import Config

def load_player(role, config):
    if role == Board.BLACK:
        section = "Black"
    else:
        section = "White"

    player_type = config.get_as_str(section, "type")
    if player_type == "Bot":
        evaluator_type = config.get_as_str(section, "evaluator")
        model = config.get_as_str(section, "model")
        if evaluator_type == "Naive":
            evaluator = NaiveScorer()
        elif evaluator_type == "Model":
            evaluator = ModelScorer()
            evaluator.load(model)
        depth = config.get_as_int(section, "depth", 1)
        final_depth = config.get_as_int(section, "final_depth", 3)
        player = Bot(evaluator, depth, final_depth, role)
    elif player_type == "Human":
        player = HumanPlayer(role)
    else:
        raise Exception("Unknown player type:{0}".format(player_type))
    return player

def tell_game_stat(game):
    b,w,t = game.game_stat()
    num_of_games = b + w + t
    info_template = "total games: {}, black wins: {} {}, white wins: {} {}, ties: {}"
    print(info_template.format(num_of_games,
                               b,
                               1.*b/num_of_games,
                               w,
                               1.*w/num_of_games,
                               t))

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
    parser.add_argument("--conf", default="./config/config.ini", help="player config")
    parser.add_argument("--verbose", default=1, type=int, help="verbose level")
    parser.add_argument("--games", default=100, type=int, help="number of games to play")

    args = parser.parse_args()
    player_config = Config(args.conf)

    print('-' * 70)
    print("CONFIG")
    print('-' * 70)
    player_config.print_config()
    print('-' * 70)

    play(args.games, args.verbose, player_config)
