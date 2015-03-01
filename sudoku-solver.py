import sys, copy

breadth = 0

#class Board(enum.Enum):
class State():
    solved = 0
    unsolved = 1
    broken = 2

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
    
    def index(self): return self._index    
    def row(self): return self._row
    def column(self): return self._column
    def subgrid(self): return self._subgrid
    def value(self): return self._value
    def branches(self): return 9 - len(self._restrictions)
        
    def possibleValues(self):
        for i in range(1, 10):
            if i not in self._restrictions:
                yield i
    
    def setValue(self, value):
        if not self.getRestriction(value):
            self._value = value
            self._restrictions = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
            self._restrictions.remove(value)
            
    def getRestriction(self, value): return value in self._restrictions
    def setRestriction(self, value):
        if self.value() == 0:
            self._restrictions.add(value)

class Board(object):
    def __init__(self, name = "Unnamed"):
        self.setName(name)
        self.clear()
        global breadth
        breadth += 1
        
    def __deepcopy__(self, memo={}):
        boardCopy = Board()
        boardCopy._name = copy.deepcopy(self._name, memo)
        boardCopy._squares = copy.deepcopy(self._squares, memo)
        return boardCopy
        
    def name(self): return self._name
    def setName(self, name): self._name = name
    
    def clear(self):
        self._squares = list(Square(i) for i in range(81))
        
    def inputEuler(self, lines):
        self.clear()
        self.setName(lines[0].strip())
        for i in range(9):
            row = lines[i + 1]
            for j in range(9):
                value = int(row[j])
                if value != 0:
                    self.setValue(9 * i + j, value)
        return 10
    
    def outputEuler(self):
        print(self.name() + "\n", end="")
        for i in range(9):
            for j in range(9):
                square = self._squares[i * 9 + j]
                value = square.value()
                print(str(value), end="")
            print("\n", end="")
            
    def outputPretty(self):
        print("+-----------+\n|{:^11}|\n".format(self.name()), end="")
        for i in range(9):
            if i % 3 == 0:
                print("+---+---+---+\n", end="")
            for j in range(9):
                if j % 3 == 0:
                    print("|", end="")
                square = self._squares[i * 9 + j]
                value = square.value()
                print(str(value), end="")
            print("|\n", end="")
        print("+---+---+---+\n", end="")
       
    def setValue(self, index, value):
        square = self._squares[index]
        row = square.row()
        column = square.column()
        subgrid = square.subgrid()
        square.setValue(value)
        for otherSquare in self._squares:
            if row == otherSquare.row() or column == otherSquare.column() or subgrid == otherSquare.subgrid():
                otherSquare.setRestriction(value)
                
    def evolve(self):
        while True:
            changed = False
            for square in self._squares:
                if square.branches() == 1 and square.value() == 0:
                    possibleValues = list(square.possibleValues())
                    if len(possibleValues) == 1:
                        self.setValue(square.index(), possibleValues[0])
                        changed = True
            if not changed:
                break
            
    def state(self):
        state = State.solved
        for square in self._squares:
            branches = square.branches()
            if branches > 1:
                state = State.unsolved
            elif branches < 1:
                state = State.broken
                break
        return state
    
    def children(self):
        minBranches = 10
        branchSquare = None
        for square in self._squares:
            if square.value() == 0 and square.branches() < minBranches:
                minBranches = square.branches()
                branchSquare = square
                if minBranches <= 2:
                    break
        
        for value in branchSquare.possibleValues():
            boardCopy = copy.deepcopy(self)
            boardCopy.setValue(branchSquare.index(), value)
            yield boardCopy
    
    def solve(self, depth = 0):
        self.evolve()
        if self.state() == State.solved:
            sys.stderr.write("depth:{}\n".format(depth))
            sys.stderr.write("breadth:{}\n".format(breadth))
            return self
        elif self.state() == State.broken:
            return self
        else:
            returnBoard = None
            for child in self.children():
                returnBoard = child.solve(depth + 1)
                if returnBoard.state() == State.solved:
                    break
            return returnBoard
    
    def proof(self): return 100 * self._squares[0].value() + 10 * self._squares[1].value() + self._squares[2].value()
        
def main():
    global breadth
    lines = sys.stdin.readlines()
    sum = 0
    while len(lines) > 0:
        breadth = 0
        board = Board()
        size = board.inputEuler(lines)
        lines = lines[size:]
        solution = board.solve()
        solution.outputPretty()
        sum += solution.proof()
        
    sys.stderr.write("sum:{}\n".format(sum))

if __name__ == "__main__":
    main()