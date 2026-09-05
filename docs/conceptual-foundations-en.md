# Conceptual Foundations of Direct Network Synthesis

> **Status:** long-form conceptual foundation of the research project  
> **Date captured:** 2026-09-05  
> **Language:** English  
> **Repository:** `Erchard/direct-network-synthesis`

This document explains the full line of reasoning that led to the **Direct Network Synthesis (DNS)** research program. It is written for a broad technical audience: machine-learning researchers, engineers, mathematicians, software developers, and technically curious readers who may not have followed the original discussion.

The goal is not to present a finished theory. The goal is to preserve the evolution of the idea honestly: where it came from, which analogies were useful, which assumptions failed, which experimental observations changed the direction, and what the next falsifiable research step is.

This document does **not** claim novelty. It is not a paper and it does not replace the experimental rules in `docs/methodology.md`. Its purpose is to provide the project with a durable conceptual memory.

---

## 0. Epistemic labels used throughout this document

To avoid mixing speculation, mathematics, literature, and preliminary experiments, statements should be read under one of five labels:

- **[A] Reasoning / analogy.** A conceptual argument used to formulate the problem. Useful, but not evidence by itself.
- **[B] Mathematically established fact.** For example, a closed-form ridge-regression solution or a spectral decomposition identity.
- **[C] Related-work context discussed during research.** Existing ideas such as Extreme Learning Machines, random features, kernel methods, Neural Tangent Kernels, convex reformulations, Forward Projection, or hypernetworks. Exact bibliography is still to be formalized.
- **[D] Exploratory chat experiment.** A preliminary number or observation reported while developing the idea. These are **not canonical repository results** until reproduced with committed code, fixed configurations, split seeds, and the protocol in `docs/methodology.md`.
- **[E] Research hypothesis / future direction.** Something we intend to test.

This distinction is central to the project. Exploratory numbers must never silently become “results” merely because they are convenient.

---

# Part I — Why ask whether learning must be iterative?

## 1. Market price discovery as iterative measurement

### 1.1 Entrepreneurs operate under uncertainty

[A] The initial intuition came from economics.

An entrepreneur commits money, labor, and time before knowing whether a business will succeed. Profit can therefore be viewed, in part, as compensation for accepting uncertainty and risk.

This is not a moral claim that every large profit is justified by risk. Excess profit can arise from monopoly power, legal privilege, scarcity, information asymmetry, network effects, patents, or many other causes. The only point relevant here is that entrepreneurship often involves **betting on a hypothesis about an environment that is not fully known in advance**.

### 1.2 A business tests hypotheses about human needs

[A] A seller effectively proposes something like:

> People want this product, in this form, at this place, at approximately this price.

The market answers not with a theorem but with behavior: people buy or refuse to buy.

Let price be `p`, unit cost be `C`, and the number of units sold at that price be `Q(p)`. Profit is

\[
\Pi(p) = (p-C)Q(p).
\]

The seller wants a profitable point on this unknown curve. The difficulty is that `Q(p)` is not known beforehand.

### 1.3 A newly opened store cannot know the optimal price immediately

[A] A new store may begin with an approximate price and then observe:

\[
p_1 \rightarrow Q_1,
\]

\[
p_2 \rightarrow Q_2,
\]

\[
p_3 \rightarrow Q_3.
\]

The seller is not simply maximizing price and not simply maximizing units sold. The objective is some function of margin, volume, costs, inventory, and other constraints.

The important point is that **the interaction itself reveals information**.

### 1.4 Why not calculate the price before any sales occur?

[A] Human preference is not directly observable like temperature or pressure. A person may say that they would pay a certain amount and then behave differently when actual payment is required.

Therefore, a real purchase is not only a transaction. It is also a **measurement event**.

This yields our first general principle:

> **When relevant properties of the environment cannot be known in advance, real-world trials may be necessary because the trials themselves create new information.**

This is why iterative search can be structurally necessary in some problems.

---

## 2. Evolution as another iterative adaptation process

### 2.1 Species do not intentionally “try” to adapt

[A] Evolution should not be anthropomorphized. A species does not choose a target and optimize toward it.

A simplified structure is:

\[
\text{variation}
\rightarrow
\text{interaction with environment}
\rightarrow
\text{different reproductive success}
\rightarrow
\text{selection}
\rightarrow
\text{new variation}.
\]

The environment acts as a filter on variants.

### 2.2 The structural similarity to markets

[A] The abstract pattern resembles market adaptation:

**Market:**

\[
\text{price/product variant}
\rightarrow
\text{customer response}
\rightarrow
\text{profit/loss}
\rightarrow
\text{adjustment}.
\]

**Evolution:**

\[
\text{organism variant}
\rightarrow
\text{environment}
\rightarrow
\text{reproductive success}
\rightarrow
\text{selection}.
\]

In both cases, the system lacks a complete internal model that directly predicts the globally appropriate answer. The environment is used as an oracle.

---

## 3. Engineering design is different

### 3.1 Designing a machine for known conditions

[A] Now consider an engineer designing a vehicle for a desert, a bridge for a known load, or a cooling system for a known heat profile.

We do not normally build billions of random machines, destroy nearly all of them, and keep the survivors.

Instead we use models:

- mechanics;
- material properties;
- thermodynamics;
- fluid dynamics;
- geometry;
- stress analysis;
- simulation;
- empirical coefficients.

Huge numbers of bad physical designs can be rejected **before they are manufactured**.

### 3.2 Iteration does not disappear; it becomes cheaper

[A] Engineering still uses iterative refinement: CAD simulations, prototypes, test rigs, crash tests, redesigns.

The key difference is not “iteration versus no iteration” in an absolute sense. The key difference is **where the expensive trial happens** and how much can be replaced by calculation.

A million physical failures can sometimes be replaced by a million cheap simulated counterfactuals.

### 3.3 The idealized limit

[A] In the limiting thought experiment, suppose we have:

