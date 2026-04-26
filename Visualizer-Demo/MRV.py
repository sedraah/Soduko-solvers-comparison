from Backtrack import BacktrackSolver
from Backtrack import VisualBacktrackSolver

class MRVSolver(BacktrackSolver):
    """
    MRV-enhanced backtracking Sudoku solver.

    Inherits everything from BacktrackSolver.
    Only overrides solve() to use MRV cell selection
    instead of the first-empty-cell strategy.
    """

    def find_empty_mrv(self):
        """
        Scans all empty cells and returns the one with the
        fewest legal values remaining (Most Constrained Variable).

        Returns:
            (row, col) → best cell to fill next
            None       → no empty cells, board is complete
            (-1, -1)   → a cell has 0 legal values, dead end
        """
        min_count = float('inf')
        best_cell = None

        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.board[i][j] == 0:
                    count = sum(
                        1 for num in range(1, self.board.size + 1)
                        if self.board.is_valid(i, j, num)
                    )
                    if count == 0:
                        return (-1, -1)       # dead end detected early
                    if count < min_count:
                        min_count = count
                        best_cell = (i, j)

        return best_cell  # None if no empty cells found

    def solve(self) -> bool:
        """
        Same recursive backtracking as BacktrackSolver,
        but uses find_empty_mrv() instead of find_empty().
        """
        empty = self.find_empty_mrv()

        if empty is None:      return True   # board complete
        if empty == (-1, -1):  return False  # dead end, backtrack

        row, col = empty

        for num in range(1, self.board.size + 1):
            if self.board.is_valid(row, col, num):
                self.board.board[row][col] = num
                self.steps += 1

                if self.solve():
                    return True

                self.board.board[row][col] = 0   # undo, backtrack
                self.backtracks += 1

        return False

    # run() is fully inherited from BacktrackSolver, nothing to add

class VisualMRVSolver(VisualBacktrackSolver):

    def find_empty_mrv(self):
        min_count = float("inf")
        best_cell = None

        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.board.board[row][col] == 0:
                    count = sum(
                        1 for num in range(1, self.board.size + 1)
                        if self.board.is_valid(row, col, num)
                    )

                    if count == 0:
                        return (-1, -1)

                    if count < min_count:
                        min_count = count
                        best_cell = (row, col)

        return best_cell

    def solve_steps(self):
        empty = self.find_empty_mrv()

        if empty is None:
            yield ("done", None, None, None)
            return True

        if empty == (-1, -1):
            return False

        row, col = empty
        yield ("select_mrv", row, col, None)

        for num in range(1, self.board.size + 1):
            yield ("try", row, col, num)

            if self.board.is_valid(row, col, num):
                self.board.board[row][col] = num
                self.steps += 1
                yield ("place", row, col, num)

                solved = yield from self.solve_steps()
                if solved:
                    return True

                self.board.board[row][col] = 0
                self.backtracks += 1
                yield ("backtrack", row, col, 0)

        return False