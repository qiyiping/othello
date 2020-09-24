#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import time

from .othello import Board
from .util import Hash


class Node(object):
    def __init__(self, board, action, role, parent):
        self.parent = parent
        self.action = action
        self.role = role
        self.value = 0
        self.visits = 0
        self.children = []
        opponent = Board.opponent(role)
        feasible_pos = board.feasible_pos(opponent)
        if feasible_pos:
            self.unexamined_actions = (opponent, feasible_pos)
        else:
            self.unexamined_actions = (role, board.feasible_pos(role))

class MTCS(object):
    def __init__(self, time_in_ms):
        self.time_in_ms = time_in_ms

    def _get_node(self, board, role):
        return Node(board, None, role, None)

    def search(self, board, role):
        node = self._get_node(board, role)
        new_board = Board()
        new_board.set_board(board.board)

        time_limit = time.time() + self.time_in_ms / 1000.0
        while time.time() < time_limit:
            # selection
            while len(node.unexamined_actions) == 0 and len(node.children) > 0:
                node = self.select(node)
                new_board.flip(action, role)
            # expansion
            self.expand(node)
            # playout
            


    def select(self, node):
        pass
    def expand(self, node):
        pass
    def rollout(self, node):
        pass
    def update(self, node):
        pass
