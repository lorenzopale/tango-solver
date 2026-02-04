import numpy as np
from utilities import debug as debug, log as log

class Line:
    def __init__(self, line):
        self.line = line
        self.n    = len(line)

    def tbd(self):
        return len(self.line[self.line == 0])

    def solve(self, depend):
        tbd_old = None
        tbd_new = self.tbd()
        while tbd_new != 0 and tbd_new != tbd_old: # Iterate until no more changes
            tbd_old = tbd_new
            if self.tbd() == 1:
                if debug: print(f"Line completion")
                self.line[self.line == 0] = -sum(self.line)
                return self
            else:
                # Check if saturated
                if sum(self.line == 1) == (self.n / 2):
                    self.line[self.line == 0] = -1
                    return self
                if sum(self.line == -1) == (self.n / 2):
                    self.line[self.line == 0] = 1
                    return self
                # Check consecutives
                for i in range(self.n - 1):
                    if self.line[i] != 0 and self.line[i] == self.line[i+1]:
                        if debug: print(f"Consecutives {i}-{i+1}")
                        if self.line[ (i-1)%self.n ] == 0:
                            if debug: print(f"   writing {(i-1)%self.n}")
                            self.line[ (i-1)%self.n ] = -self.line[i]
                        if self.line[ (i+2)%self.n ] == 0:
                            if debug: print(f"   writing {(i+2) % self.n}")
                            self.line[ (i+2)%self.n ] = -self.line[i]
                # Check if forking
                for i in range(self.n - 2):
                    if (self.line[[i, i+1, i+2]] == [1,0,1]).all():
                        if debug: print(f"Forking {i}-{i+2}")
                        self.line[i+1] = -1
                    if (self.line[[i, i+1, i+2]] == [-1,0,-1]).all():
                        if debug: print(f"Forking {i}-{i + 2}")
                        self.line[i+1] = 1
                # Check dependencies
                for i, j, type in depend:
                    if self.line[i] != 0:
                        if debug: print(f"Dependency {i}-{j}({type}): writing {j}")
                        self.line[j] = self.line[i] * type
                    elif self.line[j] != 0:
                        if debug: print(f"Dependency {i}-{j}({type}): writing {i}")
                        self.line[i] = self.line[j] * type
                    elif type == 1 and self.line[(i-1)%self.n] != 0:
                        self.line[i] = -self.line[(i-1)%self.n]
                        self.line[j] = -self.line[(i-1)%self.n]
                    elif type == 1 and self.line[(j+1)%self.n] != 0:
                        self.line[i] = -self.line[(j+1)%self.n]
                        self.line[j] = -self.line[(j+1)%self.n]
            tbd_new = self.tbd()
        return self

    def insert_row_in_grid(self, Game, row):
        Game.grid[row,:] = self.line
        return Game

    def insert_col_in_grid(self, Game, col):
        Game.grid[:,col] = self.line
        return Game

