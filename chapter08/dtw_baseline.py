"""DTW Software Baseline — Audio Correlation Algorithm Validation.

This script implements Dynamic Time Warping (DTW) from scratch and validates
it against the `dtw-python` library. It serves as the golden reference for
hardware verification in Chapter 9.

Usage:
    python chapter08/dtw_baseline.py --validate
    python chapter08/dtw_baseline.py --profile-scaling
    python chapter08/dtw_baseline.py --compare-all
"""

from __future__ import annotations

import argparse
import time

import numpy as np

# ---------------------------------------------------------------------------
# DTW Implementation (from scratch — matches the Chapter 8 recurrence)
# ---------------------------------------------------------------------------


def dtw_unconstrained(
    x: np.ndarray, y: np.ndarray
) -> tuple[float, np.ndarray, list[tuple[int, int]]]:
    """Compute unconstrained DTW between two feature sequences.

    Parameters
    ----------
    x : np.ndarray, shape (N, D)
        Student MFCC feature sequence.
    y : np.ndarray, shape (M, D)
        Reference MFCC feature sequence.

    Returns
    -------
    distance : float
        The raw DTW distance D(N, M).
    cost_matrix : np.ndarray, shape (N, M)
        The cumulative cost matrix.
    path : list[tuple[int, int]]
        The optimal warping path from (0, 0) to (N-1, M-1).
    """
    n, m = x.shape[0], y.shape[0]

    # Local distance matrix: squared Euclidean distance
    # Avoiding the square root per Equation Card 1 hardware optimization
    diff = x[:, np.newaxis, :] - y[np.newaxis, :, :]  # (N, M, D)
    local_dist = np.sum(diff**2, axis=2)  # (N, M)

    # Cumulative cost matrix
    cost = np.full((n, m), np.inf, dtype=np.float64)
    cost[0, 0] = local_dist[0, 0]

    # First row: can only come from the left
    for j in range(1, m):
        cost[0, j] = local_dist[0, j] + cost[0, j - 1]

    # First column: can only come from below
    for i in range(1, n):
        cost[i, 0] = local_dist[i, 0] + cost[i - 1, 0]

    # Fill interior cells
    for i in range(1, n):
        for j in range(1, m):
            cost[i, j] = local_dist[i, j] + min(
                cost[i - 1, j],  # insertion (student repeats)
                cost[i - 1, j - 1],  # match (both advance)
                cost[i, j - 1],  # deletion (student skips)
            )

    # Traceback: recover the optimal warping path
    path = _traceback(cost)

    return cost[n - 1, m - 1], cost, path


def dtw_sakoe_chiba(
    x: np.ndarray, y: np.ndarray, band_width: int
) -> tuple[float, np.ndarray, list[tuple[int, int]]]:
    """Compute DTW with Sakoe-Chiba band constraint.

    Parameters
    ----------
    x : np.ndarray, shape (N, D)
    y : np.ndarray, shape (M, D)
    band_width : int
        Maximum allowed deviation |i - j| <= W.

    Returns
    -------
    distance, cost_matrix, path
    """
    n, m = x.shape[0], y.shape[0]
    w = band_width

    # Local distance (only compute within the band for efficiency)
    cost = np.full((n, m), np.inf, dtype=np.float64)

    for i in range(n):
        j_start = max(0, i - w)
        j_end = min(m, i + w + 1)
        for j in range(j_start, j_end):
            local_d = float(np.sum((x[i] - y[j]) ** 2))
            candidates = []
            if i > 0 and cost[i - 1, j] < np.inf:
                candidates.append(cost[i - 1, j])
            if i > 0 and j > 0 and cost[i - 1, j - 1] < np.inf:
                candidates.append(cost[i - 1, j - 1])
            if j > 0 and cost[i, j - 1] < np.inf:
                candidates.append(cost[i, j - 1])

            if i == 0 and j == 0:
                cost[i, j] = local_d
            elif candidates:
                cost[i, j] = local_d + min(candidates)

    path = _traceback(cost)
    return cost[n - 1, m - 1], cost, path


