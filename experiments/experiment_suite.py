#!/usr/bin/env python3
"""Seeded experiments for the two-path grand-coupling family.

The theorem is symbolic.  These experiments are deliberately redundant: they
test the construction at larger sizes, compare the exact profile law with
simulation, verify kernel locking under random continuations, and check exact
stationarity of the induced Markov matrix using rational arithmetic.
"""

import argparse
import json
import platform
import random
from collections import Counter, deque
from fractions import Fraction


SEED = 0xC0A1E5CE
MAX_ABS_Z_SCORE = 6.0


if not __debug__:
    raise RuntimeError("verification requires assertions; rerun Python without -O")


def compose(left, right):
    return tuple(left[right[index]] for index in range(len(right)))


def profile(mapping):
    return tuple(sorted(Counter(mapping).values()))


def construction(m):
    path_size = 2 * m + 1
    coloring = tuple(index % 2 for index in range(path_size)) * 2
    shift = tuple(path_size + index for index in range(path_size)) + tuple(
        index + 1 if index + 1 < path_size else index - 1
        for index in range(path_size)
    )
    return coloring, shift


def strongly_connected(generators):
    size = len(generators[0])
    for source in range(size):
        reached = {source}
        frontier = [source]
        while frontier:
            current = frontier.pop()
            for generator in generators:
                target = generator[current]
                if target not in reached:
                    reached.add(target)
                    frontier.append(target)
        if len(reached) != size:
            return False
    return True


def closure(generators):
    identity = tuple(range(len(generators[0])))
    reached = {identity}
    frontier = deque((identity,))
    while frontier:
        current = frontier.popleft()
        for generator in generators:
            candidate = compose(generator, current)
            if candidate not in reached:
                reached.add(candidate)
                frontier.append(candidate)
    return reached


def solve_stationary(generators, probabilities):
    size = len(generators[0])
    matrix = [[Fraction() for _ in range(size)] for _ in range(size)]
    for generator, probability in zip(generators, probabilities, strict=True):
        for source, target in enumerate(generator):
            matrix[source][target] += probability

    # Solve (P^T-I) pi = 0 with the last equation replaced by sum(pi)=1.
    system = []
    for row in range(size - 1):
        system.append(
            [matrix[column][row] - Fraction(row == column) for column in range(size)]
            + [Fraction()]
        )
    system.append([Fraction(1) for _ in range(size)] + [Fraction(1)])

    for pivot in range(size):
        pivot_row = next(row for row in range(pivot, size) if system[row][pivot])
        system[pivot], system[pivot_row] = system[pivot_row], system[pivot]
        divisor = system[pivot][pivot]
        system[pivot] = [value / divisor for value in system[pivot]]
        for row in range(size):
            if row == pivot or not system[row][pivot]:
                continue
            multiplier = system[row][pivot]
            system[row] = [
                left - multiplier * right
                for left, right in zip(system[row], system[pivot], strict=True)
            ]

    stationary = tuple(system[row][-1] for row in range(size))
    assert all(value > 0 for value in stationary)
    assert sum(stationary) == 1
    for target in range(size):
        assert sum(
            stationary[source] * matrix[source][target] for source in range(size)
        ) == stationary[target]
    return stationary


def exact_law(p):
    return Fraction(1, 2 - p), Fraction(1 - p, 2 - p)


def simulate(m, p, trials, rng):
    coloring, shift = construction(m)
    unbalanced = profile(coloring)
    balanced = profile(compose(coloring, shift))
    counts = Counter()
    for _ in range(trials):
        current = tuple(range(len(coloring)))
        while True:
            generator = coloring if rng.random() < float(p) else shift
            current = compose(generator, current)
            if generator == coloring:
                break
        observed = profile(current)
        assert observed in (unbalanced, balanced)
        counts[observed] += 1
    expected_unbalanced, _ = exact_law(p)
    observed_unbalanced = Fraction(counts[unbalanced], trials)
    variance = float(expected_unbalanced * (1 - expected_unbalanced) / trials)
    z_score = (float(observed_unbalanced - expected_unbalanced) / variance**0.5)
    return {
        "m": m,
        "states": 4 * m + 2,
        "p": f"{p.numerator}/{p.denominator}",
        "trials": trials,
        "unbalanced_profile": unbalanced,
        "balanced_profile": balanced,
        "observed_unbalanced": float(observed_unbalanced),
        "expected_unbalanced": float(expected_unbalanced),
        "absolute_error": abs(float(observed_unbalanced - expected_unbalanced)),
        "z_score": z_score,
    }