1. perfect knowledge of the environment;
2. perfect knowledge of interaction laws;
3. a precisely defined objective;
4. sufficient computational capacity.

Then search iterations may, in principle, be replaced by direct synthesis:

\[
\text{environment}
+
\text{laws}
+
\text{objective}
\rightarrow
\text{computed design}.
\]

A final verification may still be required. But **verification of a computed answer is conceptually different from discovering the answer through repeated failed attempts**.

This distinction is the bridge to neural networks.

---

# Part II — The neural-network question

## 4. Standard neural-network training is parameter adaptation

[B] A neural network has parameters `\theta` and a loss `L(\theta)`. A simplified gradient-descent update is

\[
\theta_{t+1}
=
\theta_t - \eta \nabla L(\theta_t).
\]

The process is:

\[
\text{prediction}
\rightarrow
\text{error}
\rightarrow
\text{gradient}
\rightarrow
\text{parameter update}
\rightarrow
\text{new prediction}.
\]

[A] This is an adaptive feedback loop.

It is not literally Darwinian evolution. Gradient information is much richer than evolutionary fitness. A gradient provides a local direction for changing a very large parameter vector. Evolutionary selection provides a much weaker aggregate signal.

Still, both involve a trajectory through candidate states rather than direct construction of the final state.

---

## 5. The central question

[A/E] If the entire training dataset is already available, why must a model traverse millions or billions of intermediate parameter states?

The conventional picture is

\[
\theta_0
\xrightarrow{D}
\theta_1
\xrightarrow{D}
\theta_2
\xrightarrow{D}
\dots
\xrightarrow{D}
\theta_n.
\]

The direct-synthesis question is whether some useful class of models can instead support

\[
D \xrightarrow{F} \theta^*.
\]

Here `D` is the dataset and `F` is a deterministic synthesis procedure.

The goal is **not** to prove that every arbitrary modern neural network has a magical one-line closed-form optimum. That is almost certainly the wrong target.

The more realistic question is:

> Can we design classes of neural systems specifically so that useful representations and parameters are directly computable from the available data?

---

## 6. Important correction: “the dataset is not the environment” does not justify iterative training

[A] An early objection was that the dataset is only a sample of the real world, not the environment itself.

That is correct, but it does not explain why training must be iterative, because conventional SGD sees the **same dataset**.

This distinction matters:

- dataset incompleteness explains the generalization problem;
- dataset incompleteness does **not by itself** explain why weights must be updated through a long trajectory.

So the question remains valid.

---

# Part III — What “non-iterative” means in DNS

## 7. The process we want to avoid

[E] We want to avoid iterative parameter search of the form

\[
W_{t+1} = W_t + \Delta W_t,
\]

where parameter state `t+1` is chosen by evaluating the quality of parameter state `t`.

Under a strict DNS experiment, this includes:

- SGD;
- Adam;
- backpropagation used for repeated weight updates;
- coordinate descent over trainable parameters;
- evolutionary weight search;
- random search guided by validation or training loss;
- iterative learned optimization of the specific model parameters;
- any outer loop of “change parameters -> measure loss -> change again.”

### 7.1 Direct computation is allowed

[B] DNS permits finite deterministic operations such as:

- matrix multiplication;
- solving linear systems;
- pseudoinverse;
- ridge regression;
- SVD;
- eigendecomposition;
- QR decomposition;
- Cholesky decomposition;
- kernel construction;
- deterministic feature construction;
- one or a small number of passes through data to accumulate sufficient statistics.

A numerical library may internally use iterative algorithms to solve an eigensystem or linear system. That does not violate the conceptual definition as long as there is **no outer optimization loop over trainable model parameters using feedback from the task loss**.

This distinction is important. DNS is not a fetish for “literally one CPU pass.” It is a research program about replacing **adaptive parameter search** with **direct mathematical synthesis**.

---

# Part IV — The simplest evidence that direct training is possible

## 8. Closed-form linear regression already does this

[B] For ridge regression,

\[
W^* = (X^TX + \lambda I)^{-1}X^TY.
\]

There is no gradient trajectory in parameter space.

So the claim “learning fundamentally requires iterative updates” is already false for an important class of models.

The real difficulty is nonlinear representation.

---

# Part V — Existing ideas near DNS

## 9. Extreme Learning Machines

[C] Extreme Learning Machines (ELM) show that one can fix or randomly generate a hidden representation and solve only the output layer analytically.

If

\[
H = \phi(XW_{fixed}+b),
\]

then

\[
\beta = H^+Y
\]

or a regularized equivalent provides the output weights.

This is highly relevant to DNS: a nonlinear neural model can have an analytical readout.

But random hidden features do not solve our deeper problem of **engineering the representation itself**.

---

## 10. Random features

[C] Random-feature methods follow a similar structure: construct a nonlinear feature map, then solve a linear problem over those features.

They demonstrate that nonlinear learning can often be decomposed into:

\[
\text{representation}
\rightarrow
\text{linear solve}.
\]

Again, DNS asks whether the representation can be **designed rather than randomly sampled or gradually trained**.

---

## 11. Kernel ridge regression

[C/B] Kernel ridge gives a stronger non-iterative nonlinear baseline.

For kernel matrix `K`,

\[
\alpha = (K+\lambda I)^{-1}Y.
\]

The challenge is scaling because

\[
K\in\mathbb{R}^{N\times N}.
\]

This observation eventually changed the DNS project significantly: instead of viewing a strong kernel only as a competitor, we began to view it as a **behavioral specification** that could potentially be compiled into a compact network.

---

## 12. Neural Tangent Kernel viewpoint

[C] Neural Tangent Kernel theory shows that, in certain infinite-width regimes, network training can be described through kernel dynamics in function space.

For DNS, the conceptual lesson is that the boundary between “neural network” and “kernel method” is not absolute.

---

## 13. Convex reformulations of some ReLU training problems

