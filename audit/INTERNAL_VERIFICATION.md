# Internal Verification Report

**Subject:** Coalescence-Class Cardinalities in Finite Grand Couplings Need Not Be Deterministic  
**Date:** 20 July 2026  
**Nature of review:** internal adversarial verification; not independent peer review

## Executive conclusion

The explicit counterexample and its full `4m+2` family withstand the internal audit. For each `m >= 1` and `0 < p < 1`, one fixed map law and its induced transition matrix produce two terminal block-size profiles with positive probability:

```text
(2m, 2m+2)       with probability 1/(2-p)
(2m+1, 2m+1)     with probability (1-p)/(2-p).
```

The induced chain is irreducible and aperiodic. Exactly two coalescence classes remain almost surely. The negative answer is established symbolically and does not depend on computation or simulation.

The claim that six states are necessary also withstands the audit, but it is a computer-assisted theorem. Its reduction to a finite graph problem is mathematical; its last step relies on exhaustive enumeration. Two differently organized Python implementations agree on the complete small-graph classification, and a narrower C++ search independently rules out every two-map support on four and five states.

| Claim | Disposition | Meaning |
|---|---|---|
| Counterexample family | Verified | Complete symbolic proof checked step by step. |
| Exact terminal law | Verified | Exact geometric sums; no simulation. |
| Six-state minimality | Computer-assisted | Symbolic reduction plus exhaustive finite census. |
| Reproducibility | Verified on reference platform | Exact Python/C++, sanitizers, fixed outputs, and manifest checks. |
| Novelty and priority | Not established | Targeted public search found no resolution; external review remains necessary. |
| Computing applications | Not established | Concrete research programs are identified, but no production benefit is claimed. |

## 1. Scope and standard of review

This audit asks six narrow questions:

- Does the theorem answer the forward question actually posed by Grimmett and Holmes?
- Is the map law consistent with one transition matrix, and is that chain irreducible?
- Can a rank-one word occur, or can a rank-two kernel later change?
- Does the parity calculation give the stated profiles and probabilities for every `m`?
- Does the finite census prove minimality for arbitrary support, rather than only for two maps?
- Can a third party reproduce every computer-assisted claim from the standalone folder?

The audit checked the version-of-record source, reconstructed the proof independently from the map definitions, reviewed every theorem-bearing program, compared independent implementations, ran the complete reproduction entry point, and inspected the generated PDFs page by page. It also separated mathematical novelty from known transformation-semigroup terminology.

This is not an independent audit in the scholarly sense. The same research process that assembled the manuscript also performed this verification. The report is useful because it makes the proof obligations, tests, and remaining risks explicit; it cannot replace review by probability and transformation-semigroup specialists.

## 2. Fit to the published question

Grimmett and Holmes define the forward product by applying the common random maps in chronological order, so the prefix map is

```text
Q_t = F_t F_{t-1} ... F_1,       (fg)(x) = f(g(x)).
```

Their Open Problem 3.11 asks whether the cardinalities, with repetition, of the coalescence classes are deterministic. A negative answer requires one finite state space, one fixed probability law on maps, its fixed consistent transition matrix, and two distinct terminal size multisets with positive probability.

The construction meets that burden. It does not vary the transition matrix or coupling between outcomes. For fixed `m` and `p`, the only randomness is the i.i.d. sequence drawn from the same two maps `A` and `C`.

## 3. Symbolic theorem audit

### 3.1 Construction

Let each of two paths have vertices indexed `0,...,2m`. Write their vertices as `L_i` and `R_i`. The maps are

```text
A(L_i) = A(R_i) = L_(i mod 2)

C(L_i) = R_i
C(R_i) = L_(i+1)       for i < 2m
C(R_(2m)) = L_(2m-1).
```

The map law is `mu = p delta_A + (1-p) delta_C`. Its transition matrix is defined by

```text
P(x,y) = p 1{A(x)=y} + (1-p) 1{C(x)=y}.
```

Consistency is therefore an identity, not an inferred property.

### 3.2 Irreducibility and aperiodicity

Starting from `L_0`, repeated application of `C` visits every vertex before entering its final four-cycle. From an arbitrary state, repeated `C` steps reach that cycle. The cycle contains an even-indexed vertex, and `A` sends every even-indexed vertex to `L_0`. Thus every state reaches `L_0`, and `L_0` reaches every state. The positive-transition digraph is strongly connected, so `P` is irreducible.

The map `A` fixes `L_0`. Since `p > 0`, the irreducible chain has a positive self-loop and is aperiodic.

### 3.3 Exclusion of rank one

Use the auxiliary simple graph consisting of the two disjoint paths. Both supported maps preserve every edge:

- `A` is the parity coloring into the adjacent vertices `L_0` and `L_1`.
- `C` sends every left-path edge to the corresponding right-path edge.
- Away from the right endpoint, `C` shifts a right-path edge one step along the left path.
- The final edge is reflected and maps to the same final left-path edge with reversed orientation.

Every supported word is therefore a graph endomorphism. The graph is nonempty and loopless. A constant map would send an edge to a loop, so no supported word has rank one.

