#!/usr/bin/env python3
"""Exact certificate for a negative answer to Grimmett--Holmes Q3.11."""

from fractions import Fraction


if not __debug__:
    raise RuntimeError("verification requires assertions; rerun Python without -O")


N = 6
A = (0, 1, 0, 0, 1, 0)
C = (3, 4, 5, 1, 2, 1)
GENERATORS = (A, C)
WEIGHTS = (Fraction(1, 2), Fraction(1, 2))
EDGES = {frozenset(edge) for edge in ((0, 1), (1, 2), (3, 4), (4, 5))}


def compose(left, right):
    """left o right, so prefix (F1,...,Ft) is Ft o ... o F1."""
    return tuple(left[right[i]] for i in range(N))


def kernel(f):
    classes = {}
    for source, target in enumerate(f):
        classes.setdefault(target, []).append(source)
    return tuple(sorted((tuple(block) for block in classes.values()), key=lambda b: b[0]))


def profile(f):
    return tuple(sorted(map(len, kernel(f))))


def rank(f):
    return len(set(f))


def is_endomorphism(f):
    return all(frozenset((f[u], f[v])) in EDGES for u, v in EDGES)


def semigroup_closure(generators):
    semigroup = set(generators)
    todo = list(generators)
    while todo:
        left = todo.pop()
        for right in tuple(semigroup):
            for product in (compose(left, right), compose(right, left)):
                if product not in semigroup:
                    semigroup.add(product)
                    todo.append(product)
    return semigroup


def transition_matrix():
    matrix = [[Fraction(0) for _ in range(N)] for _ in range(N)]
    for f, weight in zip(GENERATORS, WEIGHTS):
        for i in range(N):
            matrix[i][f[i]] += weight
    return matrix


def reachable(adjacency, source):
    seen = {source}
    todo = [source]
    while todo:
        u = todo.pop()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return seen


def main():
    assert sum(WEIGHTS) == 1 and all(weight > 0 for weight in WEIGHTS)
    assert all(is_endomorphism(f) for f in GENERATORS)

    matrix = transition_matrix()
    assert all(sum(row) == 1 for row in matrix)
    adjacency = [{j for j, value in enumerate(row) if value} for row in matrix]
    assert all(len(reachable(adjacency, i)) == N for i in range(N))

    semigroup = semigroup_closure(GENERATORS)
    assert len(semigroup) == 21
    assert all(is_endomorphism(f) for f in semigroup)
    assert min(map(rank, semigroup)) == 2

    balanced = compose(A, C)  # F1=C, F2=A
    assert balanced == (0, 1, 0, 1, 0, 1)
    assert kernel(A) == ((0, 2, 3, 5), (1, 4))
    assert profile(A) == (2, 4)
    assert kernel(balanced) == ((0, 2, 4), (1, 3, 5))
    assert profile(balanced) == (3, 3)

    # Once a prefix has rank two, every subsequent supported map sends its
    # two-point image edge to another edge. Therefore the kernel can never
    # grow again. This directly checks that invariant for the entire closure.
    rank_two = [f for f in semigroup if rank(f) == 2]
    assert rank_two
    for current in rank_two:
        for future in semigroup:
            continued = compose(future, current)
            assert rank(continued) == 2
            assert kernel(continued) == kernel(current)

    # A appears eventually almost surely under iid fair draws. At its first
    # appearance A o current has rank two, so k(mu)=2 almost surely.
    for current in semigroup | {tuple(range(N))}:
        assert rank(compose(A, current)) == 2

    print("grand-coupling counterexample: PASS")
    print("support_size=2 weights=1/2,1/2 semigroup_size=21 min_rank=2")
    print("P irreducible: PASS")
    print("prefix A: probability 1/2, terminal profile (2,4)")
    print("prefix C,A: probability 1/4, terminal profile (3,3)")


if __name__ == "__main__":
    main()
