"""
This file is responsible for measuring performance and reporting results.

Metrics Stored:
steps = how many assignments/operations the solver counted.
backtracks = how many times the solver had to undo all their assignments due to invalid moves
time_ms = how long the solver took in milliseconds

Classes:
PerformanceMetrics = stores metrics for a single solver run.
MetricsCollector = aggregates runs for one (solver, input-size) pair
EmpiricalResults = aggregates MetricCollectors across input sizes for one solver.

The output result is a table with the metrics for each algorithm then three charts
comparing each metric across the three algorithms.
"""

import statistics
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from typing import List

class PerformanceMetrics:
    """
    Store performance metrics for a single algorithm run.
    """

    def __init__(self, steps: int = 0, backtracks: int = 0, time_ms: float = 0.0):
        self.steps      = steps
        self.backtracks = backtracks
        self.time_ms    = time_ms


class MetricsCollector:
    """
    Collect and aggregate PerformanceMetrics across multiple runs.
    """

    def __init__(self):
        self.runs: List[PerformanceMetrics] = []

    def add_run(self, metrics: PerformanceMetrics):
        self.runs.append(metrics)

    def get_statistics(self) -> dict | None:
        """
        returns: max (worst-case), average, and standard deviation for each of the three metrics.
        """
        if not self.runs:
            return None

        def _stats(data: list) -> dict:
            return {
                'max':   max(data),
                'avg':   statistics.mean(data),
                'stdev': statistics.stdev(data) if len(data) > 1 else 0.0,
            }

        return {
            'time_ms':    _stats([r.time_ms    for r in self.runs]),
            'steps':      _stats([r.steps      for r in self.runs]),
            'backtracks': _stats([r.backtracks for r in self.runs]),
        }


class EmpiricalResults:
    """
    Aggregate MetricsCollector results across multiple input sizes for one
    solver algorithm.
    """

    def __init__(self, algorithm_name: str = "Algorithm"):
        self.algorithm_name = algorithm_name
        # list of (num_clues, stats_dict) in insertion order
        self._rows: list[tuple[int, dict]] = []

    def add(self, num_clues: int, collector: MetricsCollector):
        stats = collector.get_statistics()
        if stats:
            self._rows.append((num_clues, stats))

    # Helper Function to create table
    def _build_table_lines(self) -> list[str]:
        """
        Return the full table as a list of printable strings.
        """
        if not self._rows:
            return ["No data to display."]

        col_w  = 10
        title  = f"  {self.algorithm_name} - Execution Data"

        header = (
            f"{'Clues':>6} | "
            f"{'Time Max':>{col_w}} | {'Time Avg':>{col_w}} | {'Time Std':>{col_w}} | "
            f"{'Steps Max':>{col_w}} | {'Steps Avg':>{col_w}} | {'Steps Std':>{col_w}} | "
            f"{'BT Max':>{col_w}} | {'BT Avg':>{col_w}} | {'BT Std':>{col_w}}"
        )
        sep    = "=" * len(header)
        sub    = f"{'':>6}   {'(ms)':>{col_w}}   {'(ms)':>{col_w}}   {'(ms)':>{col_w}}   " \
                 f"{'':>{col_w}}   {'':>{col_w}}   {'':>{col_w}}   " \
                 f"{'':>{col_w}}   {'':>{col_w}}   {'':>{col_w}}"

        lines = [sep, title, sep, header, sub, "-" * len(header)]

        for num_clues, stats in self._rows:
            t = stats['time_ms']
            s = stats['steps']
            b = stats['backtracks']
            lines.append(
                f"{num_clues:>6} | "
                f"{t['max']:>{col_w}.4f} | {t['avg']:>{col_w}.4f} | {t['stdev']:>{col_w}.4f} | "
                f"{s['max']:>{col_w}.0f} | {s['avg']:>{col_w}.2f} | {s['stdev']:>{col_w}.2f} | "
                f"{b['max']:>{col_w}.0f} | {b['avg']:>{col_w}.2f} | {b['stdev']:>{col_w}.2f}"
            )

        lines.append(sep)
        return lines

    def print_table(self):
        """
        Print the results table to stdout.
        """
        print("\n" + "\n".join(self._build_table_lines()))

    def save_to_file(self, output_dir: str = "."):
        """
        Save the results table to a text file named
        {algorithm_name}ExecutionData.txt inside the output directory.
        """
        os.makedirs(output_dir, exist_ok=True)
        safe_name = self.algorithm_name.replace(" ", "_").replace("+", "Plus")
        path = os.path.join(output_dir, f"{safe_name}ExecutionData.txt")

        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self._build_table_lines()) + "\n")

        print(f"   Saved execution data to: {path}")
        return path


    # Data accessors used by the plotting function
    def clues(self) -> list[int]:
        return [r[0] for r in self._rows]

    def metric_series(self, metric: str, stat: str) -> list[float]:
        """
        Return a list of statistic values (max, avg, std) for metrics
        (time_ms,steps,backtracks) across all input sizes.
        """
        return [r[1][metric][stat] for r in self._rows]


    def empty_cells(self) -> list[int]:
        total = 81  # fixed Sudoku size
        return [total - r[0] for r in self._rows]


