# -*- coding: utf-8 -*-

import tensorflow as tf


class OthelloModel(object):
    def __init__(self):
        self.x = tf.placeholder(tf.float32, shape=[None,64], name="board")
        self.y = tf.placeholder(tf.float32, shape=[None,1], name="y")

        w1 = tf.Variable(tf.truncated_normal([8,8], mean=0.0, stddev=0.2), name="weight1")
        b1 = tf.Variable(tf.zeros(1), name="bias1")
        w2 = tf.Variable(tf.truncated_normal([4,1], mean=0.0, stddev=0.2), name="weight2")
        b2 = tf.Variable(tf.zeros(1), name="bias2")
        self.params = [w1, b1, w2, b2]

        # model
        w11 = tf.reshape(w1, (64,1))
        w12 = tf.reshape(tf.transpose(w1), (64,1))
        reversed_w1 = tf.reverse(w1, [True, True])
        w13 = tf.reshape(reversed_w1, (64,1))
        w14 = tf.reshape(tf.transpose(reversed_w1), (64,1))
        w = tf.concat(1, [w11,w12,w13,w14])
        h = tf.nn.relu(tf.matmul(self.x, w) + b1)

        self.logits = tf.matmul(h, w2) + b2
        self.prediction = tf.nn.sigmoid(self.logits)

        # cost
        cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(self.logits, self.y))

        # optimizer
        optimizer = tf.train.AdagradOptimizer(learning_rate=0.2)
        # optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
        self.opt_op = optimizer.minimize(cost)

        self.init_op = tf.initialize_all_variables()
        self.sess = tf.Session()
        self.saver = tf.train.Saver(self.params)

    def init_params(self):
        self.sess.run(self.init_op)

    @property
    def parameters(self):
        return self.params
    @property
    def session(self):
        return self.sess

    def save_params(self, file_path):
        self.saver.save(self.sess, file_path)

    def restore_params(self, file_path):
        self.saver.restore(self.sess, file_path)

    def predict(self, x):
        return self.sess.run(self.prediction, feed_dict={self.x: x})

    def update_param(self, x, y):
        self.sess.run([self.opt_op], feed_dict={self.x: x, self.y: y})

from othello import Board
from ai import Agent
import numpy as np

class TDLProcessor(object):
    def __init__(self, role, model_path, batch_size=50):
        self.role = role
        self.model = OthelloModel()
        self.model.init_params()
        self.model_path = model_path
        self.batch_size = batch_size
        self.game_processed = 0
        self.x = []
        self.y = []

    def __call__(self, player, i, j, result, board):
        if player == self.role:
            with board.flip2(i,j,player):
                target = 0.0
                if self.role == Board.BLACK and result > 0:
                    target = 1.0
                if self.role == Board.WHITE and result < 0:
                    target = 1.0
                self.x.append(board.board2)
                self.y.append(target)
            if len(self.x) >= self.batch_size:
                xx = np.vstack(self.x)
                yy = np.vstack(self.y)
                self.model.update_param(xx, yy)
                self.x = []
                self.y = []

    def after_one_game(self):
        self.game_processed += 1
        if self.game_processed % 10000 == 0:
            print "# game processed: ", self.game_processed

    def after_one_replay(self):
        self.save_model()

    def save_model(self, model_path=None):
        if model_path is None:
            model_path = self.model_path
        self.model.save_params(model_path)

class TDLAgent(Agent):
    def __init__(self, role, update=False, alpha=0.1, epsilon=0.1, model_file=None):
        super(TDLAgent, self).__init__(role)
        self._model = OthelloModel()
        self._model.init_params()
        if model_file is not None:
            self._model.restore_params(model_file)
        self._alpha = alpha
        self._update = update
        self._epsilon = epsilon
        self._prev_state = None

    def _epsilon_greedy(self, pos, val):
        r = np.random.rand()
        if r < 1 - self._epsilon:
            idx = np.argmax(val)
        else:
            idx = np.random.randint(low=0, high=len(pos))
        return pos[idx], val[idx]

    def save_model(self, model_path):
        if self._update:
            self._model.save_params(model_path)

    def _is_first_step(self, board):
        return board.blanks >= 59

    def _update_param(self, v):
        prev_val = self._model.predict(self._prev_state)[0][0]
        target = (1.0-self._alpha) * prev_val + self._alpha * v
        self._model.update_param(self._prev_state, [[target]])

    def play(self, board):
        if self._is_first_step(board):
            self._prev_state = None
        pos = board.feasible_pos(self.role)
        next_vals = []
        for i,j in pos:
            with board.flip2(i, j, self.role):
                if board.is_terminal_state():
                    if board.wins(self.role):
                        next_vals.append(1.0)
                    else:
                        next_vals.append(0.0)
                else:
                    next_vals.append(self._model.predict(board.board2)[0][0])

        p,v = self._epsilon_greedy(pos, next_vals)
        if self._update:
            if  self._prev_state is not None:
                self._update_param(v)
            with board.flip2(p[0], p[1], self.role):
                self._prev_state = board.board2.copy()

        return p

    def tell_result(self, board):
        if self._update and self._prev_state is not None:
            v = 0.0
            if board.wins(self.role):
                v = 1.0
            self._update_param(v)
