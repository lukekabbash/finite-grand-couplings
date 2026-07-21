#!/usr/bin/env python3
"""Construct a small P3 + P3 endomorphism support with two kernel profiles."""

from itertools import combinations, product


N = 6
EDGES = {frozenset(e) for e in ((0, 1), (1, 2), (3, 4), (4, 5))}


def is_endomorphism(f):
    return all(frozenset((f[u], f[v])) in EDGES for u, v in EDGES)


def rank(f):
    return len(set(f))


def profile(f):
    return tuple(sorted((f.count(x) for x in set(f))))


def strongly_connected(gens):
    for source in range(N):
        seen = {source}
        todo = [source]
        while todo:
            u = todo.pop()
            for f in gens:
                v = f[u]
                if v not in seen:
                    seen.add(v)
                    todo.append(v)
        if len(seen) != N:
            return False
    return True


def compose(left, right):
    return tuple(left[right[i]] for i in range(N))


def closure(gens):
    semigroup = set(gens)
    todo = list(gens)
    while todo:
        a = todo.pop()
        for b in tuple(semigroup):
            for c in (compose(a, b), compose(b, a)):
                if c not in semigroup:
                    semigroup.add(c)
                    todo.append(c)
    return semigroup


def shortest_left_words(gens):
    words = {g: (index,) for index, g in enumerate(gens)}
    todo = list(gens)
    while todo:
        current = todo.pop(0)
        for index, g in enumerate(gens):
            nxt = compose(g, current)
            if nxt not in words:
                words[nxt] = words[current] + (index,)
                todo.append(nxt)
    return words


def main():
    endomorphisms = [f for f in product(range(N), repeat=N) if is_endomorphism(f)]
    p24 = [f for f in endomorphisms if rank(f) == 2 and profile(f) == (2, 4)]
    p33 = [f for f in endomorphisms if rank(f) == 2 and profile(f) == (3, 3)]
    print(f"endomorphisms={len(endomorphisms)} profile_24={len(p24)} profile_33={len(p33)}")

    sc_pairs = 0
    for a, b in combinations(endomorphisms, 2):
        if not strongly_connected((a, b)):
            continue
        sc_pairs += 1
        semigroup = closure((a, b))
        profiles = {profile(f) for f in semigroup if rank(f) == 2}
        if {(2, 4), (3, 3)} <= profiles:
            print("HIT support=2", a, b, "semigroup_size", len(semigroup))
            words = shortest_left_words((a, b))
            for wanted in ((2, 4), (3, 3)):
                witness = min(f for f in semigroup if rank(f) == 2 and profile(f) == wanted)
                print("witness", wanted, witness, "word", words[witness])
            return
    print(f"strongly_connected_pairs={sc_pairs}; none has both profiles")

    # Any third endomorphism preserves non-synchronization. Search in tuple
    # order for a reproducible lexicographically minimal support.
    checked = 0
    for a in p24:
        for b in p33:
            for c in endomorphisms:
                checked += 1
                if strongly_connected((a, b, c)):
                    print("HIT support=3", a, b, c)
                    print(f"triples_checked={checked}")
                    return
    print(f"NO_HIT support<=3 triples_checked={checked}")


if __name__ == "__main__":
    main()