[C] Existing work shows that some restricted ReLU training problems can be reformulated as convex optimization problems with global guarantees.

The lesson is important:

> The architecture can be chosen so that the learning problem itself becomes mathematically tractable.

This supports the DNS philosophy of **synthesis-friendly architectures** rather than arbitrary architectures.

---

## 14. Closed-form and layer-wise learning

[C] There is a broad family of methods where individual layers, blocks, or readouts are fitted without end-to-end backpropagation.

This prevents us from making naive novelty claims. “No backprop” by itself is not a new research contribution.

---

## 15. Forward Projection (2026, discussed in research chat)

[C] A particularly relevant work discussed during research is **Forward Projection**, where local hidden targets are constructed and each layer is obtained through a closed-form regression step rather than standard backpropagation.

A generic layer solve has the form

\[
W_l =
(A_{l-1}^TA_{l-1}+\lambda I)^{-1}
A_{l-1}^T\tilde Z_l.
\]

The important lesson for DNS is not a claim of novelty over this method. It is that **deep, multilayer systems do not logically require backpropagation merely because they are deep**.

Our stronger ambition is to replace random or heuristic hidden targets with **deterministically designed task geometry**.

---

## 16. Hypernetworks and meta-learning

[C] Another route is

\[
G_\phi(D) = \theta,
\]

where one learned system consumes a task or dataset and emits parameters for another model.

This is close to `Dataset -> Weights`, but the optimization burden is moved into the hypernetwork training process.

We therefore view hypernetworks as **amortized synthesis**, not necessarily as the cleanest answer to the original engineering question.

---

# Part VI — The key reframing: weights may not be the hard part

## 17. If good hidden representations were known, inter-layer weights could be simple

[A/B] Consider

\[
X
\rightarrow H_1
\rightarrow H_2
\rightarrow \dots
\rightarrow H_L
\rightarrow Y.
\]

Suppose useful target representations

\[
H_1^*, H_2^*, \ldots, H_L^*
\]

were already known.

Then many inter-layer mappings could be posed as regression problems:

\[
W_1 \approx X^+H_1^*,
\]

\[
W_2 \approx (H_1^*)^+H_2^*,
\]

and, with ridge regularization,

\[
W_l =
(H_{l-1}^TH_{l-1}+\lambda I)^{-1}
H_{l-1}^TH_l^*.
\]

This led to the central reframing:

> **The hardest part of deep learning may be discovering useful internal representations, not computing the final numerical weights once those representations are specified.**

So the DNS problem becomes

\[
D
\rightarrow
(H_1^*,H_2^*,\ldots,H_L^*)
\rightarrow
(W_1,W_2,\ldots,W_L).
\]

---

# Part VII — Evolution of our own DNS hypotheses

## 18. DNS 0.1 — direct spectral/supervised hidden representation

[E] The first prototype idea was:

1. use `X` and `Y`;
2. build a deterministic hidden representation using SVD/PCA plus supervised geometry;
3. solve mappings to that representation directly;
4. solve the final output layer by ridge regression.

### 18.1 Exploratory result

[D] An early `sklearn digits` experiment reported approximately **93.7% accuracy** from a deterministic spectral mixture of input geometry and label geometry.

This was useful as a proof of life but not competitive enough.

**Do not treat this number as canonical until reproduced in the repository.**

---

## 19. RBF kernel ridge became our non-iterative oracle

[D] An early experiment on `digits` reported roughly **97.96%** for RBF kernel ridge, compared with roughly **97.78%** for a small gradient-trained MLP in that particular run.

This changed the project direction.

The question was no longer:

> Can a nonlinear model be fitted without gradient updates at all?

For small problems, the answer was already clearly yes.

The harder problem became:

> Can the behavior of a strong kernel system be represented by a compact feed-forward mechanism without storing the whole training set?

### 19.1 Why multiple RBF numbers appear in the research history

[D] As the experimental protocol became stricter, several different RBF figures were reported in different rounds:

- approximately **98.06%** in one cleaner train/validation/test experiment;
- approximately **98.61% ± 0.59** across one set of ten splits;
- approximately **98.13%** in another new-split validation round;
- approximately **98.19% ± 0.59** in a later 20-split analysis.

These should **not** be merged into one benchmark claim or cherry-picked.

They represent different experimental stages.

The project rule is:

> A canonical result exists only when code, configuration, split seeds, command, commit SHA, and result artifact are committed under the formal methodology.

### 19.2 Spectral compression observation

[D] Exploratory analysis suggested that the useful geometry of the RBF kernel on `digits` can be approximated at much lower rank than `N`.

One early table reported approximately:

| Rank | Exploratory accuracy |
|---:|---:|
| 10 | ~80.9% |
| 20 | ~89.8% |
| 50 | ~93.9% |
| 75 | ~96.1% |
| 150 | ~97.0% |
| 200 | ~97.96% |
| Full | ~97.96% |

Later discussion generalized the observation to roughly **150–300 useful spectral directions** retaining most or all performance in this small task.

This suggested

\[
K \approx HH^T
\]

with `H` much narrower than `N`.

The network could then be interpreted as a compact mechanism for computing `H(x)`.

---

## 20. DNS-ReLU 0.2 — deterministic ReLU feature construction

[E/D] The next prototype moved closer to an ordinary neural layer.

Hidden directions were constructed deterministically from combinations of:

- PCA/SVD directions;
- class-centroid directions;
- Fisher-like supervised directions;
- train-derived quantile thresholds for ReLU units.

For direction `d_j` and threshold `t_jk`,

\[
h_{jk}(x)=\max(0,d_j^Tx-t_{jk}).
\]

The output layer was solved once:

\[
W=(H^TH+\lambda I)^{-1}H^TY.
\]

### 20.1 Exploratory performance

[D] Chat experiments reported roughly **97.5–98%** on `digits` without gradient updates.

### 20.2 Novelty check

