#!/usr/bin/env python3
"""Verify the two-map grand-coupling family on two equal odd paths."""

from collections import deque
from fractions import Fraction


if not __debug__:
    raise RuntimeError("verification requires assertions; rerun Python without -O")


def compose(left, right):
    return tuple(left[right[index]] for index in range(len(right)))


def rank(mapping):
    return len(set(mapping))


def profile(mapping):
    return tuple(sorted(mapping.count(target) for target in set(mapping)))


def kernel(mapping):
    blocks = {}
    for source, target in enumerate(mapping):
        blocks.setdefault(target, []).append(source)
    return tuple(sorted(tuple(block) for block in blocks.values()))


def construction(m):
    path_size = 2 * m + 1
    state_count = 2 * path_size

    def left(index):
        return index

    def right(index):
        return path_size + index

    edges = {
        frozenset((side(index), side(index + 1)))
        for side in (left, right)
        for index in range(path_size - 1)
    }

    coloring = tuple(left(index % 2) for index in range(path_size)) + tuple(
        left(index % 2) for index in range(path_size)
    )
    shift = tuple(right(index) for index in range(path_size)) + tuple(
        left(index + 1 if index + 1 < path_size else index - 1)
        for index in range(path_size)
    )
    assert len(coloring) == len(shift) == state_count
    return edges, coloring, shift


def is_endomorphism(mapping, edges):
    return all(frozenset((mapping[left], mapping[right])) in edges for left, right in edges)


def strongly_connected(generators):
    state_count = len(generators[0])
    for source in range(state_count):
        reached = {source}
        frontier = [source]
        while frontier:
            current = frontier.pop()
            for generator in generators:
                target = generator[current]
                if target in reached:
                    continue
                reached.add(target)
                frontier.append(target)
        if len(reached) != state_count:
            return False
    return True


def closure(generators):
    identity = tuple(range(len(generators[0])))
    reached = {identity}
    frontier = deque((identity,))
    while frontier:
        current = frontier.popleft()
        for generator in generators:
            result = compose(generator, current)
            if result in reached:
                continue
            reached.add(result)
            frontier.append(result)
    return reached


def terminal_profile_distribution(coloring, shift, collapsing_probability):
    assert 0 < collapsing_probability < 1
    shift_probability = 1 - collapsing_probability
    identity = tuple(range(len(coloring)))
    powers = []
    first_seen = {}
    current = identity
    while current not in first_seen:
        first_seen[current] = len(powers)
        powers.append(current)
        current = compose(shift, current)

    cycle_start = first_seen[current]
    cycle_length = len(powers) - cycle_start
    distribution = {}
    for time, power in enumerate(powers):
        probability = collapsing_probability * shift_probability**time
        if time >= cycle_start:
            probability /= 1 - shift_probability**cycle_length
        terminal_profile = profile(compose(coloring, power))
        distribution[terminal_profile] = distribution.get(terminal_profile, Fraction()) + probability
    assert sum(distribution.values()) == 1
    return cycle_start, cycle_length, tuple(sorted(distribution.items()))


def verify(m):
    edges, coloring, shift = construction(m)
    generators = (coloring, shift)
    assert all(is_endomorphism(generator, edges) for generator in generators)
    assert strongly_connected(generators)
    assert coloring[0] == 0

    balanced = compose(coloring, shift)
    unbalanced_profile = (2 * m, 2 * m + 2)
    balanced_profile = (2 * m + 1, 2 * m + 1)
    assert profile(coloring) == unbalanced_profile
    assert profile(balanced) == balanced_profile

    semigroup = closure(generators)
    assert min(map(rank, semigroup)) == 2
    assert {
        profile(current) for current in semigroup if rank(current) == 2
    } == {unbalanced_profile, balanced_profile}
    for current in semigroup:
        if rank(current) != 2:
            continue
        for future in generators:
            continued = compose(future, current)
            assert rank(continued) == 2
            assert kernel(continued) == kernel(current)

    tested_probabilities = (Fraction(1, 7), Fraction(2, 5), Fraction(1, 2), Fraction(4, 5))
    fair_result = None
    for collapsing_probability in tested_probabilities:
        cycle_start, cycle_length, distribution = terminal_profile_distribution(
            coloring, shift, collapsing_probability
        )
        expected = tuple(
            sorted(
                (
                    (unbalanced_profile, Fraction(1, 2 - collapsing_probability)),
                    (
                        balanced_profile,
                        Fraction(1 - collapsing_probability, 2 - collapsing_probability),
                    ),
                )
            )
        )
        assert distribution == expected
        if collapsing_probability == Fraction(1, 2):
            fair_result = (cycle_start, cycle_length, distribution)
    assert fair_result is not None
    cycle_start, cycle_length, distribution = fair_result
    return (
        len(coloring),
        len(semigroup),
        unbalanced_profile,
        balanced_profile,
        cycle_start,
        cycle_length,
        distribution,
    )


def main():
    for m in range(1, 9):
        (
            state_count,
            semigroup_size,
            first_profile,
            second_profile,
            cycle_start,
            cycle_length,
            distribution,
        ) = verify(m)
        print(
            f"m={m} states={state_count} semigroup={semigroup_size} "
            f"profiles={first_profile},{second_profile} "
            f"shift_tail={cycle_start} shift_period={cycle_length} distribution={distribution}: PASS"
        )
    print("two-path grand-coupling family: PASS")


if __name__ == "__main__":
    main()
