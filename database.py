# -*- coding: utf-8 -*-

import struct
import gzip

from othello import Board

def _move_to_str(move):
    player,row,column = move
    if player == Board.BLACK:
        p = '+'
    else:
        p = '-'
    return '{0}{1}{2}'.format(p,chr(ord('a') + column), row+1)

def _mirror1(r, c):
    return c,r

def _mirror2(r, c, sz=8):
    return sz-1-c, sz-1-r

def mirror(r, c, d1, d2, sz=8):
    if d1:
        r,c = _mirror1(r,c)
    if d2:
        r,c = _mirror2(r,c,sz)
    return r,c

def save_db_as_text(db, output_file):
    with open(output_file, 'w') as f:
        for moves, result in db.games:
            f.write("{0}:{1}\n".format(''.join(map(_move_to_str, moves)), result))

def _byte_to_int(b):
    return struct.unpack('b', b)[0]

class ThorDb(object):
    """WTHOR database format: http://cassio.free.fr/cassio/custom_install/database/FORMAT_WTHOR.TXT
    """
    def __init__(self, *database_files):
        self._games = []
        self.inconsistencies = 0
        for database_file in database_files:
            self.add_file(database_file)

    @property
    def games(self):
        return self._games

    def add_file(self, file_name):
        self._games.extend(self._read_thor_file(file_name))
        print "inconsistencies = ", self.inconsistencies

    def _read_thor_file(self, file_name):
        file_header_size = 16
        record_header_size = 8
        shots = 60
        record_size = 68

        games = []
        with open(file_name, "rb") as f:
            c = f.read()
            board_size = _byte_to_int(c[12])
            if board_size == 8 or board_size == 0:
                for i in xrange(file_header_size, len(c), record_size):
                    moves = []
                    b = Board()
                    player = Board.BLACK
                    black_score = _byte_to_int(c[i+6])
                    for j in xrange(record_header_size, record_size):
                        play = _byte_to_int(c[i+j])
                        if play > 0:
                            column = (play % 10) -1
                            row = (play // 10) -1
                            if not b.is_feasible(row, column, player):
                                player = Board.opponent(player)
                            moves.append((player, row, column))
                            b.flip(row, column, player)
                            player = Board.opponent(player)

                    score = b.score(Board.BLACK)
                    if b.score(Board.BLACK) > b.score(Board.WHITE):
                        score += b.score(Board.BLANK)
                    if score == black_score:
                        games.append((moves, black_score*2 - 64))
                    else:
                        self.inconsistencies += 1
        return games

class TextDb(object):
    def __init__(self, *db_files):
        self._games = []
        for db_file in db_files:
            self.add_file(db_file)

    @property
    def games(self):
        return self._games

    def db_stat(self):
        black_wins = 0
        ties = 0
        white_wins = 0
        for _, result in self._games:
            if result > 0:
                black_wins += 1
            elif result < 0:
                white_wins += 1
            else:
                ties += 1
        return (black_wins, white_wins, ties)

    def _mirror_move(self, m, d1, d2):
        r,c = mirror(m[1], m[2], d1, d2)
        return m[0],r,c

    def xgames(self, d1, d2):
        for moves,result in self._games:
            moves2 = map(lambda m: self._mirror_move(m,d1,d2), moves)
            yield moves2,result

    def add_file(self, file_name):
        self._games.extend(self._read_text_file(file_name))

    def _read_text_file(self, file_name):
        games = []
        if file_name.endswith(".gz"):
            f = gzip.open(file_name)
        else:
            f = open(file_name)
        for l in f:
            games.append(self._parse(l))
        f.close()
        return games

    def _parse(self, l):
        moves = []
        tokens = l.strip().split(':')
        steps = len(tokens[0])/3

        for idx in range(0, steps):
            if l[3*idx] == '+':
                player = Board.BLACK
            else:
                player = Board.WHITE
            row = ord(l[3*idx+1]) - ord('a')
            column = int(l[3*idx+2]) - 1
            moves.append((player, row, column))
        result = int(tokens[1])
        return (moves, result)


def validate(db):
    import random
    for moves, result in db.xgames(True, False):
        if random.random() < 0.9:
            continue
        b = Board()
        for p,r,c in moves:
            assert b.is_feasible(r,c,p)
            b.flip(r,c,p)
        black_score = b.score(Board.BLACK)
        white_score = b.score(Board.WHITE)
        score = black_score
        if b.score(Board.BLACK) > b.score(Board.WHITE):
            score = b.score(Board.BLANK) + black_score
        assert result in (black_score-white_score, 2*score - 64)

if __name__ == '__main__':
    # database_files = ["./database/logbook.txt", "./database/WTH.txt"]
    database_files = ["./database/logbook.txt"]
    db = TextDb(*database_files)
    validate(db)