[C] Literature inspection showed that the basic idea overlaps strongly with known deterministic ELM variants, including PCA-informed and LDA/Fisher-informed constructions.

Therefore DNS-ReLU 0.2 should be treated as a **baseline/building block**, not a novelty claim.

This was an important research-discipline lesson: good performance is not sufficient evidence of a new idea.

---

## 21. DNS 0.3 — naive chaining of spectral targets

[E] We then attempted to implement the representation-first hypothesis literally:

\[
X
\xrightarrow{closed\ form}
H_1^*
\xrightarrow{closed\ form}
H_2^*
\xrightarrow{closed\ form}
H_3^*.
\]

A spectral embedding of a good kernel geometry served as the target.

### 21.1 Negative result

[D] This did not improve sufficiently. A best validation figure around **96.4%** was discussed for one variant, and adding layers did not systematically help.

### 21.2 Diagnosis: useful does not imply realizable

The failure revealed a conceptual mistake:

> **A representation may be good for the task but difficult or impossible for the preceding layer to realize.**

We had asked, “What representation would be useful?” but not, “Can this particular block actually produce it?”

This introduced the concept of **realizability**.

---

## 22. Realizability becomes a second fundamental criterion

[E] A useful hidden target should satisfy both:

1. **Task usefulness** — it should encode geometry relevant to prediction and generalization.
2. **Layer realizability** — it should be reachable from the current representation through the available synthesized feature mechanism.

Conceptually,

\[
H_l^*
\in
\text{TaskUseful}
\cap
\text{RealizableByLayer}_l.
\]

This is one of the most important conceptual shifts in the project.

---

## 23. DNS 0.4 — project the target into the realizable feature space

[E] Given current activations `A_{l-1}`, build a deterministic candidate feature matrix

\[
\Phi_l = \Phi_l(A_{l-1}).
\]

Build a desired target representation `T_l` separately.

Instead of forcing the layer to reproduce `T_l` exactly, project the target into the span of the available features:

\[
B_l =
(\Phi_l^T\Phi_l+\lambda I)^{-1}\Phi_l^TT_l,
\]

\[
H_l = \Phi_lB_l.
\]

Now `H_l` is realizable by construction.

### 23.1 Realizability error

We introduced

\[
e_l =
\frac{\|T_l-H_l\|_F}{\|T_l\|_F}.
\]

This measures how much of the desired representation the current feature mechanism fails to express.

### 23.2 Kernel-target alignment

We also tracked a quantity of the form

\[
A(K_H,K_Y)=
\frac{\langle K_H,K_Y\rangle_F}
{\|K_H\|_F\|K_Y\|_F}.
\]

The purpose was to observe not only accuracy but the evolution of representation geometry across layers.

### 23.3 Early encouraging observation

[D] On one exploratory split, the reported accuracy progression was approximately

\[
96.94\% \rightarrow 97.22\% \rightarrow 97.50\%,
\]

while alignment increased roughly

\[
0.745 \rightarrow 0.930 \rightarrow 0.957.
\]

This was the first sign that **analytically synthesized depth might be useful**.

But a single split is debugging evidence, not research evidence.

### 23.4 Multi-split analysis

[D] In one 8-split round, approximate figures were:

- 1 layer: ~97.33%;
- 3 layers: ~97.57% ± 0.51;
- direct deterministic ReLU baseline: ~96.91%;
- RBF: ~98.13%.

A later 20-split analysis gave a more conservative picture:

| Model | Exploratory mean test accuracy |
|---|---:|
| Direct deterministic ReLU | ~96.75% ± 0.85 |
| DNS 0.4, 1 layer | ~96.99% ± 0.81 |
| DNS 0.4, 2 layers | ~97.10% ± 0.79 |
| DNS 0.4, 3 layers | ~97.17% ± 0.78 |
| RBF kernel ridge | ~98.19% ± 0.59 |

### 23.5 Statistical conclusion

[D] The 3-layer DNS 0.4 model exceeded the 1-layer variant by only about **0.18 percentage points**, with a reported `p≈0.16`. That is not strong evidence for useful depth.

However, DNS 0.4 3-layer exceeded the direct deterministic ReLU baseline by roughly **0.42 percentage points**, with a reported `p≈0.005`, which looked more robust.

We explicitly **did not accept** the claim that depth had already been proven useful.

That restraint is part of the project methodology.

### 23.6 Shuffled-label sanity test

[D] With shuffled training labels, exploratory accuracy dropped to roughly **11.7%** for a 10-class problem, close to chance level.

This helped rule out obvious forms of label leakage in that implementation round.

### 23.7 Critical negative result: label alignment is not generalization

[D] Hidden kernel-target alignment could keep rising strongly, for example approximately

\[
0.65 \rightarrow 0.84 \rightarrow 0.93,
\]

while test accuracy changed only slightly:

\[
96.99 \rightarrow 97.10 \rightarrow 97.17.
\]

This produced an important conclusion:

> **Maximizing similarity to label geometry is not the same as maximizing generalization.**

A representation can become increasingly organized around training labels without becoming substantially better on unseen examples.

### 23.8 Residual/skip variant did not solve the problem

[D] A residual/skip variant was tested to reduce information loss between layers.

Exploratory realizability error reportedly improved approximately

\[
0.19 \rightarrow 0.12 \rightarrow 0.09,
\]

but test accuracy did not improve and in some development runs degraded.

This gave another important lesson:

> Better realization of a bad target is still a bad design.

So neither task alignment alone nor realizability alone is enough.

---

# Part VIII — DNS 0.5: Kernel Compiler

## 24. The strongest reframing so far

After DNS 0.4, we asked a simpler question:

> Why invent an “ideal” geometry if a strong geometry is already known to work?

RBF kernel ridge had repeatedly served as a strong non-iterative reference in exploratory experiments.

So we changed the objective from

\[
X,Y \rightarrow \text{invented }K^*
\]

to

