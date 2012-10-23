import subprocess
import sys
import numpy

class GameOverException(Exception): pass
class GameWonException(Exception): pass
class MineGame(object):
  def __init__(self, x, y, nmines):
    self.shape = (x, y)
    self.board = self.new_board(x, y, nmines)
    self.count = self.board_counts(self.board)
    self.steps = numpy.zeros((x, y), bool)

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
    self.steps[i,j] = True
    if self.board[i,j]:
      raise GameOverException()
    if self.is_won:
      raise GameWonException()
    return self.count[i,j]

  def show(self):
    s = ''
    for i in range(self.shape[0]):
      for j in range(self.shape[1]):
        s += str(self.count[i,j]) if self.steps[i,j] else 'X'
      s += '\n'
    return s.replace('0', ' ')

def difficulty(x, y, nmines):
  return 10 * nmines / (x * y)

def play_game(x, y, nmines):
  game = MineGame(x, y, nmines)
  print '{0} {1} {2}'.format(x, y, nmines)
  while True:
    input = sys.stdin.readline().strip()
    i, j = map(int, input.split(' '))
    try:
      print game.step(i, j)
      #print game.show()
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

def launch_games(x, y, nmines, solver_cmd, n):
  print 'mines - [{0}x{1}, {2} mines, difficulty {3}]'.format(x, y, nmines, int(difficulty(x, y, nmines)))
  print 'played by - "{0}"'.format(solver_cmd)
  l = []
  for i in range(n):
    gm = launch_game(x, y, nmines, solver_cmd)
    #print gm.show()
    l.append(gm.is_won)
  wins = sum(l)
  print '{0} games played'.format(n)
  print '{0} games won ({1:.2f}%)'.format(wins, wins / float(n) * 100.)
  return wins

def main(argv):
  if len(argv) < 6:
    print 'usage: mines.py GAMES X_SIZE Y_SIZE N_MINES SOLVER_CMD'
    return 
  games, x, y, nmines = map(int, argv[1:5])
  solver_cmd = argv[5]
  launch_games(x, y, nmines, solver_cmd, games)

if __name__ == '__main__':
  main(sys.argv)

