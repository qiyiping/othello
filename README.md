# Playing Othello(Reversi) By Reinforcement Learning #

## Introduction ##
This is a simple application that learn playing Othello by
*reinforcement learning*.

TD(0) is used to evaluate a policy.

Value approximation function is based on *n-tuple network* introduced
in Wojciech's paper.

## Quick Start ##

Run `python tdl.py` to learn a policy by self-play.

Edit `config/config.ini` to setup players and run `python run.py` to
play Othello in command line.

Or you can try the simple web app:
  * Run `npm install && npm run build` in `web/ui`.
  * Install `gevent` and `flask`: `pip install gevent flask`
  * Run `python run_server.py`
  * Open [http://localhost:44399](http://localhost:44399) and play!

## Reference ##
- Jaśkowski, Wojciech (2014). Systematic n-tuple networks for
  othello position evaluation. ICGA Journal, 37(2), 85–96.

- Sutton, R. S., & Barto, A. G. (1998). Reinforcement learning: an
  introduction. : MIT press Cambridge.
