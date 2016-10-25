# -*- coding: utf-8 -*-

import tensorflow as tf
from othello import Board
from ai import Agent
import numpy as np

class OthelloModel(object):
    def __init__(self):
        with tf.Graph().as_default() as self._graph:
            self.x = tf.placeholder(tf.float32, shape=[None,8,8], name="board")
            self.y = tf.placeholder(tf.float32, shape=[None,1], name="y")

            self._params = []
            self._prediction = []
            self._train_step = []

            for i in range(0, Board.NUMBER_OF_STAGES):
                # model
                with tf.name_scope("conv1"):
                    output_channels1 = 16
                    kernel = tf.Variable(tf.truncated_normal([3,3,1,output_channels1], stddev=0.1))
                    bias = tf.Variable(tf.zeros([output_channels1]))
                    x = tf.reshape(self.x, [-1,8,8,1])
                    h = tf.nn.relu(tf.nn.conv2d(x, kernel, strides=[1,1,1,1], padding="SAME") + bias)
                    p1 = tf.nn.max_pool(h, ksize=[1,2,2,1], strides=[1,2,2,1], padding="SAME")
                    self._params.extend([kernel, bias])
                with tf.name_scope("conv2"):
                    output_channels2 = 16
                    kernel = tf.Variable(tf.truncated_normal([3,3,output_channels1,output_channels2], stddev=0.1))
                    bias = tf.Variable(tf.zeros([output_channels2]))
                    h = tf.nn.relu(tf.nn.conv2d(p1, kernel, strides=[1,1,1,1], padding="SAME")+ bias)
                    p2 = tf.nn.max_pool(h, ksize=[1,2,2,1], strides=[1,2,2,1], padding="SAME")
                    self._params.extend([kernel, bias])
                with tf.name_scope("full_connect1"):
                    full1_size = 16
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
                self._prediction.append(tf.nn.sigmoid(logits))

                # cost
                regularizers = (tf.nn.l2_loss(f1_weights) + tf.nn.l2_loss(f1_bias) +
                          tf.nn.l2_loss(f2_weights) + tf.nn.l2_loss(f2_bias))
                cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits, self.y)) # + 5e-4 * regularizers

                # optimizer
                optimizer = tf.train.AdagradOptimizer(learning_rate=0.05)
                self._train_step.append(optimizer.minimize(cost))

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

    def predict(self, x, stage):
        return self._sess.run(self._prediction[stage], feed_dict={self.x: x})

    def update_param(self, x, y, stage):
        self._sess.run(self._train_step[stage], feed_dict={self.x: x, self.y: y})

class TDLAgent(Agent):
    def __init__(self, role, update=False, alpha=0.1, epsilon=0.1, model_file=None, temperature=0.1, explore_method="epsilon"):
        super(TDLAgent, self).__init__(role)
        self._model = OthelloModel()
        if model_file is not None:
            self._model.restore_params(model_file)
        self._alpha = alpha
        self._update = update
        self._epsilon = epsilon
        self._temperature = temperature
        if explore_method not in ["epsilon", "softmax"]:
            raise Exception("`explore_method' should be 'epsilon' or 'softmax'.")
        self._explore_method = explore_method

    def _epsilon_greedy(self, pos, val):
        r = np.random.rand()
        if r < 1 - self._epsilon:
            idx = np.argmax(val)
        else:
            idx = np.random.randint(low=0, high=len(pos))
        return pos[idx], val[idx]

    def _softmax_weighted(self, pos, val):
        x = np.exp(np.array(val)/self._temperature)
        s = np.sum(x)
        r = np.random.rand()
        a = 0.0
        idx = -1
        for i, e in enumerate(x):
            a += (e/s)
            if a >= r:
                idx = i
                break
        return pos[idx], val[idx]

    def save_model(self, model_path):
        if self._update:
            self._model.save_params(model_path)

    def _update_param(self, b, v):
        stage = Board._stage(b)
        v_old = self._model.predict([b], stage)[0][0]
        target = v_old + self._alpha * (v - v_old)
        self._model.update_param([b], [[target]], stage)

    def play(self, board):
        pos = board.feasible_pos(self.role)
        next_vals = []
        for i,j in pos:
            with board.flip2(i, j, self.role):
                stage = board.stage()
                if board.is_terminal_state():
                    if board.wins(self.role):
                        next_vals.append(1.0)
                    else:
                        next_vals.append(0.0)
                else:
                    next_vals.append(self._model.predict([board.board], stage)[0][0])
        if self._explore_method == "epsilon":
            p,v = self._epsilon_greedy(pos, next_vals)
        elif self._explore_method == "softmax":
            p,v = self._softmax_weighted(pos, next_vals)

        if self._update:
            if self._s is not None:
                self._update_param(self._s, v)
            with board.flip2(p[0], p[1], self.role):
                self._s = board.board.copy()

        return p

    def begin_of_game(self, board):
        self._s = None

    def end_of_game(self, board):
        if self._update and self._s is not None:
            v = 0.0
            if board.wins(self.role):
                v = 1.0
            self._update_param(self._s, v)
