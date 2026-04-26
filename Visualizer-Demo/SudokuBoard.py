import random
import copy

class SudokuBoard:
    def __init__(self, n=3):
        """
        Initialize a Sudoku board of n * n random numbers.
        :param n: Board dimension (n = 3 for standard Sudoku)
        """
        # Size of each sub-grid
        self.box_size = n
        # Total board dimensions
        self.size = n * n
        #Initializes a board with all 0s
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]



    def is_valid(self, row, col, num):
        """
        Checks if the value placed in the board at [row][col] is valid.

        According to Sudoku rules a move is valid if:
        - The number does not already exist in the same row.
        - The number does not already exist in the same column.
        - The number does not already exist in the same square.
        :param self: Sudoku board object.
        :param row: Row in the sudoku board of length n.
        :param col: Column in the sudoku board of length n.
        :param num: The value placed and to be checked.
        :return: Returns True if the move is valid, False otherwise.
        """

        #If the value is found in the same row, then it is an illegal move.
        if num in self.board[row]:
            return False

        #If the value is found in the same column, then it is an illegal move.
        if num in [self.board[i][col] for i in range(self.size)]:
            return False

        #If the value is found in its 3x3 box, then it is an illegal move.
        box_row, box_col = (row // self.box_size) * self.box_size, (col // self.box_size) * self.box_size
        for i in range(box_row, box_row + self.box_size):
            for j in range(box_col, box_col + self.box_size):
                if self.board[i][j] == num:
                    return False

        return True

    def find_empty(self):
        """
        Finds the next empty cell in the board (empty here being defined as 0).
        :param self: Sudoku board object.
        :return: Returns (row, col) if empty cell exists or None if board is full.
        """

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return i, j
        return None

    """
    Since the same puzzle will be run on three different algorithms, each algorithm
    has to have its own copy of the original puzzle. In contrast to a regular copy, a deep copy
    copies also the elements within the board without affecting the original.
    """
    def copy(self):
        """
        Returns a deep copy of the board object.
        :return: copied new board.
        """
        new_board = SudokuBoard(self.box_size)
        new_board.board = copy.deepcopy(self.board)
        return new_board

    def display(self):
        """
        Prints the board.
        """
        for i in range(self.size):
            if i % self.box_size == 0 and i != 0:
                print("-" * (self.size * 2 + self.box_size - 1))

            for j in range(self.size):
                if j % self.box_size == 0 and j != 0:
                    print ("|", end=" ")
                print(self.board[i][j] if self.board[i][j] != 0 else ".", end=" ")
            print()

    def _fill_board(self):
        """
        Helper function for generate_puzzle() to create boards with valid solutions only.

        Steps:
        1. Find an empty cell
        2. Try numbers in random order
        3. Place a number if valid
        4. Recursively continue
        5. Backtrack if needed


        :return: True if board is successfully filled, False otherwise
        """

        #Base case: no empty cells, meaning that the board is full.
        empty = self.find_empty()
        if empty is None:
            return True

        row, col = empty

        # Generate different boards randomly
        numbers = list(range(1, self.size + 1))
        random.shuffle(numbers)

        for num in numbers:
            if self.is_valid(row, col, num):
                self.board[row][col] = num

                if self._fill_board():
                    return True

                self.board[row][col] = 0

        return False

    def count_solutions(self, limit=2):
        empty = self.find_empty()
        if empty is None:
            return 1

        row, col = empty
        count = 0

        for num in range(1, self.size + 1):
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                count += self.count_solutions(limit)
                self.board[row][col] = 0

                if count >= limit:
                    return count

        return count

    def generate_puzzle(self, clues):
        """
        Generate a valid Sudoku puzzle with a given number of clues.
        :parameter clues: Number of clues to generate the puzzle.
        :return:
        """


        #Fill the board completely
        self._fill_board()

        positions = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(positions)

        for row, col in positions:
            temp = self.board[row][col]
            self.board[row][col] = 0

            # Check if uniqueness is broken
            board_copy = self.copy()
            if board_copy.count_solutions(limit=2) != 1:
                self.board[row][col] = temp  # undo removal

            # Stop when desired number of clues reached
            filled = sum(cell != 0 for r in self.board for cell in r)
            if filled <= clues:
                break

        return self

