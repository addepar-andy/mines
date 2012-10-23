import sys
import random

def rand_move(x, y):
  n = x * y
  r = random.randint(0, n - 1)
  return r % x, r / x

class MineSolver(object):
  def __init__(self, x, y, nmines):
    self.x = x
    self.y = y

  def move(self):
    return rand_move(self.x, self.y)

def solve_game():
  line = sys.stdin.readline().strip()
  s = MineSolver(*map(int, line.split()))
  while True:
    move = s.move()
    print ' '.join(map(str, move))
    sys.stdout.flush()
    val = sys.stdin.readline().strip()
    if val == 'you win' or val == 'game over':
      return
    i = int(val)

def main(argv):
  solve_game()

if __name__ == '__main__':
  main(sys.argv)