### 3.4 Almost-sure arrival at rank two

The first occurrence of `A` is almost sure because `p > 0` and the draws are i.i.d. If `T` initial copies of `C` precede it, the prefix product is `A C^T`. Its rank is at most the rank of `A`, which is two. Rank one is impossible, so the prefix has rank exactly two.

### 3.5 Kernel permanence

For any maps `f` and `q`, equality `q(x)=q(y)` implies `fq(x)=fq(y)`. Left composition may merge kernel blocks but cannot split them. After the first `A`, every later prefix remains an endomorphism and therefore has rank at least two; ordinary rank monotonicity gives rank at most two. Its rank stays two. A strict merger of kernel blocks would reduce that rank, so the kernel itself is permanent.

This point is decisive. It converts two short positive-probability prefixes into terminal outcomes, rather than merely transient profiles.

### 3.6 Parity calculation for arbitrary `m`

The map `C^2` remains on the same path and reverses the index parity of every vertex. This remains true at the reflected endpoint. An even power of `C` therefore puts the two paths in the same parity phase. Each path has `m+1` even-indexed vertices and `m` odd-indexed vertices, so `A C^T` has sorted profile `(2m,2m+2)` when `T` is even.

An odd power puts the two paths in opposite phases before `A` identifies them by parity. Each resulting fiber receives `m` vertices from one path and `m+1` from the other. The profile is `(2m+1,2m+1)`.

### 3.7 Exact law

The waiting time `T` has `Pr(T=t)=p(1-p)^t`. Hence

```text
Pr(T even) = p sum_(k>=0) (1-p)^(2k)     = 1/(2-p)
Pr(T odd)  = p sum_(k>=0) (1-p)^(2k+1)   = (1-p)/(2-p).
```

Both probabilities are positive for `0 < p < 1`. The terminal profile is therefore genuinely nonconstant.

### 3.8 Verdict on the main theorem

No logical gap was found. The proof handles the full parameter range, uses the forward composition convention, proves consistency and irreducibility, rules out later kernel change, and derives the law exactly. The six-state case is not an isolated computer discovery; it is the first member of a symbolic infinite family.

## 4. Minimality audit

### 4.1 Symbolic reduction

Let `M` be the monoid generated by the support and let `r` be its minimum rank. A fixed word of rank `r` has positive probability and occurs almost surely in disjoint i.i.d. blocks. Once it occurs, the prefix reaches rank `r` and its kernel becomes permanent. Irreducibility of the induced chain is equivalent to transitivity of `M` on the state set.

Define the kernel graph `Gr(M)` by joining two distinct vertices when no element of `M` collapses them. Then:

- every member of `M` is an endomorphism of `Gr(M)`;
- the image of a minimum-rank map is an `r`-clique;
- the fibers of that map form a proper `r`-coloring;
- consequently `omega(Gr(M)) = chi(Gr(M)) = r`;
- random terminal profiles require at least two optimal coloring-size profiles;
- transitivity and the existence of an edge rule out isolated vertices; and
- `End(Gr(M))` is transitive because it contains the transitive monoid `M`.

These are necessary conditions for every smaller counterexample, regardless of support size.

### 4.2 Exhaustive census

The primary census enumerates every labelled simple graph through six vertices, every set partition required to compute exact optimal coloring profiles, and every vertex subset required for the clique number. For the relevant graphs through five vertices it enumerates all endofunctions and retains exactly the graph endomorphisms.

The independent classifier uses direct surjective color assignments rather than set partitions, recomputes the edge predicate, canonicalizes under every relabelling, and freezes detailed structural outputs.

The exact result is:

```text
n = 1,2,3,4: no graph passes the coloring filter

n = 5, rank 3:
  150 labelled graphs
  3 isomorphism classes
  endomorphism counts 48, 42, 50
  0 transitive endomorphism monoids

n = 6, rank 2:
  90 labelled graphs
  1 isomorphism class: P3 disjoint-union P3
  144 endomorphisms
  transitive endomorphism monoid
```

The three five-state types all have profiles `(1,1,3)` and `(1,2,2)`, but fail transitivity. Thus none can be the kernel graph of an irreducible counterexample. The six-state type has profiles `(2,4)` and `(3,3)` and is realized by the construction.

### 4.3 Redundant two-map search

The C++ pair search independently enumerates every unordered pair of self-maps at orders four and five. It freezes the following totals and exits with an error if they change:

```text
n=4: pairs=32640, strongly_connected=10476, nonsynchronizing=1152
n=5: pairs=4881250, strongly_connected=1277160, nonsynchronizing=60000
```

No pair has multiple minimum-rank profiles. This agrees with the graph theorem but proves less: it covers two-map support only. The manuscript correctly relies on the graph census for unrestricted support.

### 4.4 Verdict on minimality

The reduction is valid and the programs exhaust the stated finite spaces. The state-minimality theorem is properly labelled computer-assisted. A fully human proof of the five-state obstruction would strengthen presentation but is not required for the central counterexample.

## 5. Code and reproducibility audit

