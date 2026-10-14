"""Guaranteed ancestry: is row P certain to be discovered before row K can be? (every OR branch of K's prerequisites leads through P)"""
import re, functools
from defaults import TREE   # the design document, or a run's patched copy; also applies the finalised switches
t = open(TREE, encoding='utf-8').read(); body = t[:t.index('\n## 4.')]
IDRX = r'\b([A-Z]{1,3}-?[A-Z]?\d{1,2}[A-Z]?(?:-W|-V\d+)?|ME-B)\b'
rows = {}
for l in body.split('\n'):
    c = [x.strip() for x in l.split('|')[1:-1]]
    if len(c) >= 7 and re.match(r'^[A-Z][A-Z0-9-]*$', c[0]) and c[1].startswith('**'): rows[c[0]] = c
def terms(pre):
    d = 0; out = []; cur = ''
    for ch in pre:
        d += ch == '('; d -= ch == ')'
        if ch == '+' and d == 0: out.append(cur); cur = ''
        else: cur += ch
    return out + [cur]
@functools.lru_cache(None)
def sure(k):
    """rows certainly discovered before k (every OR branch of its prerequisites leads through them) — the shared parser"""
    import prereq as PQ
    out = set()
    for grp in PQ.parse(rows[k][4], set(rows)):
        per = [set().union(*[{p} | sure(p) for p in o if p != k]) for o in grp]
        if per: out |= set.intersection(*per)
    return frozenset(out)
