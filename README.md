# Coalescence-class cardinalities in finite grand couplings

This repository contains a self-contained preprint and the exact programs supporting a counterexample to Grimmett and Holmes, Open Problem 3.11.

**Status:** public review candidate `v1.0.0-rc.2`; the complete reproduction pipeline passes; independent peer review and publication priority remain pending.

Repository: <https://github.com/lukekabbash/finite-grand-couplings>

For every integer `m >= 1` and probability `0 < p < 1`, the construction gives one irreducible, aperiodic Markov chain on `4m+2` states and one consistent two-map grand coupling whose terminal coalescence profile is

```text
(2m, 2m+2)       with probability 1/(2-p)
(2m+1, 2m+1)     with probability (1-p)/(2-p).
```

The symbolic proof does not depend on a search. A separate computer-assisted theorem shows that no irreducible example exists on fewer than six states, without restricting support size.

## Read first

- [Academic preprint](paper/grand-coupling-counterexample.pdf)
- [Recorded exact results](results/RESULTS.md)
- [Guide for external reviewers](REVIEW_GUIDE.md)

The review guide states which claims are symbolic, which are computer-assisted, and which remain outside the established result.

## Reproduce the mathematics

Requirements:

- Python 3.10 or newer;
- a C++20 compiler;
- macOS, Linux, or WSL;
- no network access and no third-party Python package for the mathematical checks.

Run from this folder:

```sh
./reproduce.sh --trials 100000
```

The command verifies the release manifest, runs exact Python checks, compiles independent C++ verifiers, performs the exhaustive graph and two-map censuses, runs AddressSanitizer and UndefinedBehaviorSanitizer builds, and finishes with deterministic property checks and a seeded simulation smoke test. All compilation occurs in a temporary directory that is removed on exit.

If a compiler does not provide the requested sanitizers, the explicit reduced mode is:

```sh
./reproduce.sh --trials 100000 --no-sanitizers
```

That mode is labelled reduced in its output. It does not change the mathematical theorem, but it omits two implementation-safety checks.

## Build the documents

The released PDFs are included. To rebuild them exactly with the pinned document toolchain:

```sh
python3 -m pip install -r requirements-docs.txt
./build_documents.sh
```

The builder uses US Letter pages, core PDF fonts, deterministic ReportLab output, bookmarks, live reference links, and structural PDF checks. The manuscript builder is [paper/build_paper.py](paper/build_paper.py).

After an intentional edit, build, regenerate the drift ledger, and rerun all checks with:

```sh
./seal_release.sh --trials 100000
```

`MANIFEST.sha256` detects changed, missing, extra, unsafe, or symlinked release files. It is a drift ledger, not a digital signature. A public archival release should add a signed Git tag or repository/archive checksum.

## Evidence map

| Claim | Decisive evidence | Classification |
|---|---|---|
| Nonconstant terminal class sizes | Explicit maps and symbolic proof | Proved |
| Exact two-atom law | Parity argument and geometric series | Proved |
| Six states are necessary | Kernel-graph reduction plus exhaustive census | Computer-assisted |
| Implementations agree | Independent Python/C++, frozen counts, sanitizers | Verified |
| `20m+2` monoid-size formula for every `m` | Checked only through `m=24` | Not proved |
| Novelty or priority | Targeted public literature search | Not established |
| Production computing benefit | Research directions only | Not established |

Simulation is not used to prove the theorem. Discovery scripts are kept separate from verification so that exploratory history cannot be confused with evidence.

## Repository layout

```text
paper/          academic preprint, source, and PDF
verification/   theorem-bearing exact Python and C++ programs
experiments/    seeded properties, exact stationarity, and simulation checks
exploration/    discovery programs; not part of the proof
results/        frozen expected outcomes and reference run
tools/          manifest, PDF, and release utilities
```

The root scripts resolve their own location. The folder may therefore be moved, renamed, or initialized as a repository without changing paths.

## Research provenance

This is an independent experiment in AI-assisted mathematical research led by Luke Kabbash, who is not a professional mathematician and does not hold a doctorate in mathematics. The research, software, and manuscript were substantially generated with OpenAI's GPT-5.6 Sol under human direction. The project tests whether an LLM-centered workflow can produce new, independently checkable mathematical knowledge. Its claims should be treated as reproducible research claims awaiting specialist review, not as claims to conventional mathematical authority. Demonstrated errors will be documented and corrected, or the affected claims withdrawn.

## Before final v1.0.0

- Ask a probability specialist to check the forward composition convention and symbolic proof.
- Ask a transformation-semigroup specialist to check the kernel-graph reduction and terminology.
- Reimplement or independently rerun the five-state census in a third system.
- Refresh the priority search at the actual submission date.
- Choose a repository license and archive the final reviewed release.
- Add tagged-PDF accessibility if required by the venue.

## Source question

G. R. Grimmett and M. Holmes, “Coalescence in Markov Chains,” *Journal of Theoretical Probability* 39 (2026), Article 49, [doi:10.1007/s10959-026-01500-w](https://doi.org/10.1007/s10959-026-01500-w).
