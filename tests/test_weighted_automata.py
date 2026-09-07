import numpy as np

from dns.synthesis.weighted_automata import (
    all_words,
    hankel_matrix,
    max_absolute_error,
    random_stable_automaton,
    reconstruct_weighted_automaton,
    select_hankel_basis,
)


def test_all_words_is_length_lexicographic():
    assert all_words(("a", "b"), 2) == (
        (),
        ("a",),
        ("b",),
        ("a", "a"),
        ("a", "b"),
        ("b", "a"),
        ("b", "b"),
    )


def test_spectral_reconstruction_matches_unseen_longer_words():
    teacher = random_stable_automaton(("a", "b"), state_count=3, seed=97001)
    reconstruction = reconstruct_weighted_automaton(
        teacher.evaluate,
        ("a", "b"),
        max_basis_length=4,
    )
    check_words = all_words(("a", "b"), 8)
    assert reconstruction.basis.rank == 3
    assert reconstruction.automaton.state_count == 3
    assert max_absolute_error(
        teacher.evaluate,
        reconstruction.automaton.evaluate,
        check_words,
    ) < 1e-8


def test_hankel_rank_exposes_non_finite_rank_growth_on_anbn_indicator():
    def anbn_indicator(word):
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

    ranks = []
    for max_length in (2, 3, 4):
        words = all_words(("a", "b"), max_length)
        ranks.append(int(np.linalg.matrix_rank(hankel_matrix(anbn_indicator, words, words))))
    assert ranks == [4, 6, 8]


def test_short_candidate_window_produces_incomplete_reconstruction():
    teacher = random_stable_automaton(("a", "b"), state_count=3, seed=97002)
    basis = select_hankel_basis(teacher.evaluate, ("a", "b"), max_length=0)
    assert basis.rank == 1
    reconstruction = reconstruct_weighted_automaton(
        teacher.evaluate,
        ("a", "b"),
        max_basis_length=0,
    )
    assert max_absolute_error(
        teacher.evaluate,
        reconstruction.automaton.evaluate,
        all_words(("a", "b"), 3),
    ) > 1e-3
