#!/usr/bin/env python3
"""Census the smallest kernel graphs with multiple optimal color profiles."""

from itertools import combinations, product


if not __debug__:
    raise RuntimeError("verification requires assertions; rerun Python without -O")


def set_partitions(size):
    blocks = []

    def visit(vertex):
        if vertex == size:
            yield tuple(blocks)
            return
        bit = 1 << vertex
        for index in range(len(blocks)):
            blocks[index] |= bit
            yield from visit(vertex + 1)
            blocks[index] ^= bit
        blocks.append(bit)
        yield from visit(vertex + 1)
        blocks.pop()

    yield from visit(0)


def profile(partition):
    return tuple(sorted(block.bit_count() for block in partition))


def endomorphism_action(size, pairs, graph_code):
    edges = {
        frozenset((left, right))
        for index, (left, right) in enumerate(pairs)
        if (graph_code >> index) & 1
    }
    endomorphisms = []
    action = [set() for _ in range(size)]
    for mapping in product(range(size), repeat=size):
        if any(frozenset((mapping[left], mapping[right])) not in edges for left, right in edges):
            continue
        endomorphisms.append(mapping)
        for source, target in enumerate(mapping):
            action[source].add(target)

    for source in range(size):
        reached = {source}
        frontier = [source]
        while frontier:
            current = frontier.pop()
            for target in action[current]:
                if target in reached:
                    continue
                reached.add(target)
                frontier.append(target)
        if len(reached) != size:
            return False, (), len(endomorphisms)

    minimum_rank = min(len(set(mapping)) for mapping in endomorphisms)
    profiles = {
        tuple(sorted(mapping.count(target) for target in set(mapping)))
        for mapping in endomorphisms
        if len(set(mapping)) == minimum_rank
    }
    return len(profiles) > 1, tuple(sorted(profiles)), len(endomorphisms)


def census(size):
    pairs = tuple(combinations(range(size), 2))
    partitions = tuple(set_partitions(size))
    assert len(partitions) == (1, 2, 5, 15, 52, 203)[size - 1]
    first = {}
    qualifying = {}
    endomorphism_hits = {}

    for graph_code in range(1 << len(pairs)):
        neighbor_masks = [0] * size
        edge_masks = []
        for edge_index, (left, right) in enumerate(pairs):
            if not (graph_code >> edge_index) & 1:
                continue
            neighbor_masks[left] |= 1 << right
            neighbor_masks[right] |= 1 << left
            edge_masks.append((1 << left) | (1 << right))
        if any(mask == 0 for mask in neighbor_masks):
            continue

        proper = []
        chromatic_number = size
        for partition in partitions:
            if len(partition) > chromatic_number:
                continue
            if any(any((block & edge) == edge for edge in edge_masks) for block in partition):
                continue
            if len(partition) < chromatic_number:
                chromatic_number = len(partition)
                proper.clear()
            proper.append(partition)

        clique_number = 1
        for vertices in range(1, 1 << size):
            order = vertices.bit_count()
            if order <= clique_number:
                continue
            if all(
                not (vertices >> left) & 1
                or not (vertices >> right) & 1
                or (neighbor_masks[left] >> right) & 1
                for left, right in pairs
            ):
                clique_number = order

        if clique_number != chromatic_number:
            continue
        profiles = sorted({profile(partition) for partition in proper})
        if len(profiles) < 2:
            continue
        qualifying[chromatic_number] = qualifying.get(chromatic_number, 0) + 1
        if size <= 5:
            action_hit, action_profiles, endomorphism_count = endomorphism_action(size, pairs, graph_code)
            if action_hit and chromatic_number not in endomorphism_hits:
                edges = [pairs[index] for index in range(len(pairs)) if (graph_code >> index) & 1]
                endomorphism_hits[chromatic_number] = (edges, action_profiles, endomorphism_count)
        if chromatic_number not in first:
            edges = [pairs[index] for index in range(len(pairs)) if (graph_code >> index) & 1]
            first[chromatic_number] = (edges, profiles)

    return qualifying, first, endomorphism_hits


def main():
    expected = {
        1: {},
        2: {},
        3: {},
        4: {},
        5: {3: 150},
        6: {2: 90, 3: 13_500, 4: 1_770},
    }
    for size in range(1, 7):
        qualifying, first_by_rank, endomorphism_hits = census(size)
        assert qualifying == expected[size]
        if size <= 5:
            assert not endomorphism_hits
        print(f"n={size} qualifying_graphs_by_rank={qualifying}")
        for rank, (edges, profiles) in sorted(first_by_rank.items()):
            print(f"  rank={rank} first edges={edges} profiles={profiles}")
        for rank, (edges, profiles, count) in sorted(endomorphism_hits.items()):
            print(f"  endomorphism_hit rank={rank} maps={count} edges={edges} profiles={profiles}")
    print("kernel-graph census: PASS")


if __name__ == "__main__":
    main()