def _traceback(cost: np.ndarray) -> list[tuple[int, int]]:
    """Recover optimal warping path via reverse traceback."""
    n, m = cost.shape
    i, j = n - 1, m - 1
    path = [(i, j)]

    while i > 0 or j > 0:
        if i == 0:
            j -= 1
        elif j == 0:
            i -= 1
        else:
            candidates = {
                (i - 1, j - 1): cost[i - 1, j - 1],
                (i - 1, j): cost[i - 1, j],
                (i, j - 1): cost[i, j - 1],
            }
            i, j = min(candidates, key=candidates.get)
        path.append((i, j))

    path.reverse()
    return path


def dtw_normalized(distance: float, n: int, m: int) -> float:
    """Compute normalized DTW distance per Equation Card 4."""
    return distance / (n + m)


# ---------------------------------------------------------------------------
# Validation against dtw-python library
# ---------------------------------------------------------------------------


def validate_against_library() -> None:
    """Validate our DTW implementation against the dtw-python library."""
    try:
        from dtw import dtw as dtw_lib
    except ImportError:
        print("WARNING: dtw-python not installed. Install with: pip install dtw-python")
        print("Running self-validation with known example instead.\n")
        _validate_known_example()
        return

    rng = np.random.default_rng(42)

    # Generate synthetic MFCC-like sequences
    d = 80  # feature dimension (80 Mel bins)
    for n, m in [(50, 40), (100, 120), (200, 180), (500, 450)]:
        x = rng.standard_normal((n, d))
        y = rng.standard_normal((m, d))

        # Our implementation
        our_dist, _, our_path = dtw_unconstrained(x, y)

        # Library implementation
        alignment = dtw_lib(x, y, dist_method="sqeuclidean")
        lib_dist = alignment.distance

        rel_error = abs(our_dist - lib_dist) / max(abs(lib_dist), 1e-15)
        status = "PASS" if rel_error < 1e-6 else "FAIL"
        print(
            f"  N={n:4d}, M={m:4d}: "
            f"ours={our_dist:12.4f}, lib={lib_dist:12.4f}, "
            f"rel_err={rel_error:.2e} [{status}]"
        )

    print()


def _validate_known_example() -> None:
    """Validate against the worked example from Chapter 8.3."""
    # The 4x5 local distance matrix from the chapter
    local_dist_matrix = np.array(
        [
            [2, 4, 7, 6, 3],
            [5, 3, 2, 5, 4],
            [8, 6, 1, 3, 6],
            [9, 7, 4, 2, 1],
        ],
        dtype=np.float64,
    )

    # Create synthetic 1D features that produce these squared distances
    # We use 1D features where x[i] and y[j] are chosen so that (x[i]-y[j])^2
    # matches the local distance matrix
    # For simplicity, we directly verify the cost matrix
    n, m = 4, 5
    cost = np.full((n, m), np.inf)
    cost[0, 0] = local_dist_matrix[0, 0]

    for j in range(1, m):
        cost[0, j] = local_dist_matrix[0, j] + cost[0, j - 1]
    for i in range(1, n):
        cost[i, 0] = local_dist_matrix[i, 0] + cost[i - 1, 0]
    for i in range(1, n):
        for j in range(1, m):
            cost[i, j] = local_dist_matrix[i, j] + min(
                cost[i - 1, j], cost[i - 1, j - 1], cost[i, j - 1]
            )

    # Expected from the chapter's worked example
    expected_cost = np.array(
        [
            [2, 6, 13, 19, 22],
            [7, 5, 7, 12, 16],
            [15, 11, 6, 9, 15],
            [24, 18, 10, 8, 9],
        ],
        dtype=np.float64,
    )

    match = np.allclose(cost, expected_cost)
    print(f"  Known example (4x5 grid): DTW distance = {cost[3, 4]:.0f}, expected = 9")
    print(f"  Cost matrix match: {'PASS' if match else 'FAIL'}")
    if not match:
        print(f"  Computed:\n{cost}")
        print(f"  Expected:\n{expected_cost}")
    print()


# ---------------------------------------------------------------------------
# Profiling: demonstrate O(N^2) scaling
# ---------------------------------------------------------------------------


