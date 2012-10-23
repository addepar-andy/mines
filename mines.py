import argparse
import collections
import json
import os
import os.path
import subprocess
import sys

import numpy

class GameOverException(Exception): pass
class GameWonException(Exception): pass
class MineGame(object):
  def __init__(self, board):
    self.shape = board.shape
    self.board = board
    self.count = self.board_counts(self.board)
    self.steps = numpy.zeros(self.shape, bool)
    self.moves = collections.deque()
    self.active = True

  @classmethod
  def new_board(cls, x, y, nmines):
    n = x * y
    m = numpy.zeros(n, bool)
    i = numpy.arange(n)
    numpy.random.shuffle(i)
    m[i[:nmines]] = True
    return m.reshape((x, y))

  @classmethod
  def board_counts(cls, b):
    c = numpy.zeros(b.shape, int)
    for i in range(b.shape[0]):
      for j in range(b.shape[1]):
        if b[i,j]:
          c[max(i-1, 0):i+2, max(j-1, 0):j+2] += 1
    return c

  @property
  def is_won(self): return (self.steps | self.board).all()

  def step(self, i, j):
    assert self.active, 'cannot play a completed game'
    self.moves.append((i,j))
    self.steps[i,j] = True
    if self.board[i,j]:
      self.active = False
      raise GameOverException()
    if self.is_won:
      self.active = False
      raise GameWonException()
    return self.count[i,j]

  def show(self):
    s = ''
    for i in range(self.shape[0]):
      for j in range(self.shape[1]):
        s += str(self.count[i,j]) if self.steps[i,j] else 'X'
      s += '\n'
    return s.replace('0', ' ')

  def state_log(self):
    g = MineGame(self.board)
    l = []
    for mi in self.moves:
      try: 
        g.step(*mi)
      except (GameOverException, GameWonException) as e:
        pass
      l.append(g.show())
    return l

  def json(self):
    return json.dumps(dict(
      shape=self.shape,
      board=self.board.tolist(),
      count=self.count.tolist(),
      moves=list(self.moves),
      log=self.state_log(),
    ))

def mine_game(x, y, nmines):
  return MineGame(MineGame.new_board(x, y, nmines))

def difficulty(x, y, nmines):
  return 10 * nmines / (x * y)

def play_game(x, y, nmines):
  game = mine_game(x, y, nmines)
  print '{0} {1} {2}'.format(x, y, nmines)
  while True:
    input = sys.stdin.readline().strip()
    i, j = map(int, input.split(' '))
    try:
      print game.step(i, j)
    except GameOverException:
      print "game over"
      break
    except GameWonException:
      print "you win"
      break
  return game

def launch_game(x, y, nmines, solver_cmd):
  p_solv = subprocess.Popen(solver_cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  stdin, stdout = sys.stdin, sys.stdout
  sys.stdin, sys.stdout = p_solv.stdout, p_solv.stdin
  won = play_game(x, y, nmines)
  sys.stdin, sys.stdout = stdin, stdout
  return won

def launch_games(x, y, nmines, solver_cmd, n, log_dir=None):
  print 'mines - [{0}x{1}, {2} mines, difficulty {3}]'.format(x, y, nmines, int(difficulty(x, y, nmines)))
  print 'played by - "{0}"'.format(solver_cmd)
  l = []
  if log_dir is not None and not os.path.exists(log_dir):
    os.mkdir(log_dir)
  for i in range(n):
    gm = launch_game(x, y, nmines, solver_cmd)
    if log_dir is not None:
      open(os.path.join(log_dir, 'mines.log.{0}.json'.format(i)), 'w').write(gm.json())
    l.append(gm.is_won)
  wins = sum(l)
  print '{0} games played'.format(n)
  print '{0} games won ({1:.2f}%)'.format(wins, wins / float(n) * 100.)
  return wins

def main(argv):
  parser = argparse.ArgumentParser(description='Play minesweeper')
  parser.add_argument('ngames', type=int)
  parser.add_argument('xsize', type=int)
  parser.add_argument('ysize', type=int)
  parser.add_argument('nmines', type=int)
  parser.add_argument('solver_cmd', type=str)
  parser.add_argument('--log', dest='log_dir', default=None, help='log games to a folder')
  args = parser.parse_args()

  games, x, y, nmines = args.ngames, args.xsize, args.ysize, args.nmines
  launch_games(x, y, nmines, args.solver_cmd, games, log_dir=args.log_dir)

if __name__ == '__main__':
  main(sys.argv)

