"""Recompute all published numbers from the original Kaggle JSONL.

Requires numpy and scipy. Run from any working directory:
    python analysis/recompute.py
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import csv
import hashlib
import json

import numpy as np
from scipy.stats import t


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "mortal_benchmark_results.jsonl"
CSV_PATH = ROOT / "data" / "mortal_benchmark_summary.csv"
SUMMARY_PATH = ROOT / "data" / "summary.json"
EXPECTED_SHA256 = "9e09abc6d7eb373314f044faeeb7f6a1fe20ad6ac395fca4f5f581050c9d5fe9"
COMMIT = "0cff2b52982be5b1163aa9a62fb01f03ce91e0d2"
KEY = 9427144312314120477
SEEDS = set(range(10000, 12000, 10))
POINTS = np.array([90, 45, 0, -135], dtype=np.int64)
RANKS = np.array([1, 2, 3, 4], dtype=np.int64)


def load_pairs() -> dict[int, dict[str, dict]]:
    raw = RAW_PATH.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_SHA256, f"Unexpected raw data SHA-256: {digest}"
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    assert len(rows) == 400, f"Expected 400 direction records, got {len(rows)}"
    pairs: dict[int, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        seed = row["seed_start"]
        label = row["challenger"]
        assert seed in SEEDS and label in {"582500", "298k"}
        assert row["champion"] != label
        assert row["seed_count"] == 10 and sum(row["ranks"]) == 40
        assert row["key"] == KEY and row["commit"] == COMMIT
        assert label not in pairs[seed], f"Duplicate seed/direction: {seed}, {label}"
        pairs[seed][label] = row
    assert set(pairs) == SEEDS
    assert all(set(pair) == {"582500", "298k"} for pair in pairs.values())
    return pairs


def model_metrics(batch_ranks: np.ndarray) -> dict:
    counts = batch_ranks.sum(axis=0)
    games = int(counts.sum())
    return {
        "games": games,
        "rank_counts": counts.tolist(),
        "average_rank": float(counts @ RANKS / games),
        "rank_rates": (counts / games).tolist(),
        "rank_pt_per_game": float(counts @ POINTS / games),
    }


def main() -> None:
    pairs = load_pairs()
    seeds = sorted(pairs)
    a = np.array([pairs[seed]["582500"]["ranks"] for seed in seeds], dtype=np.int64)
    b = np.array([pairs[seed]["298k"]["ranks"] for seed in seeds], dtype=np.int64)
    models = {"582500": model_metrics(a), "298k": model_metrics(b)}
    assert all(model["games"] == 8000 for model in models.values())

    # Same paired-batch bootstrap as the Kaggle notebook.
    rng = np.random.default_rng(20260925)
    indices = rng.integers(0, len(seeds), size=(5000, len(seeds)))
    aa, bb = a[indices].sum(axis=1), b[indices].sum(axis=1)
    pt_draws = aa @ POINTS / aa.sum(axis=1) - bb @ POINTS / bb.sum(axis=1)
    rank_draws = aa @ RANKS / aa.sum(axis=1) - bb @ RANKS / bb.sum(axis=1)

    # A model-based probability: normal batch-difference likelihood with
    # unknown mean and variance and reference prior p(mu,sigma^2) ∝ 1/sigma^2.
    batch_pt_differences = (a @ POINTS - b @ POINTS) / 40
    batch_mean = float(batch_pt_differences.mean())
    batch_se = float(batch_pt_differences.std(ddof=1) / np.sqrt(len(seeds)))
    probability_positive = float(t.cdf(batch_mean / batch_se, df=len(seeds) - 1))

    # Nonparametric sensitivity check using Dirichlet(1) batch weights.
    bb_rng = np.random.default_rng(20260927)
    positive = 0
    for _ in range(50):
        weights = bb_rng.exponential(size=(2000, len(seeds)))
        positive += int(np.count_nonzero(weights @ batch_pt_differences > 0))
    bayesian_bootstrap_probability = positive / 100000

    result = {
        "title": "Mortal 582500 vs 298k paired benchmark",
        "source_notebook": "https://www.kaggle.com/code/ess666/mortal-582500-vs-298k-benchmark?scriptVersionId=352932090",
        "raw_jsonl_sha256": EXPECTED_SHA256,
        "paired_batches": len(seeds),
        "games_per_model": 8000,
        "seed_range_inclusive": [10000, 11999],
        "points_by_rank": [90, 45, 0, -135],
        "models": models,
        "comparison_582500_minus_298k": {
            "average_rank_difference": models["582500"]["average_rank"] - models["298k"]["average_rank"],
            "rank_pt_difference": models["582500"]["rank_pt_per_game"] - models["298k"]["rank_pt_per_game"],
            "paired_bootstrap_95pct_rank_pt_interval": np.quantile(pt_draws, [0.025, 0.975]).tolist(),
            "paired_bootstrap_95pct_average_rank_interval": np.quantile(rank_draws, [0.025, 0.975]).tolist(),
            "posterior_probability_rank_pt_difference_positive": probability_positive,
            "bayesian_bootstrap_probability_rank_pt_difference_positive": bayesian_bootstrap_probability,
            "probability_scope": "Expected Rank PT under this 1-vs-3 arena protocol, not single-game win rate or universal strength.",
        },
    }

    # Compare our independent computation with Kaggle's exported CSV.
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as file:
        csv_rows = {row[""]: row for row in csv.DictReader(file)}
    for label in models:
        assert abs(float(csv_rows[label]["平均顺位"]) - models[label]["average_rank"]) < 1e-12
        assert abs(float(csv_rows[label]["Rank PT"]) - models[label]["rank_pt_per_game"]) < 1e-12

    SUMMARY_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["comparison_582500_minus_298k"], ensure_ascii=False, indent=2))
    print(f"Verified {len(seeds)} pairs, 8000 games per model, and original Kaggle CSV.")


if __name__ == "__main__":
    main()