def property_sweep(max_m, rng):
    checks = 0
    for m in range(1, max_m + 1):
        coloring, shift = construction(m)
        generators = (coloring, shift)
        assert strongly_connected(generators)
        unbalanced = (2 * m, 2 * m + 2)
        balanced = (2 * m + 1, 2 * m + 1)

        power = tuple(range(len(coloring)))
        for time in range(8 * m + 17):
            collapsed = compose(coloring, power)
            assert profile(collapsed) == (unbalanced if time % 2 == 0 else balanced)
            locked_profile = profile(collapsed)
            for _ in range(40):
                collapsed = compose(rng.choice(generators), collapsed)
                assert profile(collapsed) == locked_profile
                assert len(set(collapsed)) == 2
                checks += 1
            power = compose(shift, power)
    return checks


def semigroup_sweep(max_m):
    observations = []
    for m in range(1, max_m + 1):
        generators = construction(m)
        semigroup = closure(generators)
        minimum_rank = min(len(set(mapping)) for mapping in semigroup)
        profiles = sorted(
            {
                profile(mapping)
                for mapping in semigroup
                if len(set(mapping)) == minimum_rank
            }
        )
        assert minimum_rank == 2
        assert profiles == [(2 * m, 2 * m + 2), (2 * m + 1, 2 * m + 1)]
        observations.append(
            {
                "m": m,
                "states": 4 * m + 2,
                "semigroup_size": len(semigroup),
                "observed_size_formula": 20 * m + 2,
                "minimum_rank": minimum_rank,
                "minimum_profiles": profiles,
            }
        )
        assert len(semigroup) == 20 * m + 2
    return observations


def run(trials):
    rng = random.Random(SEED)
    property_checks = property_sweep(100, rng)
    semigroups = semigroup_sweep(24)
    simulations = [
        simulate(m, p, trials, rng)
        for m in (1, 7, 25)
        for p in (Fraction(1, 5), Fraction(1, 2), Fraction(4, 5))
    ]
    maximum_absolute_z_score = max(abs(cell["z_score"]) for cell in simulations)
    assert maximum_absolute_z_score <= MAX_ABS_Z_SCORE
    stationarity = []
    for m, p in ((1, Fraction(1, 2)), (4, Fraction(2, 5)), (12, Fraction(4, 5))):
        coloring, shift = construction(m)
        stationary = solve_stationary((coloring, shift), (p, 1 - p))
        stationarity.append(
            {
                "m": m,
                "states": 4 * m + 2,
                "p": f"{p.numerator}/{p.denominator}",
                "minimum_mass": str(min(stationary)),
                "maximum_mass": str(max(stationary)),
                "denominator_lcm_proxy": max(value.denominator for value in stationary),
                "residual": "0 (exact rational arithmetic)",
            }
        )
    return {
        "status": "PASS",
        "python": platform.python_implementation() + " " + platform.python_version(),
        "seed": SEED,
        "simulation_acceptance_rule": f"max absolute z-score <= {MAX_ABS_Z_SCORE}",
        "maximum_absolute_z_score": maximum_absolute_z_score,
        "property_checks": property_checks,
        "property_range": "m=1..100",
        "semigroup_observations": semigroups,
        "simulations": simulations,
        "stationarity": stationarity,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=100_000)
    args = parser.parse_args()
    if args.trials < 2:
        parser.error("--trials must be at least 2")
    print(json.dumps(run(args.trials), indent=2))


if __name__ == "__main__":
    main()