\[
K_{oracle}
\rightarrow
\text{compact executable representation}.
\]

This is the core idea of **DNS 0.5 Kernel Compiler**.

---

## 25. Kernel as specification, network as compiled mechanism

[A/E] The engineering analogy becomes sharper here:

- the oracle kernel `K*` is a known functional specification of similarity geometry;
- the neural mechanism is the compact executable representation we want to construct;
- we do not evolve its weights through a long loss trajectory;
- we attempt to **compile the known behavior into a compact parametric mechanism**.

This is much closer to engineering design than to evolutionary trial-and-error.

---

## 26. Basic mathematics of DNS 0.5

Let

\[
K^* = K_{RBF}.
\]

Compute the eigendecomposition

\[
K^*=U\Lambda U^T.
\]

Choose rank `r` and define

\[
T = U_r\Lambda_r^{1/2}.
\]

Then

\[
TT^T \approx K^*.
\]

### 26.1 First block

Construct deterministic features `\Phi_1(X)` and project the spectral target into that realizable feature space:

\[
B_1=(\Phi_1^T\Phi_1+\lambda I)^{-1}\Phi_1^TT,
\]

\[
H_1=\Phi_1B_1.
\]

The first block induces

\[
K^{(1)}=H_1H_1^T.
\]

### 26.2 Subsequent blocks should learn only residual geometry

Instead of making every block approximate the full target again, compute

\[
R_1 = K^* - K^{(1)}.
\]

Because approximation residuals may be indefinite, take the positive spectral component:

\[
R_1^+ = U_+\Lambda_+U_+^T.
\]

Then define the next target

\[
T_2 = U_{+,r_2}\Lambda_{+,r_2}^{1/2}.
\]

The next block should explain only what the previous block failed to explain.

After `L` blocks,

\[
K^{(L)} = \sum_{l=1}^{L}H_lH_l^T.
\]

Residual:

\[
R_L=K^*-K^{(L)}.
\]

Primary structural metric:

\[
E_L =
\frac{\|K^*-K^{(L)}\|_F}{\|K^*\|_F}.
\]

---

## 27. What would count as useful analytical depth?

[E] A deeper DNS model is not interesting merely because it contains more blocks.

We want to see

\[
E_1 > E_2 > E_3 > \dots
\]

and ideally

\[
Acc_1 \le Acc_2 \le Acc_3 \le \dots.
\]

Each new closed-form block should:

1. explain a new part of the oracle geometry;
2. preserve what previous blocks already explained;
3. preferably improve generalization.

If reconstruction error decreases while accuracy remains flat, that is still informative: perhaps the model is learning parts of the kernel that are irrelevant to the downstream classification boundary.

If accuracy improves without monotonic kernel reconstruction, then kernel reconstruction itself may be the wrong task-relevant objective.

Either outcome is scientifically useful.

---

# Part IX — Theoretical caution and the right level of ambition

## 28. Why a universal direct formula for arbitrary networks is probably the wrong target

[C] Complexity-theoretic results discussed during research suggest that globally optimizing even small ReLU networks can be computationally hard in general formulations.

For DNS, this is not a proof that direct synthesis is impossible.

It suggests a more realistic target:

Not

\[
F(\text{arbitrary architecture}, D)
=
\text{globally optimal arbitrary weights},
\]

but

> **Design a restricted class of synthesis-friendly architectures where direct construction is part of the architecture itself.**

Engineering systems are often designed to be analyzable, decomposable, controllable, and testable. Neural architectures can potentially be designed the same way.

---

## 29. Synthesis-friendly networks as a separate research object

[E] A future DNS architecture does not have to be a standard MLP or standard Transformer.

Potential design principles include:

- explicit feature bases per block;
- closed-form local projections;
- residual decomposition with measurable contributions;
- controlled rank;
- measurable geometry per layer;
- stable linear-algebraic inter-layer solves;
- modular compilation;
- architecture designed **for synthesis rather than for backpropagation**.

This may ultimately matter more than attempting to “train a normal architecture in an unusual way.”

---

# Part X — Experimental discipline

## 30. Why this project is easy to fool ourselves with

DNS research is especially vulnerable to subtle self-deception:

- selecting kernel hyperparameters after seeing test performance;
- choosing rank after seeing test accuracy;
- keeping only favorable random splits;
- comparing against an intentionally weak MLP baseline;
- rediscovering an old ELM variant and calling it new;
- hiding iterative optimization inside feature selection;
- showing only successful ablations;
- using label information from test data indirectly through preprocessing.

Therefore the protocol is not bureaucracy. It is part of the scientific content.

---

## 31. Mandatory experiment rules

These rules align with `docs/methodology.md`.

### 31.1 Train / validation / test separation

- Train data may fit preprocessing, kernel statistics, feature synthesis, and closed-form coefficients.
- Validation data may select hyperparameters and model families.
- Test data is reserved for locked comparisons.

Once test performance has influenced design, that test set is no longer genuinely unseen.

### 31.2 Seeds

Record:

- split seeds;
- sampling seeds;
- pseudo-random feature seeds, if any;
- synthetic-data seeds.

### 31.3 Multiple splits

Single-split runs are debugging only.

Research evidence should include:

- mean;
- standard deviation;
- paired differences where possible;
- effect sizes;
- confidence intervals or statistical tests for improvement claims.

### 31.4 Leakage tests

At minimum:

- shuffled-label sanity test;
- preprocessing fit only on training data;
- no test-derived thresholds;
- no kernel hyperparameters selected on test;
- no seed cherry-picking.

### 31.5 Ablations

For DNS 0.5, useful ablations include:

- no residual blocks;
- random spectral targets;
- PCA-only feature basis;
- Fisher-only feature basis;
- no positive-residual clipping;
- fixed rank versus adaptive residual rank;
- different oracle kernels;
- one wide block versus several residual blocks with the same total feature budget.

### 31.6 Negative results are first-class results

