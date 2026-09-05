# Related Work: Kernel Approximation and Direct Readouts

Status: working note, started 2026-09-05. This is not a novelty claim.

The current DNS 0.5 evidence sits near well-established kernel approximation and
fixed-feature literature. The project should treat these methods as references or
baselines unless a later source review identifies a narrower difference.

## Checked Sources

| Area | Source | Relevance to DNS |
|---|---|---|
| Kernel PCA / spectral features | Schoelkopf, Smola and Mueller, "Nonlinear Component Analysis as a Kernel Eigenvalue Problem", 1998, DOI: https://doi.org/10.1162/089976698300017467 | The rank-limited spectral oracle used here is a kernel eigenproblem reference, not a new DNS idea. |
| Nystrom kernel machines | Williams and Seeger, "Using the Nystrom Method to Speed Up Kernel Machines", NIPS 2000/2001, https://papers.nips.cc/paper/1866-using-the-nystrom-method-to-speed-up-kernel-machines | Directly covers low-rank kernel approximation through a smaller landmark/eigendecomposition system. |
| Random Fourier features | Rahimi and Recht, "Random Features for Large-Scale Kernel Machines", NIPS 2007, https://papers.nips.cc/paper/3182-random-features-for-large-scale-kernel-machines | Covers randomized explicit features whose inner products approximate shift-invariant kernels such as RBF. |
| Extreme learning machines | Huang, Zhu and Siew, "Extreme Learning Machine: Theory and Applications", Neurocomputing 2006, DOI: https://doi.org/10.1016/j.neucom.2005.12.126 | Random hidden nodes plus analytically solved output weights are established prior art for non-gradient readouts. |
| Landmark selection | Oglic and Gaertner, "Nystrom Method with Kernel K-means++ Samples as Landmarks", ICML 2017, https://proceedings.mlr.press/v70/oglic17a.html | Data-dependent landmark selection for Nystrom approximation is established; class-balanced or farthest-first variants here are controls, not novelty claims. |
| Implementation reference | scikit-learn `Nystroem` documentation, https://scikit-learn.org/stable/modules/generated/sklearn.kernel_approximation.Nystroem.html | Confirms the standard feature-map form: kernels to basis points multiplied by a normalization from the basis kernel matrix. |

## Implication for the Next Experiment

The matched-readout result showed that rank-192 spectral RBF features nearly
preserve the full RBF oracle on reused digits development splits, while the
current DNS05 compiler remains far behind that spectral reference. A professional
next test is therefore not another residual-depth variant. It is a landmark
diagnostic:

1. Can simple Nystrom-style landmark features explain most of the gap between
   the compiler and the spectral oracle?
2. Does deterministic farthest-first landmark selection outperform uniform
   sampling under the same readout grid?
3. Does train-label-balanced landmark selection help classification enough to be
   worth separating as a supervised synthesis procedure?

Any success in this diagnostic belongs first to the established Nystrom/kernel
approximation family. DNS can only claim a later contribution if it defines a
specific reproducible synthesis change beyond those methods and compares against
them directly.
