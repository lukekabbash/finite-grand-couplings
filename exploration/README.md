# Exploration archive

These programs record discovery routes. They are not invoked by `reproduce.sh` and do not support theorem claims.

- `construct_n6.py` searches endomorphism supports on the graph `P3` disjoint-union `P3`.
- `search_pairs.py` explores two- and structured three-map supports on four states.
- `search_supports.cpp` is an optimized four-state support search.

Keeping exploration separate prevents a heuristic search, partial search, or early hypothesis from being mistaken for proof evidence.

