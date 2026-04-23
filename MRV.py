from Backtrack import BacktrackSolver


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

    def solve(self, board) -> bool:
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

                if self.solve(board):
                    return True

                self.board.board[row][col] = 0   # undo, backtrack
                self.backtracks += 1

        return False

    # run() is fully inherited from BacktrackSolver, nothing to add