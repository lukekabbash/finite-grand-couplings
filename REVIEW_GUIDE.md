# External review guide

This is the `v1.0.0-rc.2` public review candidate. It is intended to make the strongest claims easy to attack, reproduce, or correct before a final release.

## Highest-value mathematical checks

1. Check the forward composition convention and the proof that the first occurrence of the collapsing map permanently fixes the terminal kernel.
2. Check the exact two-atom terminal-profile law for the full `4m+2` family.
3. Check the kernel-graph reduction used to turn state minimality into a finite graph census.
4. Independently rerun or reimplement the five-state obstruction. The included Python classifiers and narrower C++ two-map search are deliberately organized differently, but they are not independent peer review.
5. Search for prior resolutions of Grimmett and Holmes, Open Problem 3.11, or equivalent constructions under different terminology.

## Reproduce the package

From the repository root:

```sh
./reproduce.sh --trials 100000
```

The command verifies the release manifest, runs the exact Python checks, compiles independent C++ verifiers, executes the exhaustive censuses, runs sanitizer builds, and finishes with deterministic properties and a seeded simulation smoke test. The simulation is not part of the proof.

To rebuild the manuscript with the pinned Python dependencies:

```sh
python3 -m pip install -r requirements-docs.txt
./build_documents.sh
```

## Claim boundaries

- The counterexample family and its probability law are symbolic claims.
- The assertion that six states are necessary is computer-assisted.
- The observed monoid-size formula is not claimed for all family members.
- Novelty and publication priority remain provisional pending specialist review.

Please report mathematical objections, reproduction failures, or relevant prior work through [GitHub Issues](https://github.com/lukekabbash/finite-grand-couplings/issues). Demonstrated errors will be documented and corrected, or the affected claims withdrawn.
