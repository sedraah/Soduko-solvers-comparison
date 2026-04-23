from PerformanceMetrics import PerformanceMetrics
import time


def solve_constraint_propagation(board):
    """
    Solves a Sudoku puzzle using:
    - Backtracking search (DFS)
    - Constraint propagation (forward checking + arc consistency style)
    - MRV heuristic (Minimum Remaining Values)

    Returns:
        solved_board (SudokuBoard): solved puzzle
        metrics (PerformanceMetrics): performance stats (steps, backtracks, time)
    """
    start_time = time.time()
    steps = [0]
    backtracks = [0]

    # Convert board to dictionary of possible values
    values = board_to_values(board)

    # Solve using constraint propagation + search
    result = search(values, board.size, board.box_size, steps, backtracks)

    time_ms = (time.time() - start_time) * 1000

    # Convert CSP's solution back to board
    solved_board = board.copy()
    if result:
        for key, val in result.items():
            row, col = key
            solved_board.board[row][col] = int(val)

    metrics = PerformanceMetrics(steps[0], backtracks[0], time_ms)
    return solved_board, metrics


def board_to_values(board):
    """
    Convert board to dictionary of possible values.
    Each cell is mapped to a string of possible values:
    - Filled cells: single value (e.g., "5")
    - Empty cells: all possible digits ("123456789")

    Args:
        board (SudokuBoard): input Sudoku grid

    Returns:
        dict: {(row, col): "possible values"}
    """
    values = {}
    size = board.size

    for r in range(size):
        for c in range(size):
            if board.board[r][c] != 0:
                # Cell is filled
                values[(r, c)] = str(board.board[r][c])
            else:
                # Cell is empty - all values possible initially
                values[(r, c)] = ''.join(str(i) for i in range(1, size + 1))

    return values


def get_peers(row, col, size, box_size):
    """
    Returns all peer cells that share:
    - Same row
    - Same column
    - Same 3x3 box

    Args:
        row (int): row index
        col (int): column index
        size (int): board size (n^2)
        box_size (int): subgrid size (n)

    Returns:
        set of (row, col) tuples
    """
    peers = set()

    # Same row peers
    for c in range(size):
        if c != col:
            peers.add((row, c))

    # Same column peers
    for r in range(size):
        if r != row:
            peers.add((r, col))

    # Same box peers
    box_row = (row // box_size) * box_size
    box_col = (col // box_size) * box_size
    for r in range(box_row, box_row + box_size):
        for c in range(box_col, box_col + box_size):
            if (r, c) != (row, col):
                peers.add((r, c))

    return peers


def assign(values, cell, digit, size, box_size):
    """
    Assign a digit to a cell and propagate constraints.
    Eliminate all other values from this cell, then propagate.
    Returns updated values dict, or False if contradiction detected.

     Args:
        values (dict): CSP state
        cell (tuple): (row, col)
        digit (str): value to assign

    Returns:
        dict or False: updated CSP state or failure
    """
    other_values = values[cell].replace(digit, '')

    # Eliminate all other values from this cell
    for other_digit in other_values:
        if not eliminate(values, cell, other_digit, size, box_size):
            return False

    return values


def eliminate(values, cell, digit, size, box_size):
    """
    Eliminate digit from values[cell] and propagate constraints.

    Two constraint propagation rules:
    1. If a cell has only one possible value, eliminate that value from peers
    2. If a constraint (row/col/box) has only one place for a value, put it there

    Returns:
        dict or False: updated CSP state or failure
    """
    if digit not in values[cell]:
        return values  # Already eliminated

    values[cell] = values[cell].replace(digit, '')

    # Contradiction: no possible values left for this cell
    if len(values[cell]) == 0:
        return False

    # Rule 1: If cell has only one value left, eliminate it from peers
    if len(values[cell]) == 1:
        remaining_digit = values[cell]
        peers = get_peers(cell[0], cell[1], size, box_size)
        for peer in peers:
            if not eliminate(values, peer, remaining_digit, size, box_size):
                return False

    # Rule 2: If digit now appears in only one place in a unit, put it there
    for unit in get_units(cell, size, box_size):
        # Find cells in this unit that can still have this digit
        places = [c for c in unit if digit in values[c]]

        # Contradiction: no place for this digit
        if len(places) == 0:
            return False

        # Only one place, assign it
        elif len(places) == 1:
            if not assign(values, places[0], digit, size, box_size):
                return False

    return values


def get_units(cell, size, box_size):
    """
    Get all units (row, column, box) that contain this cell.
    Args:
        cell (tuple): (row, col)
        size (int): board size
        box_size (int): subgrid size

    Returns:
        list of lists of cells
    """
    row, col = cell
    units = []

    # Row unit
    row_unit = [(row, c) for c in range(size)]
    units.append(row_unit)

    # Column unit
    col_unit = [(r, col) for r in range(size)]
    units.append(col_unit)

    # Box unit
    box_row = (row // box_size) * box_size
    box_col = (col // box_size) * box_size
    box_unit = [(r, c) for r in range(box_row, box_row + box_size)
                for c in range(box_col, box_col + box_size)]
    units.append(box_unit)

    return units


def search(values, size, box_size, steps, backtracks):
    """
    Search using depth-first search with:
    - MRV heuristic (choose most constrained cell)
    - Constraint propagation (via assign/eliminate)
    - Backtracking on failure

     Args:
        values (dict): CSP state
        size (int): board size
        box_size (int): subgrid size
        steps (list): step counter
        backtracks (list): backtrack counter

    Returns:
        dict or False: solved CSP or failure
    """
    steps[0] += 1

    # First, propagate constraints from initial state
    if values is False:
        return False

    # Check if solved
    if all(len(values[cell]) == 1 for cell in values):
        return values

    # Choose unfilled cell with minimum remaining values (via MRV heuristic)
    min_len = size + 1
    best_cell = None
    for cell in values:
        if len(values[cell]) > 1 and len(values[cell]) < min_len:
            min_len = len(values[cell])
            best_cell = cell

    if best_cell is None:
        return False

    # Try each possible value for this cell
    for digit in values[best_cell]:
        # Make a copy and try this value assignment
        new_values = {k: v for k, v in values.items()}

        # Assign and propagate
        result = assign(new_values, best_cell, digit, size, box_size)

        if result is not False:
            # Recurse
            solution = search(result, size, box_size, steps, backtracks)
            if solution:
                return solution

        # Backtrack
        backtracks[0] += 1

    return False