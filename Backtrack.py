import time
from SudokuBoard import SudokuBoard
from PerformanceMetrics import PerformanceMetrics

class BacktrackSolver:
    """
    Baseline brute-force backtracking Sudoku solver.

    Searches for empty cells and tries numbers sequentially from 1 to n^2,
    using recursion to backtrack whenever the current placement is invalid.
    """

    def __init__(self, board: SudokuBoard):
        """
        Initializes a solver with a SudokuBoard object
        :param board: A SudokuBoard instance (should be a copy of the original puzzle).

        """
        self.board = board
        self.steps = 0
        self.backtracks = 0

    def solve(self) -> bool:
        """
        A recursive backtracking function to solve the Sudoku board
        Algorithm Steps:
            1- The algorithm finds an empty cell, if any
            2- For the numbers from 1 to 9 sequentially, it checks whether the number is a valid option to be inserted
            3- After updating the board, the function recursively calls itself, passing the new board
            4- The function recursively tries to finish the solution by calling itself until reaching the final solution
                where all insertions are valid and no empty cell is remaining or where no valid solution is found after
                looping through all the numbers, in that case we're going to backtrack and reset the last inserted element to zero
        """

        empty = self.board.find_empty()

        if empty is None:  # recursion base case
            return True
        else:
            row, col = empty  # position of the empty cell

        for num in range(1, self.board.size + 1):

            if self.board.is_valid(row, col, num):
                self.board.board[row][col] = i
                self.steps += 1

                if self.solve():
                    return True

                self.board.board[row][col] = 0  # all options were exhausted, undo the last change
                self.backtracks += 1

        return False

    def run(self) -> PerformanceMetrics:
        """
        Run the solver and return performance metrics.
        :return: PerformanceMetrics object with steps, backtracks, and time (ms).
        """

        start = time.perf_counter()
        self.solve()
        elapsed_ms = (time.perf_counter() - start) * 1000

        return PerformanceMetrics(
            steps=self.steps,
            backtracks=self.backtracks,
            time_ms=elapsed_ms
        )
