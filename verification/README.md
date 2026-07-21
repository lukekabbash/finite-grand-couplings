# Verification programs

These files support theorem claims and are run by `../reproduce.sh`.

- `verify_counterexample.py` closes the six-state semigroup exactly, checks consistency, irreducibility, minimum rank, both kernels, and kernel locking.
- `verify_counterexample.cpp` independently builds the reachable prefix-product chain from the identity.
- `verify_family.py` checks the family exactly for `m=1..8` and four rational values of `p`.
- `verify_family_independent.cpp` uses a separately written constructor and closure routine through `m=24`.
- `kernel_graph_census.py` performs the primary exhaustive labelled graph census.
- `classify_kernel_graphs.py` independently recomputes colorings, isomorphism classes, and endomorphism actions.
- `search_two_map_minimality.cpp` exhausts every unordered map pair on four and five states. It is a redundant lower-bound check, not the proof for arbitrary support.

All Python checks require assertions. The assertion-based C++ verifiers reject `NDEBUG`. The exhaustive C++ search freezes its exact aggregate counters with ordinary runtime checks.

