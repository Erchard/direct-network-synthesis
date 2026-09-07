"""Weighted-automaton synthesis from Hankel blocks."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

import numpy as np

Word = tuple[str, ...]
SeriesFunction = Callable[[Word], float]


@dataclass(frozen=True)
class WeightedAutomaton:
    """Finite weighted automaton over a fixed alphabet."""

    alphabet: tuple[str, ...]
    initial: np.ndarray
    transitions: dict[str, np.ndarray]
    final: np.ndarray

    def __post_init__(self) -> None:
        alphabet = tuple(self.alphabet)
        if not alphabet:
            raise ValueError("alphabet must be non-empty.")
        object.__setattr__(self, "alphabet", alphabet)
        initial = np.asarray(self.initial, dtype=float)
        final = np.asarray(self.final, dtype=float)
        if initial.ndim != 1 or final.ndim != 1:
            raise ValueError("initial and final must be 1D vectors.")
        if initial.shape != final.shape:
            raise ValueError("initial and final must have the same width.")
        rank = initial.shape[0]
        checked: dict[str, np.ndarray] = {}
        for symbol in alphabet:
            if symbol not in self.transitions:
                raise ValueError(f"missing transition for symbol {symbol!r}.")
            matrix = np.asarray(self.transitions[symbol], dtype=float)
            if matrix.shape != (rank, rank):
                raise ValueError("transition matrices must be square with state width.")
            checked[symbol] = matrix
        object.__setattr__(self, "initial", initial)
        object.__setattr__(self, "final", final)
        object.__setattr__(self, "transitions", checked)

    @property
    def state_count(self) -> int:
        return int(self.initial.shape[0])

    def evaluate(self, word: Sequence[str]) -> float:
        state = self.initial.copy()
        for symbol in word:
            state = state @ self.transitions[symbol]
        return float(state @ self.final)

    def evaluate_many(self, words: Iterable[Word]) -> np.ndarray:
        return np.asarray([self.evaluate(word) for word in words], dtype=float)


@dataclass(frozen=True)
class HankelBasis:
    """Prefix/suffix basis used by the finite spectral reconstruction."""

    prefixes: tuple[Word, ...]
    suffixes: tuple[Word, ...]
    rank: int
    candidate_count: int


@dataclass(frozen=True)
class HankelReconstruction:
    """Result of extracting a weighted automaton from finite Hankel blocks."""

    automaton: WeightedAutomaton
    basis: HankelBasis
    singular_values: tuple[float, ...]
    hankel_condition: float


def all_words(alphabet: Sequence[str], max_length: int) -> tuple[Word, ...]:
    """Enumerate all words up to max_length in deterministic length-lexicographic order."""

    if max_length < 0:
        raise ValueError("max_length must be non-negative.")
    checked_alphabet = tuple(alphabet)
    words: list[Word] = [()]
    frontier: list[Word] = [()]
    for _ in range(max_length):
        frontier = [word + (symbol,) for word in frontier for symbol in checked_alphabet]
        words.extend(frontier)
    return tuple(words)


def hankel_matrix(
    series: SeriesFunction,
    prefixes: Sequence[Word],
    suffixes: Sequence[Word],
) -> np.ndarray:
    matrix = np.empty((len(prefixes), len(suffixes)), dtype=float)
    for row_index, prefix in enumerate(prefixes):
        for column_index, suffix in enumerate(suffixes):
            matrix[row_index, column_index] = series(prefix + suffix)
    return matrix


def select_hankel_basis(
    series: SeriesFunction,
    alphabet: Sequence[str],
    *,
    max_length: int,
    tolerance: float = 1e-9,
) -> HankelBasis:
    """Choose a deterministic finite basis from complete short-word behavior."""

    candidates = all_words(alphabet, max_length)
    full = hankel_matrix(series, candidates, candidates)
    rank = int(np.linalg.matrix_rank(full, tol=tolerance))
    if rank == 0:
        raise ValueError("zero-rank series is not supported by this V0 extractor.")

    prefixes: list[Word] = [()]
    prefix_rows = [0]
    current_rank = int(np.linalg.matrix_rank(full[prefix_rows, :], tol=tolerance))
    for row_index, word in enumerate(candidates[1:], start=1):
        if current_rank >= rank:
            break
        trial_rows = [*prefix_rows, row_index]
        trial_rank = int(np.linalg.matrix_rank(full[trial_rows, :], tol=tolerance))
        if trial_rank > current_rank:
            prefixes.append(word)
            prefix_rows.append(row_index)
            current_rank = trial_rank

    suffixes: list[Word] = [()]
    suffix_columns = [0]
    current_rank = int(np.linalg.matrix_rank(full[np.ix_(prefix_rows, suffix_columns)], tol=tolerance))
    for column_index, word in enumerate(candidates[1:], start=1):
        if current_rank >= rank:
            break
        trial_columns = [*suffix_columns, column_index]
        trial_rank = int(
            np.linalg.matrix_rank(full[np.ix_(prefix_rows, trial_columns)], tol=tolerance)
        )
        if trial_rank > current_rank:
            suffixes.append(word)
            suffix_columns.append(column_index)
            current_rank = trial_rank

    basis_block = hankel_matrix(series, prefixes, suffixes)
    basis_rank = int(np.linalg.matrix_rank(basis_block, tol=tolerance))
    if basis_rank != rank:
        raise ValueError("candidate words did not yield a complete Hankel basis.")
    return HankelBasis(
        prefixes=tuple(prefixes),
        suffixes=tuple(suffixes),
        rank=rank,
        candidate_count=len(candidates),
    )


def reconstruct_weighted_automaton(
    series: SeriesFunction,
    alphabet: Sequence[str],
    *,
    max_basis_length: int,
    tolerance: float = 1e-9,
) -> HankelReconstruction:
    """Extract a finite weighted automaton from complete Hankel subblocks."""

    basis = select_hankel_basis(
        series,
        alphabet,
        max_length=max_basis_length,
        tolerance=tolerance,
    )
    h_lambda = hankel_matrix(series, basis.prefixes, basis.suffixes)
    u, singular_values, vt = np.linalg.svd(h_lambda, full_matrices=False)
    rank = basis.rank
    kept = singular_values[:rank]
    sqrt_s = np.sqrt(kept)
    prefix_factor = u[:, :rank] * sqrt_s[None, :]
    suffix_factor = sqrt_s[:, None] * vt[:rank, :]
    prefix_pinv = np.linalg.pinv(prefix_factor, rcond=tolerance)
    suffix_pinv = np.linalg.pinv(suffix_factor, rcond=tolerance)

    empty_prefix_index = basis.prefixes.index(())
    empty_suffix_index = basis.suffixes.index(())
    transitions: dict[str, np.ndarray] = {}
    for symbol in alphabet:
        shifted = hankel_matrix(
            series,
            tuple(prefix + (symbol,) for prefix in basis.prefixes),
            basis.suffixes,
        )
        transitions[symbol] = prefix_pinv @ shifted @ suffix_pinv

    condition = float(kept[0] / kept[-1]) if kept[-1] > 0.0 else float("inf")
    automaton = WeightedAutomaton(
        alphabet=tuple(alphabet),
        initial=prefix_factor[empty_prefix_index, :],
        transitions=transitions,
        final=suffix_factor[:, empty_suffix_index],
    )
    return HankelReconstruction(
        automaton=automaton,
        basis=basis,
        singular_values=tuple(float(value) for value in kept),
        hankel_condition=condition,
    )


def random_stable_automaton(
    alphabet: Sequence[str],
    *,
    state_count: int,
    seed: int,
    transition_scale: float = 0.35,
) -> WeightedAutomaton:
    """Generate a deterministic full-rank-ish test automaton with bounded outputs."""

    if state_count <= 0:
        raise ValueError("state_count must be positive.")
    rng = np.random.default_rng(seed)
    initial = rng.normal(size=state_count)
    final = rng.normal(size=state_count)
    transitions = {
        symbol: transition_scale * rng.normal(size=(state_count, state_count))
        for symbol in alphabet
    }
    return WeightedAutomaton(tuple(alphabet), initial, transitions, final)


def max_absolute_error(
    left: SeriesFunction,
    right: SeriesFunction,
    words: Sequence[Word],
) -> float:
    return float(max(abs(left(word) - right(word)) for word in words))
