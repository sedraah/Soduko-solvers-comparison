import copy

from PerformanceMetrics import PerformanceMetrics
import time

# Precompute structure (GLOBAL)

ROWS = "ABCDEFGHI"
COLS = "123456789"

def cross(A, B):
    return [a + b for a in A for b in B]

CELLS = cross(ROWS, COLS)

UNITLIST = (
    [cross(ROWS, c) for c in COLS] +  # columns
    [cross(r, COLS) for r in ROWS] +  # rows
    [cross(rs, cs) for rs in ("ABC","DEF","GHI")
                    for cs in ("123","456","789")]  # boxes
)

UNITS = {s: [u for u in UNITLIST if s in u] for s in CELLS}
PEERS = {s: set(sum(UNITS[s], [])) - {s} for s in CELLS}

# Conversion helpers

def cell_to_row_col(cell):
    row = ROWS.index(cell[0])
    col = COLS.index(cell[1])
    return row, col

def board_to_grid_string(board):
    """
    Convert SudokuBoard → string of 81 chars
    (row-major, 0 -> '.')
    """
    chars = []
    for r in range(board.size):
        for c in range(board.size):
            val = board.board[r][c]
            chars.append(str(val) if val != 0 else ".")
    return "".join(chars)


def grid_values(grid):
    """
    Map grid string → {cell: value}
    """
    return dict(zip(CELLS, grid))


# ==============================
# Core CSP operations
# ==============================

def assign(values, s, d, steps):
    """
    Assign digit d to cell s and propagate constraints.
    """
    steps[0] += 1  # count assignments

    other = values[s].replace(d, "")
    for d2 in other:
        if not eliminate(values, s, d2, steps):
            return False
    return values


def eliminate(values, s, d, steps):
    """
    Eliminate digit d from cell s and propagate.
    """
    if d not in values[s]:
        return values

    values[s] = values[s].replace(d, "")

    # contradiction: no values left
    if len(values[s]) == 0:
        return False

    # If only one value remains → eliminate from peers
    if len(values[s]) == 1:
        d2 = values[s]
        for p in PEERS[s]:
            if not eliminate(values, p, d2, steps):
                return False

    # Only place for digit in unit
    for u in UNITS[s]:
        places = [s2 for s2 in u if d in values[s2]]

        if len(places) == 0:
            return False
        elif len(places) == 1:
            if not assign(values, places[0], d, steps):
                return False

    return values

# Search (MRV + propagation)

def search(values, steps, backtracks):
    """
    Depth-first search with MRV + constraint propagation
    """
    if values is False:
        return False

    # solved
    if all(len(values[s]) == 1 for s in CELLS):
        return values

    # MRV: choose most constrained variable
    _, s = min((len(values[s]), s) for s in CELLS if len(values[s]) > 1)

    for d in values[s]:
        new_values = values.copy()

        result = assign(new_values, s, d, steps)
        if result:
            attempt = search(result, steps, backtracks)
            if attempt:
                return attempt

        backtracks[0] += 1

    return False

# Main solver function


def solve_constraint_propagation(board) -> PerformanceMetrics:
    """
    Constraint Propagation Sudoku solver heavily inspired by Peter Norvig's solver.

    Returns:
        PerformanceMetrics only (consistent with other solvers)
    """
    start_time = time.perf_counter()

    steps = [0]
    backtracks = [0]

    # Convert board → grid string
    grid = board_to_grid_string(board)

    # Initialize domains
    values = {s: "123456789" for s in CELLS}

    # Initial constraint propagation
    for s, d in grid_values(grid).items():
        if d in "123456789":
            if not assign(values, s, d, steps):
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                return PerformanceMetrics(steps[0], backtracks[0], elapsed_ms)

    # Search
    result = search(values, steps, backtracks)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return PerformanceMetrics(
        steps=steps[0],
        backtracks=backtracks[0],
        time_ms=elapsed_ms
    )

class VisualCSPSolver:
    def __init__(self, board):
        self.board = board
        self.steps = 0
        self.backtracks = 0
        self.values = {s: "123456789" for s in CELLS}

    def board_to_grid_string(self):
        chars = []

        for row in range(self.board.size):
            for col in range(self.board.size):
                value = self.board.board[row][col]
                chars.append(str(value) if value != 0 else ".")

        return "".join(chars)

    def grid_values(self):
        return dict(zip(CELLS, self.board_to_grid_string()))

    def assign_steps(self, values, s, d):
        self.steps += 1

        other_values = values[s].replace(d, "")

        for d2 in other_values:
            result = yield from self.eliminate_steps(values, s, d2)
            if not result:
                return False

        return values

    def eliminate_steps(self, values, s, d):
        if d not in values[s]:
            return values

        values[s] = values[s].replace(d, "")

        row, col = cell_to_row_col(s)
        yield ("reduce", row, col, int(d))

        if len(values[s]) == 0:
            return False

        if len(values[s]) == 1:
            d2 = values[s]
            row, col = cell_to_row_col(s)

            if self.board.board[row][col] == 0:
                self.board.board[row][col] = int(d2)
                self.steps += 1
                yield ("propagate", row, col, int(d2))

            for peer in PEERS[s]:
                result = yield from self.eliminate_steps(values, peer, d2)
                if not result:
                    return False

        for unit in UNITS[s]:
            places = [cell for cell in unit if d in values[cell]]

            if len(places) == 0:
                return False

            elif len(places) == 1:
                result = yield from self.assign_steps(values, places[0], d)
                if not result:
                    return False

        return values

    def search_steps(self, values):
        if values is False:
            return False

        if all(len(values[s]) == 1 for s in CELLS):
            yield ("done", None, None, None)
            return True

        _, s = min((len(values[s]), s) for s in CELLS if len(values[s]) > 1)

        row, col = cell_to_row_col(s)

        for d in values[s]:
            old_board = copy.deepcopy(self.board.board)
            new_values = values.copy()

            yield ("guess", row, col, int(d))

            result = yield from self.assign_steps(new_values, s, d)

            if result:
                solved = yield from self.search_steps(result)
                if solved:
                    return True

            self.board.board = old_board
            self.backtracks += 1
            yield ("backtrack", row, col, 0)

        return False

    def solve_steps(self):
        grid = self.grid_values()

        for s, d in grid.items():
            if d in "123456789":
                result = yield from self.assign_steps(self.values, s, d)

                if not result:
                    return False

        solved = yield from self.search_steps(self.values)

        if solved:
            return True

        return False