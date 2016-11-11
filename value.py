# -*- coding: utf-8 -*-
import tensorflow as tf
from othello import Board
import numpy as np


class ModelScorer(object):
    def __init__(self):
        with tf.Graph().as_default() as self._graph:
            self.x = tf.placeholder(tf.float32, shape=[None, 8, 8], name="board")
            self.y = tf.placeholder(tf.float32, shape=[None, 1], name="y")


            output_channels1 = 64
            kernel = tf.Variable(tf.truncated_normal([4,4,1,output_channels1], stddev=0.1))
            bias = tf.Variable(tf.zeros([output_channels1]))
            x = tf.reshape(self.x, [-1,8,8,1])
            h = tf.nn.relu(tf.nn.conv2d(x, kernel, strides=[1,1,1,1], padding="SAME") + bias)

            s = output_channels1 * 8 * 8
            w = tf.Variable(tf.truncated_normal([s, 1], stddev=0.1))
            self._prediction = tf.matmul(tf.reshape(h, [-1, s]), w)
            self._cost = tf.reduce_mean(tf.square(self.y - self._prediction))
            self._optimizer = tf.train.AdagradOptimizer(learning_rate=0.07)
            self._train = self._optimizer.minimize(self._cost)

            self._session = tf.Session()
            self._saver = tf.train.Saver([kernel, bias, w])
            self._session.run(tf.initialize_all_variables())
            self._global_step = 0

    def __call__(self, board):
        return self._session.run(self._prediction, feed_dict={self.x: [board.board]})[0][0]

    def update(self, xs, ys):
        self._session.run(self._train, feed_dict={self.x: [xs], self.y: [ys]})

    def load(self, path):
        self._saver.restore(self._session, path)

    def save(self, path):
        self._saver.save(self._session, path, global_step=self._global_step)
        self._global_step += 1