A failed DNS version must remain visible in `docs/research-log.md`.

The goal is not to “prove DNS.” The goal is to discover where direct synthesis succeeds and where it fails.

### 31.7 No novelty claims without literature comparison

Any candidate contribution must be compared against relevant known families such as:

- ELM;
- deterministic ELM;
- PCA/LDA/Fisher feature networks;
- random features;
- kernel approximation;
- Nyström methods;
- closed-form layer-wise networks;
- Forward Projection-like methods;
- kernel distillation and kernel-to-network compression.

---

# Part XI — Success criteria

## 32. Stage 1: nonlinear direct fitting

This is no longer the deepest unknown because kernels and fixed-feature models already demonstrate it.

Still, the repository needs clean reproducible baselines.

A Stage-1 success means:

- nonlinear model;
- no iterative parameter optimization;
- strict data separation;
- competitive performance against a simple gradient-trained baseline;
- no hidden test tuning.

---

## 33. Stage 2: compactness

Kernel methods are not the final goal because a full kernel machine often requires quadratic memory or dependence on all training examples.

We need

\[
K^* \approx HH^T
\]

with rank `r << N`, and inference on a new sample should not require comparison with the entire training set.

---

## 34. Stage 3: useful analytical depth

This is one of the most important milestones.

At equal total feature or parameter budget, compare:

- one-block compiled model;
- two-block residual compiled model;
- three-block residual compiled model.

Evidence for useful depth requires more than better reconstruction. Ideally:

1. each block has an independently measurable residual contribution;
2. reconstruction error decreases;
3. generalization does not degrade;
4. multi-block residual organization consistently outperforms a fair one-shot wide baseline.

If condition 4 fails, we may only have an additive feature expansion rather than meaningful depth.

---

## 35. Stage 4: scaling without materializing an `N x N` kernel

[E] A practical DNS paradigm needs a path beyond explicit quadratic kernel matrices.

Possible future directions include:

- blockwise Gram computation;
- low-rank train-only statistics;
- structured kernels;
- landmark methods;
- streaming covariance/kernel summaries;
- hierarchical spectral decomposition.

These remain future hypotheses.

---

# Part XII — Scaling roadmap

## 36. `sklearn digits`

Purpose: fast laboratory for mathematical ablations.

It is not evidence of large-scale viability.

## 37. MNIST / Fashion-MNIST

Move here only when:

- DNS 0.5 is reproducible;
- protocol is locked;
- residual-block ablations are implemented;
- memory and compute complexity are understood.

## 38. CIFAR-10 / CIFAR-100

This is the first serious test of whether direct representation synthesis survives more complex visual geometry.

Local or convolution-like structured feature bases may be necessary.

## 39. Larger vision tasks

Only after demonstrating that the method does not collapse with larger `N` and input dimensionality.

## 40. Small Transformer

A language experiment should begin with a small controlled model, not a large LLM.

## 41. Autoregressive language modeling

This stage is justified only after demonstrating that multi-layer direct synthesis creates useful hierarchical representations rather than merely a fixed-feature classifier.

---

# Part XIII — Speculative Transformer direction

## 42. Top-down design of hidden representations

[E] In next-token prediction, the dataset already defines pairs

\[
(x_1,\ldots,x_t) \rightarrow x_{t+1}.
\]

One speculative strategy is to design target representations **backward from the output task**.

For example:

1. construct a representation from which the next-token prediction is simple;
2. construct an earlier representation that preserves more context while mapping easily into the later one;
3. continue backward toward the input;
4. then synthesize the forward mappings analytically.

Target design:

\[
Y
\rightarrow T_L
\rightarrow T_{L-1}
\rightarrow \dots
\rightarrow T_1,
\]

implementation:

\[
X
\rightarrow T_1
\rightarrow T_2
\rightarrow \dots
\rightarrow T_L
\rightarrow Y.
\]

This is still speculative. DNS 0.5 provides a simpler environment for testing the general principle “representation first, weights second.”

---

# Part XIV — Why GitHub and Codex matter now

## 43. From conversation to research codebase

At the beginning, a chat was enough to explore the idea.

Once the project developed:

- multiple DNS versions;
- multi-split statistics;
- p-values;
- failed variants;
- configuration sensitivity;
- literature overlap;

chat alone became an unreliable research memory.

A versioned repository is required for:

- code history;
- fixed configs;
- exact experiment IDs;
- reproducible commands;
- result artifacts;
- negative-result logging;
- links between hypothesis changes and code changes.

The repository documentation has deliberately different roles:

- `docs/hypothesis.md` — concise formal statement of research intent;
- `docs/methodology.md` — binding experimental protocol;
- `docs/research-log.md` — chronological laboratory notebook;
- `docs/conceptual-foundations-uk.md` — original long-form Ukrainian conceptual memory;
- `docs/conceptual-foundations-en.md` — broad-audience English conceptual foundation.

---

# Part XV — Timeline of hypothesis evolution

## 44. How the project changed its mind

| Stage | Initial belief | What changed it | Updated conclusion |
|---|---|---|---|
| Market | A good price is found by trial | Preferences are not directly measurable before real purchase behavior | Iteration is needed when experiments create new information |
| Evolution | Adaptation requires variation and selection | No internal model predicts the correct organism | Selection is a search mechanism under incomplete modeling |
| Engineering | Trial-and-error can be reduced | Known conditions and laws allow calculation and simulation | Search can be replaced by synthesis when enough structure is known |
| Neural training | SGD is the natural training mechanism | Dataset is already available before the first update | Ask whether the weight trajectory is fundamental or merely one solver |
| Dataset objection | Dataset is not the real environment | SGD sees the same dataset | This explains generalization difficulty, not the necessity of parameter iteration |
| DNS 0.1 | Spectral hidden targets may be enough | ~93.7% exploratory result | Simple spectral mixtures are insufficient |
| Kernel baseline | Closed-form nonlinear models may be weak | RBF gave ~98% exploratory performance | Non-iterativity itself is not the primary barrier; compactness/scaling is |
| DNS-ReLU 0.2 | Deterministic ReLU directions may solve the task | ~97.5–98% exploratory performance plus literature overlap | Works as a baseline but overlaps known deterministic ELM ideas |
| DNS 0.3 | A good task target should be enough | Chained targets failed to produce consistent depth gains | Useful targets may be unrealizable |
| Realizability | Project targets into what the layer can express | DNS 0.4 became more stable | Need task usefulness × realizability |
| DNS 0.4 | Increasing label alignment should improve deeper layers | Alignment rose much faster than test accuracy; residual skip did not fix it | Label alignment is not a generalization objective |
| DNS 0.5 | Invent a better target geometry | Strong RBF geometry already exists | Compile a known good geometry instead of inventing one |
| Current stage | Residual kernel compilation may create useful analytical depth | Not yet proven | Next experiment must test depth versus width fairly |