class Game:
    def __init__(self, n = 6):
        # Grid size
        self.n = n
        # Grid initial and working variable. +1=sun, -1=moon, 0=empty
        self.grid = np.int8(np.zeros((self.n, self.n)))
        self.initial_grid = np.int8(np.zeros((self.n, self.n)))
        # Dependencies (type: 1 for equal, -1 for cross)
        # List of list, each containing one dependency from cell A to cell B:
        # [ [A_row, A_column, B_row, B_column, type], [...] ]
        self.depend = np.empty([0,5])
        if debug: print(self)

    def import_game_from_gui(self, gui):
        self.set_game( gui.GameGrid, gui.GameDepend )

    def export_solution_moves(self):
        # Format: row, col, number_of_clicks
        # with number_of_clicks = 1 for a sun  ( 1%3 = 1 ok )
        #      number_of_clicks = 2 for a moon (-1%3 = 2 ok )
        moves = [
                    [col, row, (self.grid[row,col]%3) ]
                    for row in range(self.n)
                    for col in range(self.n)
                    if self.initial_grid[row,col] == 0      ]
        return moves



    def set_game(self, initial_grid, depend):
        self.initial_grid = np.int8(initial_grid)
        np.copyto(self.grid, self.initial_grid)
        self.depend = np.int8(depend)
        if debug: print(self)


    def _example1(self):
        self.n = 6
        initial_grid = np.int8(np.zeros((self.n, self.n)))
        initial_grid[2,2] = -1
        initial_grid[2,3] = -1
        initial_grid[4,1] = 1
        initial_grid[4,4] = -1
        initial_grid[5,2] = 1
        initial_grid[5,3] = 1
        depend = np.int8(np.array(
            [
                [0, 1, 0, 2, 1],
                [0, 3, 0, 4, 1],
                [1, 0, 2, 0, -1],
                [2, 0, 3, 0, 1],
                [1, 5, 2, 5, -1],
                [2, 5, 3, 5, 1]
            ]
        ))
        self.set_game(initial_grid, depend)

    def __str__(self):
        s = ""
        s = "+---"*self.n + "+\n"
        for r in range(self.n):
            for c in range(self.n):
                match self.grid[r,c]:
                    case -1:
                        if [r,c-1,r,c,1] in self.depend.tolist():
                            s += "= ) "
                        elif [r,c-1,r,c,-1] in self.depend.tolist():
                            s += "x ) "
                        else:
                            s += "| ) "
                    case 1:
                        if [r, c - 1, r, c, 1] in self.depend.tolist():
                            s += "= @ "
                        elif [r, c - 1, r, c, -1] in self.depend.tolist():
                            s += "x @ "
                        else:
                            s += "| @ "
                    case _:
                        if [r, c - 1, r, c, 1] in self.depend.tolist():
                            s += "=   "
                        elif [r, c - 1, r, c, -1] in self.depend.tolist():
                            s += "x   "
                        else:
                            s += "|   "
            s += "|\n"
            for c in range(self.n):
                if [r,c,r+1,c,1] in self.depend.tolist():
                    s += "+-=-"
                elif [r,c,r+1,c,-1] in self.depend.tolist():
                    s += "+-x-"
                else:
                    s += "+---"
            s += "|\n"

        return s


    def set_value(self, x: int, y:int, value: np.int8 ):
        self.grid[x,y] = value

    def set_sun(self, x: int, y:int):
        self.set_value(x,y,1)

    def set_moon(self, x: int, y:int):
        self.set_value(x,y,-1)

    def extract_row(self, row):
        return Line(self.grid[row,:])

    def extract_col(self, col):
        return Line(self.grid[:,col])

    def replace_row(self, row, lineobj):
        self.grid[row,:] = lineobj.line

    def replace_col(self, col, lineobj):
        self.grid[:, col] = lineobj.line

    def row_depend(self, row):
        query = np.logical_and( self.depend[:,0] == row, self.depend[:,2] == row)
        subdepend = self.depend[query]
        return [ dep[[1,3,4]] for dep in subdepend ]

    def col_depend(self, col):
        query = np.logical_and( self.depend[:,1] == col, self.depend[:,3] == col)
        subdepend = self.depend[query]
        return [ dep[[0,2,4]] for dep in subdepend ]

    def solve_row(self, row):
        rowdepend = self.row_depend(row)
        self.extract_row(row).solve(rowdepend).insert_row_in_grid(self,row)

    def solve_col(self, col):
        coldepend = self.col_depend(col)
        self.extract_col(col).solve(coldepend).insert_col_in_grid(self,col)

    def tbd(self):
        return sum(sum(self.grid == 0))

    def solve_step(self):
        for i in range(self.n):
            if debug: print(f"Row {i}:")
            self.solve_row(i)
            if debug: print(f"Col {i}:")
            self.solve_col(i)

    def solve(self):
        tbd_old = None
        tbd_new = self.tbd()
        while (tbd_new != tbd_old) and (tbd_new != 0):  # Iterate until no more changes
            tbd_old = tbd_new
            self.solve_step()
            tbd_new = self.tbd()
        if debug: print(self)
        return

