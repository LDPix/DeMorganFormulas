from typing import List, Tuple, Set, FrozenSet

Node = Tuple[str, object, object]

def _minimize(family):
    fam = list(set(family))
    fam.sort(key=len)
    minimal = set()
    for s in fam:
        if not any(m.issubset(s) for m in minimal):
            minimal.add(s)
    return minimal

def _product_union(A, B):
    return {a | b for a in A for b in B}

def minterms(nodes: List[Node], idx: int) -> Set[FrozenSet[str]]:
    typ, a1, a2 = nodes[idx]
    if typ == "var":
        return {frozenset([a1])}
    elif typ == "and":
        left = minterms(nodes, a1)
        right = minterms(nodes, a2)
        return _minimize(_product_union(left, right))
    elif typ == "or":
        left = minterms(nodes, a1)
        right = minterms(nodes, a2)
        return _minimize(left | right)
    else:
        raise ValueError(f"Unknown type {typ}")

def maxterms(nodes: List[Node], idx: int) -> Set[FrozenSet[str]]:
    typ, a1, a2 = nodes[idx]
    if typ == "var":
        return {frozenset([a1])}
    elif typ == "or":
        left = maxterms(nodes, a1)
        right = maxterms(nodes, a2)
        return _minimize(_product_union(left, right))
    elif typ == "and":
        left = maxterms(nodes, a1)
        right = maxterms(nodes, a2)
        return _minimize(left | right)
    else:
        raise ValueError(f"Unknown type {typ}")

def variables(nodes: List[Node], idx: int) -> Set[str]:
    typ, a1, a2 = nodes[idx]
    if typ == "var":
        return {a1}
    else:
        return variables(nodes, a1) | variables(nodes, a2)

def as_sorted_lists(family):
    return [sorted(s) for s in sorted(family, key=lambda s: (len(s), sorted(s)))]

if __name__ == "__main__":
    # Formula: (a ∧ b) ∨ (c ∧ d ∧ e) ∨ c
    nodes: List[Node] = [
        ("var", "a", None),   # 0
        ("var", "b", None),   # 1
        ("and", 0, 1),        # 2 = a ∧ b
        ("var", "c", None),   # 3
        ("var", "d", None),   # 4
        ("var", "e", None),   # 5
        ("and", 4, 5),        # 6 = d ∧ e
        ("and", 3, 6),        # 7 = c ∧ (d ∧ e)
        ("or", 7, 3),         # 8 = (c ∧ d ∧ e) ∨ c
        ("or", 2, 8),         # 9 = (a ∧ b) ∨ ((c ∧ d ∧ e) ∨ c)
    ]

    root = 9
    M = minterms(nodes, root)
    X = maxterms(nodes, root)

    print("vars =", sorted(variables(nodes, root)))
    print("minterms =", as_sorted_lists(M))
    print("maxterms =", as_sorted_lists(X))