---

# Part XVI — What we currently believe

## 45. Working beliefs

These are not final truths. They are current beliefs informed by reasoning, known mathematics, literature, and exploratory evidence.

### 45.1 Iterative weight optimization is not universally necessary

[B/C/D] Linear closed-form models, kernel ridge, ELM-like systems, and layer-wise closed-form methods already demonstrate this in restricted settings.

### 45.2 Hidden representation is probably the central difficulty

[A/D] Output ridge solves are easy. The difficult object is a compact internal representation that is simultaneously:

- task relevant;
- generalizable;
- realizable by the architecture;
- scalable.

### 45.3 Label alignment alone is insufficient

[D] Increasing alignment to training labels can fail to improve unseen performance.

### 45.4 Realizability alone is insufficient

[D] Better target reconstruction can still reconstruct the wrong target.

### 45.5 A strong known kernel is a better first specification than an invented geometry

[A/D/E] If RBF consistently behaves well, compiling it is a cleaner engineering problem than inventing a new abstract target representation at every layer.

### 45.6 Architectures should be designed for synthesis

[C/E] Trying to derive a universal direct optimizer for arbitrary networks is probably less promising than building a new family of networks whose structure explicitly supports analytical synthesis.

---

# Part XVII — What remains unproven

## 46. Open claims

1. DNS 0.5 has **not** yet proven useful depth.
2. Kernel Compiler has **not** yet matched RBF oracle performance with a compact network.
3. Reconstructing `K*` has **not** been proven to be the right objective for generalization.
4. Multi-block residual compilation has **not** been proven better than one wide block with equal total budget.
5. Scalability beyond toy datasets is unproven.
6. High-dimensional raw-image performance is unproven.
7. Sequence-model transfer is unproven.
8. Computational advantage over SGD at equal quality is unproven.
9. No novelty claim has been established for current formulas.
10. It is not yet known whether “non-iterative” will become a practical advantage or merely a different compute/memory tradeoff.
11. It is not necessary to insist on literally one physical dataset pass; the core requirement is absence of adaptive parameter search.

---

# Part XVIII — Immediate next experiment: DNS 0.5 Kernel Compiler

## 47. Narrow experiment objective

Test the following falsifiable claim:

> **Can a sequence of deterministic closed-form blocks progressively approximate a strong RBF kernel geometry, and does residual multi-block compilation outperform a fair one-shot model at comparable total feature budget?**

Do not attempt to prove scalability, novelty, and superiority to deep learning all at once.

---

## 48. Dataset and protocol

First canonical experiment:

- `sklearn digits`;
- stratified train/validation/test splits;
- fixed split-seed list;
- no test tuning;
- hyperparameters locked before test evaluation;
- run ID + config + commit SHA saved.

Classification metrics:

- accuracy;
- optionally log-loss/calibration;
- mean ± standard deviation across splits;
- paired delta against baselines;
- confidence intervals or paired significance test for primary claims.

Structural metrics:

- kernel reconstruction error `E_L`;
- spectral energy captured;
- rank/width per block;
- total features;
- memory footprint;
- solve time;
- inference time;
- alignment metrics only as secondary diagnostics.

---

## 49. Oracle definition

Construct train-only RBF kernel

\[
K^*_{ij}=\exp(-\gamma\|x_i-x_j\|^2).
\]

Select `\gamma` only through train/validation rules.

Record locked RBF kernel-ridge performance as the oracle reference.

---

## 50. Spectral target

Compute

\[
K^*=U\Lambda U^T.
\]

Choose rank `r` using validation or a train-only spectral-energy rule fixed before test.

Define

\[
T_1=U_r\Lambda_r^{1/2}.
\]

---

## 51. Block-1 synthesis

Construct deterministic `\Phi_1(X)`.

Candidate families:

- PCA directions + quantile ReLU knots;
- PCA + class-centroid directions;
- PCA + Fisher directions;
- possibly structured polynomial or RBF-like deterministic features.

Projection:

\[
B_1=(\Phi_1^T\Phi_1+\lambda I)^{-1}\Phi_1^TT_1,
\]

\[
H_1=\Phi_1B_1.
\]

---

## 52. Residual kernel decomposition

Compute

\[
R_1=K^*-H_1H_1^T.
\]

Symmetrize numerically if required:

\[
R_1\leftarrow\frac{R_1+R_1^T}{2}.
\]

Take positive spectral component:

\[
R_1^+=U_+\Lambda_+U_+^T.
\]

Next target:

\[
T_2=U_{+,r_2}\Lambda_{+,r_2}^{1/2}.
\]

Repeat for blocks 2 and 3.

---

## 53. Critical ablation: depth versus width

This is mandatory.

Compare:

### A. One-shot wide model

One feature matrix `\Phi` with total width `M`.

### B. Residual multi-block model

For example, three blocks of width approximately `M/3`.

If B does not outperform A, then the multi-block design may simply be a more complicated way to allocate the same feature budget.

