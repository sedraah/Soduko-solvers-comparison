# Sudoku Solvers Comparison

A benchmarking framework that implements and compares three Sudoku-solving algorithms: Baseline Backtracking, MRV + Backtracking, and Constraint Propagation across varying difficulty levels, measuring execution time, steps, and backtracks over 500 independent runs per configuration.

---

## Table of Contents

- [Overview](#overview)
- [Algorithms](#algorithms)
- [System Design](#system-design)
- [Project Structure](#project-structure)
- [References](#references)

---

## Overview

Sudoku is an NP-complete combinatorial puzzle on a generalized 9×9 grid, making it an ideal benchmark for comparing constraint satisfaction algorithms. This project implements three solvers from scratch in Python and evaluates them empirically across puzzle difficulties ranging from 40 clues (easy) down to 17 clues.

---

## Algorithms

### 1. Baseline Backtracking
A brute-force approach that fills empty cells sequentially (top-left to bottom-right), trying digits 1–9 and backtracking when no valid placement exists.

- **Time complexity:** O(9^k) worst case, where k = number of empty cells (k ≤ 81)
- **Space complexity:** O(k) — recursion stack depth

### 2. Backtracking with MRV Heuristic
Enhances backtracking by always selecting the most constrained cell (fewest remaining legal values) next, causing invalid branches to be detected earlier and significantly reducing the search space.

- **Time complexity:** O(9^k) worst case, but O(b^k') average where b ≪ 9 and k' ≪ k
- **Per-step overhead:** O(n⁴) for MRV cell selection vs O(n²) for baseline
- **Space complexity:** O(k)

### 3. Constraint Propagation (CSP-based)
Inspired by [Peter Norvig's solver](https://norvig.com/sudoku.html). Maintains a set of possible values per cell and applies two propagation rules before resorting to search:

1. **Single Value Rule:** if a cell has one possible value, assign it and eliminate from all peers
2. **Single Position Rule:** if a digit can only go in one place in a unit, assign it there

If propagation alone doesn't solve the puzzle, depth-first search with MRV is used as a fallback.

- **Time complexity:** O(n⁴) best/average case (propagation only); O(n^(n²)) worst case (rare)
- **Space complexity:** O(n²)

---

## System Design

### Puzzle Generation (`SudokuBoard`)
1. Generate a complete valid board using randomized backtracking
2. Remove cells one at a time, verifying uniqueness after each removal via `count_solutions(limit=2)`
3. Restore a cell if removal creates multiple solutions
4. Continue until the target clue count is reached

This guarantees every puzzle is **well-posed** (exactly one valid solution).

### Benchmarking Framework
- **Outer loop:** iterates over clue counts from 40 → 17
- **Inner loop:** generates and solves 500 independent puzzles per clue count
- Each run produces a `PerformanceMetrics` object (time, steps, backtracks)
- `MetricsCollector` aggregates mean, max, and standard deviation per configuration
- Results exported as text files and matplotlib line charts

### Performance Metrics

| Metric | Description |
|---|---|
| Execution Time (ms) | Wall-clock time from solver start to solution |
| Steps | Number of cell assignments attempted |
| Backtracks | Number of times the solver reversed a decision |


---

## References

1. S. Yakut and E. Karagoz, "A graph-theoretic solution to NP-complete Sudoku puzzles," *IEEE Access*, 2025.
2. T. Yato and T. Seta, "Complexity and completeness of finding another solution," *IEICE Transactions*, 2003.
3. N. M. H. Ismail and M. G. H. Omran, "Beyond significance: Promoting effect size measures," *Algorithms*, 2026.
4. A. Bhattarai et al., "A study of Sudoku solving algorithms: Backtracking and heuristic," *arXiv*, 2025.
5. S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Pearson, 2020.
6. P. Norvig, "Solving every Sudoku puzzle," norvig.com, 2006. https://norvig.com/sudoku.html
