#!/usr/bin/env python3
"""Exhaust two-map supports on four labelled states exactly."""

from itertools import combinations, permutations, product


N = 4
MAPS = tuple(product(range(N), repeat=N))


def compose(left, right):
    """Return left o right, matching F_t o ... o F_1."""
    return tuple(left[right[i]] for i in range(N))


def rank(f):
    return len(set(f))


def profile(f):
    counts = [0] * N
    for y in f:
        counts[y] += 1
    return tuple(sorted(c for c in counts if c))


def strongly_connected(gens):
    adjacency = [{f[i] for f in gens} for i in range(N)]
    for source in range(N):
        seen = {source}
        stack = [source]
        while stack:
            u = stack.pop()
            for v in adjacency[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        if len(seen) != N:
            return False
    return True


def closure(gens):
    # Every nonempty word. Closing under generator multiplication on both
    # sides is redundant mathematically but guards the formulation.
    semigroup = set(gens)
    frontier = list(gens)
    while frontier:
        a = frontier.pop()
        for b in tuple(semigroup):
            for c in (compose(a, b), compose(b, a)):
                if c not in semigroup:
                    semigroup.add(c)
                    frontier.append(c)
    return semigroup


def closure_or_constant(gens):
    semigroup = set(gens)
    if any(rank(f) == 1 for f in semigroup):
        return None
    frontier = list(gens)
    while frontier:
        a = frontier.pop()
        for b in tuple(semigroup):
            for c in (compose(a, b), compose(b, a)):
                if rank(c) == 1:
                    return None
                if c not in semigroup:
                    semigroup.add(c)
                    frontier.append(c)
    return semigroup


def main():
    checked_sc = 0
    hits = []
    for gens in combinations(MAPS, 2):
        if not strongly_connected(gens):
            continue
        checked_sc += 1
        sg = closure(gens)
        minimum = min(map(rank, sg))
        if minimum != 2:
            continue
        profiles = {profile(f) for f in sg if rank(f) == minimum}
        if (1, 3) in profiles and (2, 2) in profiles:
            hits.append((gens, len(sg)))
            print("HIT", gens, "semigroup_size", len(sg))
            break
    print(f"strongly_connected_two_supports_checked={checked_sc}")
    print(f"hit_count_before_stop={len(hits)}")

    # Structured three-generator search: two rank-two maps share a two-point
    # image and permute that image, while a permutation restores irreducibility.
    permutations4 = tuple(permutations(range(N)))
    structured_checked = 0
    for image in combinations(range(N), 2):
        image_set = set(image)
        compatible = [
            f for f in MAPS
            if set(f) == image_set and set(f[i] for i in image) == image_set
        ]
        thirteens = [f for f in compatible if profile(f) == (1, 3)]
        twotwos = [f for f in compatible if profile(f) == (2, 2)]
        for a in thirteens:
            for b in twotwos:
                for p in permutations4:
                    gens = (a, b, p)
                    if not strongly_connected(gens):
                        continue
                    structured_checked += 1
                    sg = closure(gens)
                    minimum = min(map(rank, sg))
                    profiles = {profile(f) for f in sg if rank(f) == minimum}
                    if minimum == 2 and {(1, 3), (2, 2)} <= profiles:
                        print("STRUCTURED_HIT", gens, "semigroup_size", len(sg))
                        print(f"structured_supports_checked={structured_checked}")
                        return
    print(f"structured_supports_checked={structured_checked}")

    # Complete search among supports consisting of one permutation and an
    # explicit rank-two map of each target profile.
    thirteens = [f for f in MAPS if profile(f) == (1, 3)]
    twotwos = [f for f in MAPS if profile(f) == (2, 2)]
    explicit_checked = 0
    for a in thirteens:
        for b in twotwos:
            for p in permutations4:
                gens = (a, b, p)
                if not strongly_connected(gens):
                    continue
                explicit_checked += 1
                sg = closure_or_constant(gens)
                if sg is not None:
                    print("EXPLICIT_HIT", gens, "semigroup_size", len(sg))
                    print(f"explicit_supports_checked={explicit_checked}")
                    return
    print(f"explicit_supports_checked={explicit_checked}")


if __name__ == "__main__":
    main()