Evidence for useful depth requires the residual organization itself to matter.

---

## 54. Additional ablations

1. RBF oracle versus linear-kernel oracle.
2. Full target every layer versus residual target.
3. Positive spectral residual versus raw residual approximation.
4. PCA-only `\Phi` versus PCA+Fisher.
5. Fixed equal rank per block versus residual-energy adaptive rank.
6. Concatenated hidden representation versus additive kernel sum.
7. One-shot low-rank RBF features versus compiled ReLU mechanism.
8. Oracle spectral embedding readout as an upper bound.

---

## 55. Failure criteria

DNS 0.5 should be considered unsuccessful in its current form if, after fair validation tuning:

- residual blocks do not reduce `E_L`;
- `E_L` decreases but test accuracy systematically does not improve;
- one-shot wide baseline is consistently as good or better;
- the compiled model requires almost `N` hidden dimensions;
- inference still effectively depends on the entire training set;
- any advantage depends on test-derived information;
- the advantage disappears across independent splits.

A negative result does not invalidate the entire DNS program. It invalidates a particular compiler design.

---

## 56. What would count as a meaningful first success?

On `digits`, we do not need a state-of-the-art headline.

A strong first-stage success would be:

1. no iterative parameter optimization;
2. 2–3 residual blocks monotonically reduce kernel reconstruction error;
3. multi-block model statistically beats a fair one-block model at equal budget;
4. test accuracy approaches the locked RBF oracle;
5. hidden representation is much smaller than `N`;
6. the result repeats across independent splits.

Only then should the project move to MNIST/Fashion-MNIST.

---

# Part XIX — Symbol glossary

## 57. Notation

| Symbol | Meaning |
|---|---|
| `D` | Dataset / learning task |
| `X` | Input matrix / features |
| `Y` | Targets / labels |
| `\theta` | Generic model parameter vector |
| `W_l` | Weights of layer `l` |
| `H_l` | Realized hidden representation at layer `l` |
| `H_l^*` | Desired/ideal hidden representation |
| `A_l` | Activations of layer `l` |
| `\Phi_l` | Candidate feature matrix / realizable feature space for block `l` |
| `T_l` | Target representation for block `l` |
| `B_l` | Closed-form projection coefficients from `\Phi_l` to `T_l` |
| `K` | Kernel / Gram matrix |
| `K^*` | Oracle or target kernel |
| `K^{(L)}` | Kernel approximation after `L` compiled blocks |
| `R_l` | Residual kernel after block `l` |
| `U,\Lambda` | Eigenvectors and eigenvalues |
| `r` | Rank / target embedding width |
| `\lambda` | Ridge regularization coefficient |
| `\gamma` | RBF bandwidth parameter in `exp(-\gamma||x-x'||^2)` |
| `Q(p)` | Quantity sold as a function of price in the market analogy |
| `\Pi(p)` | Seller profit |
| `E_L` | Relative kernel reconstruction error after `L` blocks |
| `A(K_H,K_Y)` | Kernel-target alignment |
| `e_l` | Target realizability error at layer `l` |

---

# Part XX — The entire research program in one chain

## 58. From the original intuition to the current hypothesis

The conceptual chain is:

\[
\text{unknown environment}
\Rightarrow
\text{real trials may be necessary}
\]

\[
\text{known environment + model}
\Rightarrow
\text{search can sometimes be replaced by calculation}
\]

\[
\text{training data already available}
\Rightarrow
\text{test whether direct synthesis can replace parameter search}
\]

After all refinements, the DNS program can be summarized as

\[
D
\rightarrow
\text{task/oracle geometry}
\rightarrow
\text{compact realizable representations}
\rightarrow
\text{closed-form block parameters}
\rightarrow
\text{compiled network}.
\]

For DNS 0.5 specifically:

\[
K^*_{RBF}
\rightarrow
\text{spectral targets}
\rightarrow
\text{residual realizable blocks}
\rightarrow
\sum_l H_lH_l^T \approx K^*.
\]

The most important question is no longer:

> Can any nonlinear neural model be fit without SGD?

For small and restricted settings, the answer is already clearly yes.

The real question is:

> **Can we build a scalable class of neural systems in which useful deep internal structure is designed and compiled through direct mathematical operations, rather than discovered through a long trajectory of gradient-based adaptation?**

That is the long-term objective of Direct Network Synthesis.

---

# Part XXI — Documentation and research TODOs

## 59. Formal related-work bibliography

A future `docs/related-work.md` should contain verified primary-source references for:

- closed-form linear and ridge regression;
- Extreme Learning Machines;
- deterministic/PCA/LDA ELM variants;
- random features;
- kernel ridge and low-rank kernel approximation;
- Neural Tangent Kernel;
- convex reformulations of ReLU training;
- closed-form deep/layer-wise learning;
- Forward Projection (2026);
- kernel mean embedding layer-wise methods;
- hypernetworks and dataset-to-weights meta-learning;
- kernel distillation / kernel-to-network compression;
- Nyström and spectral approximation methods.

No citation should be added merely because it sounds relevant. Every related-work claim should be tied to a verified primary source.

## 60. Canonicalization of exploratory experiment results

Every number marked **[D]** in this document must eventually pass through the repository's canonical experiment pipeline.

For each accepted result, record:

- exact command;
- configuration;
- commit SHA;
- split seeds;
- result artifact;
- summary table;
- confidence interval/statistical comparison.

Only then should the number move from “exploratory chat result” to “repository result.”

---

# 61. Final principle

The project should not try to prove the original intuition at all costs.

Its purpose is to discover the boundary between:

- information that genuinely must be acquired through adaptive search;
- and structure that can be derived from already available data and compiled by direct calculation.

If some forms of deep representation fundamentally require adaptive optimization, that is a valuable result.

If a significant portion of modern training can instead be replaced by direct synthesis, then the result would not merely be a faster optimizer. It would suggest **a different paradigm for constructing neural systems**.
