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
        self._row = row(index)
        self._column = column(index)
        self._subgrid = subgrid(index)
        self._value = 0
        self._restrictions = set()

    @property
    def index(self): return self._index    
 
    @property
    def row(self): return self._row
 
    @property
    def column(self): return self._column
 
    @property
    def subgrid(self): return self._subgrid
 
    @property
    def value(self): return self._value
 
    @property
    def branches(self): return 9 - len(self._restrictions)
        
    def possibleValues(self):
        for i in range(1, 10):
            if i not in self._restrictions:
                yield i
    
    @value.setter
    def value(self, value):
        if not self.getRestriction(value):
            self._value = value
            self._restrictions = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
            self._restrictions.remove(value)
     
    def getRestriction(self, value): return value in self._restrictions

    def setRestriction(self, value):
        if self.value == 0:
            self._restrictions.add(value)

class Board(object):
    def __init__(self):
        self.name = None
        self.clear()
        global breadth
        breadth += 1
        
    def __deepcopy__(self, memo={}):
        boardCopy = Board()
        boardCopy.name = copy.deepcopy(self.name, memo)
        boardCopy._squares = copy.deepcopy(self._squares, memo)
        return boardCopy
    
    def clear(self):
        self._squares = list(Square(i) for i in range(81))

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
        print(self.name)
        for i in range(9):
            for j in range(9):
                square = self._squares[i * 9 + j]
                value = square.value()
                print(value, end='')
            print('')
            
    def outputPretty(self):
        print("+-----------+\n|{:^11}|".format(self.name))
        for i in range(9):
            if i % 3 == 0:
                print('+---+---+---+')
            for j in range(9):
                if j % 3 == 0:
                    print('|', end='')
                square = self._squares[i * 9 + j]
                value = square.value
                print(value, end='')
            print('|')
        print('+---+---+---+')
       
    def setValue(self, index, value):
        square = self._squares[index]
        row = square.row
        column = square.column
        subgrid = square.subgrid
        square.value = value
        for otherSquare in self._squares:
            if row == otherSquare.row or column == otherSquare.column or subgrid == otherSquare.subgrid:
                otherSquare.setRestriction(value)
                
    def evolve(self):
        while True:
            changed = False
            for square in self._squares:
                if square.branches == 1 and square.value == 0:
                    possibleValues = list(square.possibleValues())
                    if len(possibleValues) == 1:
                        self.setValue(square.index, possibleValues[0])
                        changed = True
            if not changed:
                break
            
    def state(self):
        state = State.SOLVED
        for square in self._squares:
            branches = square.branches
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
            if square.value == 0 and square.branches < minBranches:
                minBranches = square.branches
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
        
def main():
    global breadth
    sum = 0
    while True:
        board = Board.parseEuler(sys.stdin)
        if board is None:
            break
        breadth = 0
        solution = board.solve()
        solution.outputPretty()
        sum += solution.proof()
        
    print("sum:{}".format(sum), file=sys.stderr)

if __name__ == '__main__':
    main()