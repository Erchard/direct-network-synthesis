# DAS Theorem Note: What V0 Actually Establishes

Status: supporting mathematical note after DAS-V0. This is not a novelty claim.

## Classical Fact Used

For a real-valued function `f` on strings, define its Hankel matrix by
`H_f(u,v)=f(uv)`, where `u` ranges over prefixes and `v` ranges over suffixes.
Weighted-automata theory establishes that finite Hankel rank is the exact state
dimension needed by a minimal weighted automaton computing `f`. Given a complete
finite prefix/suffix basis whose Hankel block has that rank, one can recover a
weighted automaton directly from a matrix factorization of the block and the
symbol-shifted blocks.

This is established related work, not a DNS theorem. Current source anchors:

- Borja Balle and Mehryar Mohri, "Learning Weighted Automata", CAI 2015:
  https://research.google/pubs/learning-weighted-automata/
- Borja Balle and Mehryar Mohri, "Spectral Learning of General Weighted
  Automata via Constrained Matrix Completion", NeurIPS 2012:
  https://papers.nips.cc/paper/2012/hash/700fdb2ba62d4554dc268c65add4b16e-Abstract.html
- Daniel Hsu, Sham Kakade and Tong Zhang, "A Spectral Algorithm for Learning
  Hidden Markov Models", JCSS 2012:
  https://doi.org/10.1016/j.jcss.2011.12.025

## Reconstruction Implemented in This Repository

DAS-V0 implements the exact finite-block reconstruction case:

1. enumerate all words over the fixed alphabet up to a locked basis length;
2. form the Hankel block `H` and shifted blocks `H_a` from exact function values;
3. greedily select prefix and suffix rows/columns that preserve the observed
   block rank while keeping the empty word available;
4. factor `H` with SVD;
5. compute each transition matrix from the shifted block with pseudoinverses;
6. evaluate the recovered automaton on longer held-out words.

The implementation is in `src/dns/synthesis/weighted_automata.py` and the locked
runner is `experiments/run_das_v0.py`.

## What This Proves and Does Not Prove

What follows from the classical theorem, assuming exact arithmetic and a complete
basis: a finite-rank series can be represented by a weighted automaton whose
state count equals the Hankel rank, and the spectral extraction formulas recover
an equivalent realization.

What DAS-V0 verifies: for three fixed synthetic finite-rank teachers, the current
implementation reconstructs the expected state count and matches exact teacher
values on all locked held-out words to numerical precision.

What DAS-V0 does not show:

- that arbitrary sequence functions have finite rank;
- that sparse samples are enough to identify the correct automaton;
- that noisy observations remain stable;
- that the method trains a neural network;
- that the result scales to language models or lowers large-model training cost.

The negative `a^n b^n` control is included to make the main assumption visible:
some simple-looking behaviors do not have a bounded finite-state weighted
representation, and finite-window fits must not be mistaken for general recovery.

## Next Mathematical Question

DAS-L1 should replace exact complete Hankel access with sampled or incomplete
observations. That is where train/validation/test separation becomes essential:
train strings estimate blocks, validation selects rank/basis policy, and sealed
test strings evaluate generalization once. The success claim must then include
accuracy/error, rank, condition number, data retained, synthesis time and
inference time against matched baselines.
