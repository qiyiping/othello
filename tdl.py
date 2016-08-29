# -*- coding: utf-8 -*-

import tensorflow as tf


class OthelloModel(object):
    def __init__(self):
        self.x = tf.placeholder(tf.float32, shape=[None,8,8], name="board")
        self.y = tf.placeholder(tf.float32, shape=[None,1], name="y")

        self._params = []

        # model
        with tf.name_scope("conv1"):
            output_channels1 = 32
            kernel = tf.Variable(tf.truncated_normal([3,3,1,output_channels1], stddev=0.1))
            bias = tf.Variable(tf.zeros([32]))
            x = tf.reshape(self.x, [-1,8,8,1])
            h = tf.nn.relu(tf.nn.conv2d(x, kernel, strides=[1,1,1,1], padding="SAME") + bias)
            p1 = tf.nn.max_pool(h, ksize=[1,2,2,1], strides=[1,2,2,1], padding="SAME")
            self._params.extend([kernel, bias])
        with tf.name_scope("conv2"):
            output_channels2 = 64
            kernel = tf.Variable(tf.truncated_normal([3,3,output_channels1,output_channels2], stddev=0.1))
            bias = tf.Variable(tf.zeros([64]))
            h = tf.nn.relu(tf.nn.conv2d(p1, kernel, strides=[1,1,1,1], padding="SAME")+ bias)
            p2 = tf.nn.max_pool(h, ksize=[1,2,2,1], strides=[1,2,2,1], padding="SAME")
            self._params.extend([kernel, bias])
        with tf.name_scope("full_connect1"):
            full1_size = 8
            conv2_size = 8 // 4 * 8 // 4 * output_channels2
            x = tf.reshape(p2, [-1, conv2_size])
            f1_weights = tf.Variable(tf.truncated_normal([conv2_size, full1_size], stddev=0.1))
            f1_bias = tf.Variable(tf.truncated_normal([full1_size], stddev=0.1))
            f1 = tf.nn.relu(tf.matmul(x,f1_weights) + f1_bias)
            self._params.extend([f1_weights, f1_bias])
        with tf.name_scope("full_connect2"):
            f2_weights = tf.Variable(tf.truncated_normal([full1_size, 1], stddev=0.1))
            f2_bias = tf.Variable(tf.truncated_normal([1], stddev=0.1))
            logits = tf.matmul(f1,f2_weights) + f2_bias
            self._params.extend([f2_weights, f2_bias])

        # prediction
        self._prediction = tf.nn.sigmoid(logits)

        # cost
        regularizers = (tf.nn.l2_loss(f1_weights) + tf.nn.l2_loss(f1_bias) +
                  tf.nn.l2_loss(f2_weights) + tf.nn.l2_loss(f2_bias))
        self._cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits, self.y)) + 5e-4 * regularizers

        # optimizer
        optimizer = tf.train.AdagradOptimizer(learning_rate=0.05)
        self._train_step = optimizer.minimize(self._cost)

        # init params
        init_op = tf.initialize_all_variables()
        self._sess = tf.Session()
        self._sess.run(init_op)

        # saver
        self._saver = tf.train.Saver(self._params)

    @property
    def parameters(self):
        return self._params
    @property
    def session(self):
        return self._sess

    def save_params(self, file_path):
        self._saver.save(self._sess, file_path)

    def restore_params(self, file_path):
        self._saver.restore(self._sess, file_path)

    def predict(self, x):
        return self._sess.run(self._prediction, feed_dict={self.x: x})

    def update_param(self, x, y):
        self._sess.run([self._train_step], feed_dict={self.x: x, self.y: y})

from othello import Board
from ai import Agent, ScoreEvaluator, AlphaBeta
import numpy as np

class TDLProcessor(object):
    def __init__(self, role, model_path, batch_size=50):
        self.role = role
        self.model = OthelloModel()
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
                self.x.append(board.board.copy())
                self.y.append([target])
            if len(self.x) >= self.batch_size:
                xx = np.stack(self.x)
                yy = np.stack(self.y)
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
    def __init__(self, role, update=False, alpha=0.1, epsilon=0.1, model_file=None, depth=3):
        super(TDLAgent, self).__init__(role)
        self._model = OthelloModel()
        if model_file is not None:
            self._model.restore_params(model_file)
        self._alpha = alpha
        self._update = update
        self._epsilon = epsilon
        self._prev_state = None
        self._depth = depth
        score_evaluator = ScoreEvaluator(role)
        self._searcher = AlphaBeta(score_evaluator, depth)

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

        if board.blanks <= self._depth:
            s, p = self._searcher.search(board, self.role)
            if s >=32:
                v = 1.0
            else:
                v = 0.0
        else:
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
                        next_vals.append(self._model.predict([board.board])[0][0])
            p,v = self._epsilon_greedy(pos, next_vals)

        if self._update:
            if  self._prev_state is not None:
                self._update_param(v)
            with board.flip2(p[0], p[1], self.role):
                self._prev_state = board.board.copy()

        return p

    def tell_result(self, board):
        if self._update and self._prev_state is not None:
            v = 0.0
            if board.wins(self.role):
                v = 1.0
            self._update_param(v)