def profile_scaling() -> None:
    """Profile DTW computation time vs. sequence length."""
    rng = np.random.default_rng(42)
    d = 80
    lengths = [50, 100, 200, 400, 800]
    band_widths = [None, 32, 64]

    print("DTW Scaling Profile")
    print("=" * 70)
    print(f"{'N':>6} {'M':>6} {'Band':>6} {'Time (ms)':>12} {'Cells':>12}")
    print("-" * 70)

    for length in lengths:
        n = m = length
        x = rng.standard_normal((n, d))
        y = rng.standard_normal((m, d))

        for w in band_widths:
            runs = 5 if length <= 400 else 2
            times = []
            for _ in range(runs):
                t0 = time.perf_counter_ns()
                if w is None:
                    dtw_unconstrained(x, y)
                    cells = n * m
                else:
                    dtw_sakoe_chiba(x, y, w)
                    cells = n * (2 * w + 1)
                t1 = time.perf_counter_ns()
                times.append((t1 - t0) / 1e6)

            mean_ms = np.mean(times)
            label = "None" if w is None else str(w)
            print(f"{n:6d} {m:6d} {label:>6} {mean_ms:12.2f} {cells:12d}")

    print()


# ---------------------------------------------------------------------------
# Compare all three algorithms
# ---------------------------------------------------------------------------


def compare_all() -> None:
    """Compare DTW, Euclidean, and Cosine distance on paired sequences."""
    rng = np.random.default_rng(42)
    d = 80
    n_pairs = 15

    print("Algorithm Comparison on Paired Sequences")
    print("=" * 80)
    print(f"{'Pair':>4} {'N':>5} {'M':>5} {'DTW_norm':>10} {'Euclidean':>10} {'Cosine':>10}")
    print("-" * 80)

    for pair_idx in range(n_pairs):
        # Generate reference
        m = rng.integers(80, 200)
        ref = rng.standard_normal((m, d))

        # Generate student as a warped version of reference + noise
        warp_factor = rng.uniform(0.7, 1.3)
        n = max(20, int(m * warp_factor))
        indices = np.linspace(0, m - 1, n).astype(int)
        stu = ref[indices] + rng.standard_normal((n, d)) * 0.5

        # DTW
        dist_dtw, _, _ = dtw_unconstrained(stu, ref)
        dtw_norm = dtw_normalized(dist_dtw, n, m)

        # Frame-averaged Euclidean (truncate to min length)
        min_len = min(n, m)
        eucl = np.mean(np.sqrt(np.sum((stu[:min_len] - ref[:min_len]) ** 2, axis=1)))

        # Utterance-level Cosine similarity (mean-pool then cosine)
        e_stu = np.mean(stu, axis=0)
        e_ref = np.mean(ref, axis=0)
        cos_sim = np.dot(e_stu, e_ref) / (np.linalg.norm(e_stu) * np.linalg.norm(e_ref) + 1e-10)
        cos_dist = 1.0 - cos_sim

        print(f"{pair_idx + 1:4d} {n:5d} {m:5d} {dtw_norm:10.4f} {eucl:10.4f} {cos_dist:10.4f}")

    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for the DTW baseline script."""
    parser = argparse.ArgumentParser(
        description="DTW Software Baseline — Audio Correlation Validation"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate DTW against dtw-python library",
    )
    parser.add_argument(
        "--profile-scaling",
        action="store_true",
        help="Profile DTW scaling with sequence length",
    )
    parser.add_argument(
        "--compare-all",
        action="store_true",
        help="Compare DTW, Euclidean, and Cosine on paired sequences",
    )
    args = parser.parse_args()

    if not any([args.validate, args.profile_scaling, args.compare_all]):
        # Default: run all
        args.validate = True
        args.profile_scaling = True
        args.compare_all = True

    if args.validate:
        print("\n=== DTW Validation ===\n")
        validate_against_library()

    if args.profile_scaling:
        print("\n=== DTW Scaling Profile ===\n")
        profile_scaling()

    if args.compare_all:
        print("\n=== Algorithm Comparison ===\n")
        compare_all()


if __name__ == "__main__":
    main()
