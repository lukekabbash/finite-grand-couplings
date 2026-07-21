#!/usr/bin/env python3
"""Classify the small kernel-graph candidates up to graph isomorphism.

This is intentionally independent of kernel_graph_census.py: it uses direct
color assignments rather than set partitions and recomputes endomorphisms from
the edge predicate.  The output is a compact finite certificate for the
all-support lower bound on the number of states.
"""

from collections import Counter
from itertools import combinations, permutations, product


if not __debug__:
    raise RuntimeError("verification requires assertions; rerun Python without -O")


def edge_pairs(size):
    return tuple(combinations(range(size), 2))


def edge_set(size, code):
    return {
        pair
        for index, pair in enumerate(edge_pairs(size))
        if (code >> index) & 1
    }


def encode_graph(size, edges):
    pairs = edge_pairs(size)
    return sum(1 << index for index, pair in enumerate(pairs) if pair in edges)


def relabel_edges(edges, permutation):
    return {
        tuple(sorted((permutation[left], permutation[right])))
        for left, right in edges
    }


def canonical_code(size, edges):
    return min(
        encode_graph(size, relabel_edges(edges, permutation))
        for permutation in permutations(range(size))
    )


def coloring_data(size, edges):
    for color_count in range(1, size + 1):
        profiles = set()
        for colors in product(range(color_count), repeat=size):
            if set(colors) != set(range(color_count)):
                continue
            if any(colors[left] == colors[right] for left, right in edges):
                continue
            counts = Counter(colors)
            profiles.add(tuple(sorted(counts.values())))
        if profiles:
            return color_count, tuple(sorted(profiles))
    raise AssertionError("every finite graph is colorable")


def clique_number(size, edges):
    result = 1
    for order in range(2, size + 1):
        for vertices in combinations(range(size), order):
            if all(tuple(sorted(pair)) in edges for pair in combinations(vertices, 2)):
                result = order
    return result


def endomorphism_data(size, edges):
    maps = []
    action = [set() for _ in range(size)]
    for mapping in product(range(size), repeat=size):
        if any(
            tuple(sorted((mapping[left], mapping[right]))) not in edges
            for left, right in edges
        ):
            continue
        maps.append(mapping)
        for source, target in enumerate(mapping):
            action[source].add(target)

    closures = []
    for source in range(size):
        reached = {source}
        frontier = [source]
        while frontier:
            current = frontier.pop()
            for target in action[current]:
                if target not in reached:
                    reached.add(target)
                    frontier.append(target)
        closures.append(tuple(sorted(reached)))

    minimum_rank = min(len(set(mapping)) for mapping in maps)
    minimum_profiles = {
        tuple(sorted(Counter(mapping).values()))
        for mapping in maps
        if len(set(mapping)) == minimum_rank
    }
    return len(maps), minimum_rank, tuple(sorted(minimum_profiles)), tuple(closures)


def automorphism_count(size, edges):
    return sum(
        relabel_edges(edges, permutation) == edges
        for permutation in permutations(range(size))
    )


def components(size, edges):
    neighbors = [set() for _ in range(size)]
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    result = []
    unseen = set(range(size))
    while unseen:
        start = min(unseen)
        reached = {start}
        frontier = [start]
        while frontier:
            current = frontier.pop()
            for target in neighbors[current]:
                if target not in reached:
                    reached.add(target)
                    frontier.append(target)
        result.append(tuple(sorted(reached)))
        unseen -= reached
    return tuple(sorted(result, key=lambda block: (len(block), block)))


def classify(size, required_rank=None):
    pairs = edge_pairs(size)
    classes = Counter()
    representatives = {}
    for code in range(1 << len(pairs)):
        edges = edge_set(size, code)
        if any(not any(vertex in edge for edge in edges) for vertex in range(size)):
            continue
        chromatic, profiles = coloring_data(size, edges)
        if required_rank is not None and chromatic != required_rank:
            continue
        if len(profiles) < 2 or clique_number(size, edges) != chromatic:
            continue
        canonical = canonical_code(size, edges)
        classes[canonical] += 1
        representatives.setdefault(canonical, edge_set(size, canonical))

    print(
        f"n={size} rank={required_rank or 'any'} "
        f"labelled={sum(classes.values())} isomorphism_classes={len(classes)}"
    )
    transitivity = []
    certificates = {}
    for index, canonical in enumerate(sorted(classes), start=1):
        edges = representatives[canonical]
        degrees = tuple(
            sorted(sum(vertex in edge for edge in edges) for vertex in range(size))
        )
        chromatic, profiles = coloring_data(size, edges)
        endomorphisms, minimum_rank, minimum_profiles, closures = endomorphism_data(
            size, edges
        )
        transitive = all(len(closure) == size for closure in closures)
        transitivity.append(transitive)
        certificates[canonical] = {
            "endomorphisms": endomorphisms,
            "minimum_rank": minimum_rank,
            "minimum_profiles": minimum_profiles,
            "transitive": transitive,
        }
        print(
            f"  class={index} labelled={classes[canonical]} canonical={canonical} "
            f"edges={sorted(edges)} degrees={degrees} components={components(size, edges)}"
        )
        print(
            f"    omega=chi={chromatic} coloring_profiles={profiles} "
            f"automorphisms={automorphism_count(size, edges)}"
        )
        print(
            f"    endomorphisms={endomorphisms} min_rank={minimum_rank} "
            f"min_profiles={minimum_profiles} transitive={transitive} closures={closures}"
        )
    return classes, tuple(transitivity), certificates


def main():
    for size in range(1, 5):
        classes, transitivity, certificates = classify(size)
        assert not classes
        assert transitivity == ()
        assert not certificates

    five_classes, five_transitivity, five_certificates = classify(5)
    assert five_classes == Counter({31: 30, 59: 60, 63: 60})
    assert five_transitivity == (False, False, False)
    assert {
        code: certificate["endomorphisms"]
        for code, certificate in five_certificates.items()
    } == {31: 48, 59: 42, 63: 50}
    assert all(
        certificate["minimum_rank"] == 3
        and certificate["minimum_profiles"] == ((1, 1, 3), (1, 2, 2))
        and not certificate["transitive"]
        for certificate in five_certificates.values()
    )

    six_classes, six_transitivity, six_certificates = classify(6, required_rank=2)
    assert tuple(six_classes.values()) == (90,)
    assert six_transitivity == (True,)
    assert len(six_certificates) == 1
    six_certificate = next(iter(six_certificates.values()))
    assert six_certificate == {
        "endomorphisms": 144,
        "minimum_rank": 2,
        "minimum_profiles": ((2, 4), (3, 3)),
        "transitive": True,
    }
    print("small kernel-graph isomorphism classification: PASS")


if __name__ == "__main__":
    main()
