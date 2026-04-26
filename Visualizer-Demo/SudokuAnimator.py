import tkinter as tk
from SudokuBoard import SudokuBoard
from Backtrack import VisualBacktrackSolver
from MRV import  VisualMRVSolver
from ConstraintPropagation import VisualCSPSolver
import copy

CELL_SIZE = 55

class SudokuAnimator:
    def __init__(self, root, board, solver_class, delay=80):
        self.root = root
        self.board = board
        self.original = copy.deepcopy(board.board)

        self.solver = solver_class(board)
        self.steps = self.solver.solve_steps()

        self.delay = delay

        self.canvas = tk.Canvas(root, width=9 * CELL_SIZE, height=9 * CELL_SIZE)
        self.canvas.pack()

        self.status = tk.Label(root, text="Starting...", font=("New Courier", 12))
        self.status.pack()

        self.metrics = tk.Label(root, text="Steps: 0 | Backtracks: 0", font=("New Courier", 12, "bold"))
        self.metrics.pack()

        self.draw_board()
        self.root.after(500, self.animate)

    def draw_board(self, highlight=None, color="yellow"):
        self.canvas.delete("all")

        for row in range(9):
            for col in range(9):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                fill = "white"
                if highlight == (row, col):
                    fill = color

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="gray")

                value = self.board.board[row][col]
                if value != 0:
                    text_color = "gray10" if self.original[row][col] != 0 else "MediumOrchid2"

                    self.canvas.create_text(
                        x1 + CELL_SIZE / 2,
                        y1 + CELL_SIZE / 2,
                        text=str(value),
                        font=("New Courier", 20, "bold"),
                        fill=text_color
                    )

        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            self.canvas.create_line(i * CELL_SIZE, 0, i * CELL_SIZE, 9 * CELL_SIZE, width=width)
            self.canvas.create_line(0, i * CELL_SIZE, 9 * CELL_SIZE, i * CELL_SIZE, width=width)

    def update_metrics(self):
        self.metrics.config(
            text=f"Steps: {self.solver.steps} | Backtracks: {self.solver.backtracks}"
        )

    def animate(self):
        try:
            event, row, col, value = next(self.steps)

            if event == "try":
                self.status.config(text=f"Trying {value} at row {row + 1}, column {col + 1}")
                self.draw_board((row, col), "yellow")

            elif event == "place":
                self.status.config(text=f"Placed {value} at row {row + 1}, column {col + 1}")
                self.draw_board((row, col), "lightgreen")

            elif event == "backtrack":
                self.status.config(text=f"Backtracking from row {row + 1}, column {col + 1}")
                self.draw_board((row, col), "salmon")

            elif event == "select_mrv":
                self.status.config(text=f"MRV selected row {row + 1}, column {col + 1}")
                self.draw_board((row, col), "lightblue")

            elif event == "propagate":
                self.status.config(text=f"Constraint propagation placed {value} at row {row + 1}, column {col + 1}")
                self.draw_board((row, col), "lightgreen")

            elif event == "reduce":
                self.status.config(text=f"Removed candidate {value} from row {row + 1}, column {col + 1}")
                self.draw_board((row, col), "yellow")

            elif event == "guess":
                self.status.config(text=f"CSP guessing {value} at row {row + 1}, column {col + 1}")
                self.draw_board((row, col), "lightblue")

            elif event == "done":
                self.status.config(text="Solved!")
                self.draw_board()
                self.update_metrics()
                return

            self.update_metrics()
            self.root.after(self.delay, self.animate)

        except StopIteration:
            self.status.config(text="Finished.")
            self.draw_board()
            self.update_metrics()

#Change the board from here. You can use any LLM to generate a new board for you.

puzzle = SudokuBoard()
puzzle.board = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9],
]

root = tk.Tk()
root.title("Backtracking Sudoku Animation")

app = SudokuAnimator(
    root=root,
    board=puzzle,
    solver_class=VisualCSPSolver, #change algorithm here
    delay=20 #speed
)

root.mainloop()
