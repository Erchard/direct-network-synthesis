"""Run DAS-V0 exact spectral weighted-automaton reconstruction."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np

from dns.synthesis.weighted_automata import (
    all_words,
    hankel_matrix,
    max_absolute_error,
    random_stable_automaton,
    reconstruct_weighted_automaton,
)


def _word_to_text(word: tuple[str, ...]) -> str:
    return "".join(word) if word else "<empty>"


def _anbn_indicator(word: tuple[str, ...]) -> float:
    seen_b = False
    a_count = 0
    b_count = 0
    for symbol in word:
        if symbol == "a" and not seen_b:
            a_count += 1
        elif symbol == "b":
            seen_b = True
            b_count += 1
        else:
            return 0.0
    return float(a_count == b_count and a_count > 0)


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _run(config: dict[str, Any], command: list[str]) -> dict[str, Any]:
    alphabet = tuple(config["alphabet"])
    basis_max_length = int(config["basis_max_length"])
    heldout_max_length = int(config["heldout_max_length"])
    tolerance = float(config["rank_tolerance"])
    error_tolerance = float(config["error_tolerance"])
    basis_words = all_words(alphabet, basis_max_length)
    heldout_words = all_words(alphabet, heldout_max_length)

    finite_results = []
    for fixture in config["finite_rank_fixtures"]:
        teacher = random_stable_automaton(
            alphabet,
            state_count=int(fixture["state_count"]),
            seed=int(fixture["seed"]),
        )
        start = time.perf_counter()
        reconstruction = reconstruct_weighted_automaton(
            teacher.evaluate,
            alphabet,
            max_basis_length=basis_max_length,
            tolerance=tolerance,
        )
        synthesis_seconds = time.perf_counter() - start

        start = time.perf_counter()
        inferred = reconstruction.automaton.evaluate_many(heldout_words)
        inference_seconds = time.perf_counter() - start
        teacher_values = teacher.evaluate_many(heldout_words)
        heldout_error = float(np.max(np.abs(teacher_values - inferred)))
        basis_error = max_absolute_error(
            teacher.evaluate,
            reconstruction.automaton.evaluate,
            basis_words,
        )
        finite_results.append(
            {
                "name": fixture["name"],
                "teacher_state_count": int(fixture["state_count"]),
                "seed": int(fixture["seed"]),
                "selected_hankel_rank": reconstruction.basis.rank,
                "reconstructed_state_count": reconstruction.automaton.state_count,
                "prefix_count": len(reconstruction.basis.prefixes),
                "suffix_count": len(reconstruction.basis.suffixes),
                "prefixes": [_word_to_text(word) for word in reconstruction.basis.prefixes],
                "suffixes": [_word_to_text(word) for word in reconstruction.basis.suffixes],
                "candidate_count": reconstruction.basis.candidate_count,
                "singular_values": list(reconstruction.singular_values),
                "hankel_condition": reconstruction.hankel_condition,
                "basis_max_abs_error": basis_error,
                "heldout_max_abs_error": heldout_error,
                "heldout_word_count": len(heldout_words),
                "synthesis_seconds": synthesis_seconds,
                "inference_seconds": inference_seconds,
                "passed": bool(
                    reconstruction.basis.rank == int(fixture["state_count"])
                    and reconstruction.automaton.state_count == int(fixture["state_count"])
                    and heldout_error <= error_tolerance
                    and basis_error <= error_tolerance
                ),
            }
        )

    rank_windows = [int(value) for value in config["negative_fixture"]["rank_windows"]]
    negative_ranks = []
    for max_length in rank_windows:
        words = all_words(alphabet, max_length)
        rank = int(np.linalg.matrix_rank(hankel_matrix(_anbn_indicator, words, words), tol=tolerance))
        negative_ranks.append(
            {
                "max_length": max_length,
                "word_count": len(words),
                "hankel_rank": rank,
            }
        )
    strictly_increasing = all(
        later["hankel_rank"] > earlier["hankel_rank"]
        for earlier, later in pairwise(negative_ranks)
    )
    status = "complete" if all(item["passed"] for item in finite_results) and strictly_increasing else "failed"
    return {
        "experiment_id": config["experiment_id"],
        "status": status,
        "source_commit": _git_commit(),
        "command": " ".join(command),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "config": config,
        "finite_rank_results": finite_results,
        "negative_fixture": {
            "name": config["negative_fixture"]["name"],
            "ranks": negative_ranks,
            "strictly_increasing": strictly_increasing,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/das_v0.json")
    parser.add_argument("--output", default="results/das_v0.json")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    result = _run(config, sys.argv)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