# Cross-solver Comparison Charts

# Colour palette and display names for the three expected solvers
_SOLVER_STYLES = {
    "Backtracking":          {"color": "#dc2626"},
    "MRV + Backtracking":    {"color": "#2563eb"},
    "Constraint Propagation":{"color": "#16a34a"},
}

_METRIC_META = {
    "time_ms": {
        "ylabel": "Execution Time (ms)",
        "title":  "Execution Time vs. Number of Empty Cells",
        "file":   "timeLineChart",
    },
    "steps": {
        "ylabel": "Steps",
        "title":  "Steps vs. Number of Empty Cells",
        "file":   "stepsLineChart",
    },
    "backtracks": {
        "ylabel": "Backtracks",
        "title":  "Backtracks vs. Number of Empty Cells",
        "file":   "backtracksLineChart",
    },
}


def plot_comparison_charts(
    results_by_solver: dict,   # {solver_name: EmpiricalResults}
    stat:         str  = "avg",
    output_dir:   str  = ".",
):
    """
    Produces one clustered line chart per metric comparing all solvers.

    Parameters
    ----------
    results_by_solver : dict
        Keys are solver display names (must match _SOLVER_STYLES keys).
        Values are EmpiricalResults objects.
    stat : str
        Which statistic to plot: 'avg', 'max', or 'stdev'.
    output_dir : str
        Directory in which to save the PNG files.
    """
    os.makedirs(output_dir, exist_ok=True)

    for metric, meta in _METRIC_META.items():
        fig, ax = plt.subplots(figsize=(11, 6))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#ffffff")

        for solver_name, emp_results in results_by_solver.items():
            style = _SOLVER_STYLES.get(
                solver_name,
                {"color": "#888888"},
            )
            clues = list(map(int, emp_results.empty_cells()))
            values = emp_results.metric_series(metric, stat)

            ax.plot(
                clues, values,
                color       = style["color"],
                linewidth   = 2.0,
                label       = solver_name,
            )

            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        ax.set_title(
            meta["title"],
            fontsize=14, fontweight="bold", color="#111111", pad=14,
        )
        ax.set_xlabel(
            "Number of Empty Cells",
            fontsize=11, color="#444444",
        )
        ax.set_ylabel(meta["ylabel"], fontsize=11, color="#444444")

        ax.tick_params(colors="#444444")
        for spine in ax.spines.values():
            spine.set_edgecolor("#cccccc")

        ax.grid(False)

        ax.legend(
            facecolor="#ffffff", edgecolor="#cccccc",
            labelcolor="#333333", fontsize=10,
        )

        plt.tight_layout()

        out_path = os.path.join(output_dir, f"{meta['file']}.png")
        plt.savefig(out_path, dpi=150, facecolor="#ffffff")
        plt.close(fig)
        print(f"   Saved chart: {out_path}")
