# Frozen results

Reference date: 20 July 2026.

## Symbolic result

For every `m >= 1` and `0 < p < 1`, the construction has two terminal profiles:

```text
(2m, 2m+2)       with probability 1/(2-p)
(2m+1, 2m+1)     with probability (1-p)/(2-p).
```

The induced chain is irreducible and aperiodic, and the forward coalescence number is two almost surely. This is proved without computation.

## Six-state exact checks

Independent Python and C++ implementations agree on:

```text
reachable prefix states including identity: 22
nonidentity semigroup elements: 21
minimum rank: 2
terminal profiles: (2,4), (3,3)
positive witness-prefix probabilities at p=1/2: 1/2, 1/4
```

## Computer-assisted lower bound

The exact graph classification gives:

```text
n=1,2,3,4: no graph satisfies the necessary coloring conditions

n=5 rank=3:
  150 labelled candidates in 3 isomorphism classes
  endomorphism counts 48, 42, 50
  no transitive endomorphism class

n=6 rank=2:
  90 labelled candidates in 1 isomorphism class
  representative P3 disjoint-union P3
  144 endomorphisms; transitive action
```

The `n<=5` census, together with the symbolic kernel-graph reduction in the paper, establishes that six states are necessary. The conclusion is computer-assisted and covers arbitrary finite support.

## Redundant exhaustive two-map search

```text
NO_HIT n=4
pairs=32640
strongly_connected_pairs=10476
nonsynchronizing_pairs=1152

NO_HIT n=5
pairs=4881250
strongly_connected_pairs=1277160
nonsynchronizing_pairs=60000
```

These counts are asserted at runtime. This search is independent corroboration but covers only two-map supports.

## Family and experiment sweep

- Python exact closure and rational law checks: `m=1..8`.
- Independent C++ exact closure: `m=1..24`, up to 98 states.
- Observed and asserted over that finite range: semigroup size including identity `20m+2`.
- Fixed seed: `3231835598`.
- Kernel-lock property checks: 1,684,000 through `m=100`, up to 402 states.
- Exact rational stationary calculations: zero residual in all representative cases.
- Seeded simulation: nine cells, default 100,000 trials per cell, maximum absolute z-score required to be at most 6.

The finite observation `20m+2` is not claimed as a theorem for all `m`. Simulation is a smoke test and is not used in the exact proof.

