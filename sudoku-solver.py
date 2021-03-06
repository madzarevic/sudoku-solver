import sys, copy
from enum import Enum

breadth = 0

class State(Enum):
    SOLVED = 0
    UNSOLVED = 1
    BROKEN = 2

def row(index): return index // 9
def column(index): return index % 9
def subgrid(index): return 3 * (row(index) // 3) + column(index) // 3

class Square(object):        
    def __init__(self, index):
        self._index = index
        self._value = 0
        self._possibilities = set(range(1, 10))

    @property
    def index(self): return self._index    
  
    @property
    def value(self): return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._possibilities.clear()

    def branches(self): return len(self._possibilities) if self.value == 0 else 1
        
    def possibleValues(self):
        if self.value == 0:
            return self._possibilities
        return set(self.value)

    def setRestriction(self, value):
        if self.value == 0:
            self._possibilities.discard(value)

class Board(object):
    def __init__(self):
        self.name = None
        self._squares = list(Square(i) for i in range(81))
        global breadth
        breadth += 1
        
    def __deepcopy__(self, memo={}):
        boardCopy = Board()
        boardCopy.name = copy.deepcopy(self.name, memo)
        boardCopy._squares = copy.deepcopy(self._squares, memo)
        return boardCopy

    @staticmethod
    def parseEuler(f):
        board = Board()
        for i in range(-1, 9):
            line = f.readline()
            if line == '':
                return None
            if i == -1:
                board.name = line.strip()
            else:
                row = line.strip()
                for j in range(9):
                    value = int(row[j])
                    if value != 0:
                        board.setValue(9 * i + j, value)
        return board
    
    def outputEuler(self):
        rows = []
        rows.append(self.name)
        for i in range(9):
            row = ''
            for j in range(9):
                square = self._squares[i * 9 + j]
                row += str(square.value)
            rows.append(row)
        return "\n".join(rows)
            
    def outputPretty(self):
        rows = []
        rows.append('+-----------+')
        rows.append("|{:^11}|".format(self.name))
        for i in range(9):
            if i % 3 == 0:
                rows.append('+---+---+---+')
            row = ''
            for j in range(9):
                if j % 3 == 0:
                    row += '|'
                square = self._squares[i * 9 + j]
                row += str(square.value)
            row += '|'
            rows.append(row)
        rows.append('+---+---+---+')
        return "\n".join(rows)
       
    def setValue(self, index, value):
        square = self._squares[index]
        square.value = value
        for otherIndex in range(81):
            if row(index) == row(otherIndex) or column(index) == column(otherIndex) or subgrid(index) == subgrid(otherIndex):
                otherSquare = self._squares[otherIndex]
                otherSquare.setRestriction(value)
                
    def evolve(self):
        while True:
            changed = False
            for square in self._squares:
                if square.branches() == 1 and square.value == 0:
                    possibleValues = list(square.possibleValues())
                    if len(possibleValues) == 1:
                        self.setValue(square.index, possibleValues[0])
                        changed = True
            if not changed:
                break
            
    def state(self):
        state = State.SOLVED
        for square in self._squares:
            branches = square.branches()
            if branches > 1:
                state = State.UNSOLVED
            elif branches < 1:
                state = State.BROKEN
                break
        return state
    
    def children(self):
        minBranches = 10
        branchSquare = None
        for square in self._squares:
            if square.value == 0 and square.branches() < minBranches:
                minBranches = square.branches()
                branchSquare = square
                if minBranches <= 2:
                    break
        
        for value in branchSquare.possibleValues():
            boardCopy = copy.deepcopy(self)
            boardCopy.setValue(branchSquare.index, value)
            yield boardCopy
    
    def solve(self, depth = 0):
        self.evolve()
        if self.state() == State.SOLVED:
            print("depth:{}".format(depth), file=sys.stderr)
            print("breadth:{}".format(breadth), file=sys.stderr)
            return self
        elif self.state() == State.BROKEN:
            return self
        else:
            returnBoard = None
            for child in self.children():
                returnBoard = child.solve(depth + 1)
                if returnBoard.state() == State.SOLVED:
                    break
            return returnBoard
    
    def proof(self): return 100 * self._squares[0].value + 10 * self._squares[1].value + self._squares[2].value

def problem96(filename='p096_sudoku.txt'):
    global breadth
    sum = 0
    with open(filename, 'r') as f:
        while True:
            board = Board.parseEuler(f)
            if board is None:
                break
            breadth = 0
            solution = board.solve()
            output = solution.outputPretty()
            print(output, file=sys.stderr)
            sum += solution.proof()
    return sum
        
def main():
    print("sum:{}".format(problem96()), file=sys.stderr)

if __name__ == '__main__':
    main()