### 5.1 Evidence roles

| Component | Role | Dependence |
|---|---|---|
| `verify_counterexample.py` | Exact semigroup closure and kernel locking | Python standard library |
| `verify_counterexample.cpp` | Independent prefix-chain construction | C++20 |
| `verify_family.py` | Exact family law and closure for `m=1..8` | Python standard library |
| `verify_family_independent.cpp` | Independent family sweep for `m=1..24` | C++20 |
| `kernel_graph_census.py` | Primary labelled graph census | Python standard library |
| `classify_kernel_graphs.py` | Independent isomorphism classification | Python standard library |
| `search_two_map_minimality.cpp` | Redundant exhaustive pair search | C++20 |
| `experiment_suite.py` | Property, stationarity, and simulation smoke tests | Python standard library |

Discovery scripts are isolated under `exploration/`. They show how the example was found, but they are not invoked by the proof reproduction and do not carry theorem claims.

### 5.2 Fail-closed behavior

The Python verifiers refuse execution with assertions disabled under `python -O`. The C++ assertion-based verifiers refuse compilation with `NDEBUG`. The exhaustive pair search uses explicit frozen counters rather than `assert`, so release builds cannot silently omit its checks.

The reproduction script validates the trial count, checks required tools, compiles into a fresh temporary directory, and removes that directory on exit. Sanitizers are part of the default run. The explicit `--no-sanitizers` option is available for unsupported toolchains and prints that the run is reduced.

### 5.3 Independent and stress checks

The exact implementations agree on the six-state prefix-chain size, semigroup size, minimum rank, and profiles. Family closure is checked through 98 states in the independent C++ implementation. The experiment suite performs 1,684,000 fixed-seed kernel-lock checks through `m=100`, exact rational stationary calculations on representative chains, and seeded Monte Carlo comparisons with a six-standard-deviation smoke-test threshold.

Monte Carlo is not proof evidence. Its only purpose is to catch an implementation whose empirical behavior is plainly incompatible with the exact law.

### 5.4 Manifest and trust boundary

`MANIFEST.sha256` covers the release files, including PDFs and theorem-bearing source. The verifier rejects missing, changed, extra, unsafe, or symlinked release files. This detects drift inside a checked copy. It is not a digital signature and cannot prove who created the release. A public version should add a signed Git tag or archival checksum from a trusted repository.

## 6. Literature and claim-scope audit

The source question is real and appears as Open Problem 3.11 in the 2026 version of record. Targeted searches through the audit date found no public paper that explicitly resolves it. That search does not cover private manuscripts, unpublished correspondence, every differently worded result, or work posted after the search.

Several surrounding ideas are established:

- the integer partition of kernel block sizes is known as kernel type;
- minimum-rank ideals and random walks on finite transformation semigroups are established subjects;
- kernel graphs and the equality of clique and chromatic numbers are established tools in synchronization theory; and
- random mapping representations and coupling from the past are classical.

The defensible candidate contribution is therefore specific: the counterexample to Open Problem 3.11, the exact family and its two-atom terminal law, and the computer-assisted state-minimality theorem. The manuscript does not claim to invent kernel type, minimum-rank theory, or finite-semigroup hitting distributions.

One conceptual correction is retained prominently. Unequal cardinalities do not imply unequal stationary block masses. In this transitive setting, Steinberg's theorem gives stationary mass `1/r` to every block of a minimum-rank kernel. The distinction here is block cardinality and uniform-label mass, not stationary imbalance.

## 7. Application claims

The result supports concrete research tools but no immediate technology claim. A finite coupling profiler can build the reachable prefix-product chain, mark minimum-rank kernels, and solve for the exact terminal profile distribution. Coupling design can then be posed as optimization over random mapping representations consistent with a fixed transition matrix.

Those directions could matter in finite automata, exact-sampling diagnostics, state aggregation, or common-noise simulations. The present work does not demonstrate faster sampling, better load balancing, improved reliability, or commercial value. Forward and backward products also differ, so no coupling-from-the-past improvement follows without additional proof.

## 8. Residual risks and external work

- No independent probability specialist has checked the composition convention, irreducibility proof, or terminal-law argument.
- No independent transformation-semigroup specialist has checked the kernel-graph reduction and use of known terminology.
- No third implementation in a computer algebra or graph package has reproduced the full five-state census.
- Priority is not established by a public archival timestamp or exhaustive literature review.
- The PDF is visually checked but is not a tagged accessibility PDF.
- The monoid-size formula `20m+2` is observed and asserted over a finite range only.
- The proposed computing applications remain research hypotheses.

## 9. Final disposition

Within the limits of an internal audit, the central counterexample is ready for external mathematical review. It is short, exact, and independently reproducible from the supplied definitions. The infinite family materially strengthens the six-state witness. The state-minimality result is credible and reproducible when described, as it is here, as computer-assisted.

The strongest responsible statement is:

> The manuscript gives a complete symbolic negative answer to the published determinism question, together with an exact infinite family and a reproducible computer-assisted proof that six states are necessary. Independent peer review and priority confirmation remain outstanding.

