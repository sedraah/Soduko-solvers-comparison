"""
main.py
-------
CCS 270 – Data Structures and Algorithms
Empirical Performance Analysis of Sudoku Solving Algorithms

Experimental Setup  
--------------------------------------------------
  Input sizes : num_clues from 50 down to 17  
  Runs/size   : generates RUNS_PER_SIZE independent puzzles per clue count
  Solvers     : Backtracking | MRV + Backtracking | Constraint Propagation

Outputs
-------
  Files    : {SolverName}ExecutionData.txt   — one per solver
             timeLineChart.png               — avg execution time comparison
             stepsLineChart.png              — avg steps comparison
             backtracksLineChart.png         — avg backtracks comparison
"""

import os

from SudokuBoard import SudokuBoard
from Backtrack import BacktrackSolver
from MRV import MRVSolver
from ConstraintPropagation import solve_constraint_propagation
from PerformanceMetrics import (
    PerformanceMetrics,
    MetricsCollector,
    EmpiricalResults,
    plot_comparison_charts,
)

# ── Experiment parameters (same as TestBacktracking.py) ───────────────────────
NUM_CLUES_RANGE = range(50, 20, -2)   # 50 clues (easy) → 17 clues (hard)
RUNS_PER_SIZE   = 100                  # independent puzzles per clue count
OUTPUT_DIR      = "results"           # folder for all saved files


# ── Solver registry ────────────────────────────────────────────────────────────
# Each entry: (display_name, callable)
# The callable receives a SudokuBoard and returns a PerformanceMetrics object.

def _run_backtrack(board: SudokuBoard) -> PerformanceMetrics:
    solver = BacktrackSolver(board)
    return solver.run()


def _run_mrv(board: SudokuBoard) -> PerformanceMetrics:
    solver = MRVSolver(board)
    return solver.run()


def _run_constraint(board: SudokuBoard) -> PerformanceMetrics:
    _solved_board, metrics = solve_constraint_propagation(board)
    return metrics


SOLVERS = [
    ("Backtracking",           _run_backtrack),
    ("MRV + Backtracking",     _run_mrv),
    ("Constraint Propagation", _run_constraint),
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def print_banner(title: str):
    width = 66
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def benchmark_solver( solver_name: str, solver_fn, generator: SudokuBoard) -> EmpiricalResults:
    """
    Run *solver_fn* across all clue counts in NUM_CLUES_RANGE.
    For each clue count, generate RUNS_PER_SIZE fresh puzzles and collect
    metrics, then aggregate into an EmpiricalResults object.

    Parameters
    ----------
    solver_name : str
        Display name used in tables and chart legend.
    solver_fn : callable
        Function(SudokuBoard) → PerformanceMetrics.
    generator : SudokuBoard
        Board generator instance (stateless across calls).

    Returns
    -------
    EmpiricalResults populated with one entry per clue count.
    """
    print_banner(f"{solver_name} — Empirical Analysis")
    emp = EmpiricalResults(algorithm_name=solver_name)

    for num_clues in NUM_CLUES_RANGE:
        print(f"  [Clues: {num_clues:>2}]", end="  ", flush=True)
        collector = MetricsCollector()

        for run in range(1, RUNS_PER_SIZE + 1):
            board = generator.generate_puzzle(num_clues)

            metrics = solver_fn(board)
            collector.add_run(metrics)

            # Inline progress dot
            print(".", end="", flush=True)

        emp.add(num_clues, collector)
        stats = collector.get_statistics()
        print(
            f"  avg={stats['time_ms']['avg']:.3f} ms  "
            f"steps={stats['steps']['avg']:.0f}  "
            f"bt={stats['backtracks']['avg']:.0f}"
        )

    return emp


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print_banner("Sudoku Algorithm — Empirical Performance Benchmark")
    print(
        f"\n  Clue range : {max(NUM_CLUES_RANGE)} → {min(NUM_CLUES_RANGE)}  "
        f"(step −1)\n"
        f"  Runs/size  : {RUNS_PER_SIZE}\n"
        f"  Output dir : {OUTPUT_DIR!r}\n"
    )

    generator = SudokuBoard()
    results_by_solver: dict[str, EmpiricalResults] = {}

    # ── Run all solvers ────────────────────────────────────────────────────────
    for name, fn in SOLVERS:
        emp = benchmark_solver(name, fn, generator)
        results_by_solver[name] = emp

    # ── Print tables and save execution-data files ─────────────────────────────
    print_banner("Results Summary")
    for name, emp in results_by_solver.items():
        emp.print_table()
        emp.save_to_file(output_dir=OUTPUT_DIR)

    # ── Save comparison line charts ────────────────────────────────────────────
    print_banner("Generating Comparison Charts")
    plot_comparison_charts(
        results_by_solver,
        stat       = "avg",
        output_dir = OUTPUT_DIR,
    )

    print_banner("Benchmark Complete")
    print(f"\n  All outputs written to: {os.path.abspath(OUTPUT_DIR)}\n")


if __name__ == "__main__":
    main()
