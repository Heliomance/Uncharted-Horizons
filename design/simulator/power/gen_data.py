"""Row data for the threshold generator: focus, tier, era, prerequisite structure, world."""
import re, functools, sys
sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power'); import reach as R, ledger as Lg
EO = Lg.EO + (['Interstellar'] if 'Interstellar' not in Lg.EO else [])
t = R.t; lines = t[:t.index('\n## 4.')].split('\n')
FOCUS = {}; cur = None
for l in lines:
    m = re.match(r'^#{2,4} FOCUS: ([A-Z][A-Z &\'-]+?)\s*(?:\S+)?\s*$', l)
    if m: cur = m.group(1).strip().title()
    mm = re.match(r'^\| ([A-Z][A-Z0-9-]*) \| \*\*', l)
    if mm and cur: FOCUS[mm.group(1)] = cur
@functools.lru_cache(None)
def world(k, seen=()):
    c = R.rows[k]
    if k.startswith('QM-E'): return 'Elemental'
    m = re.search(r'Only in ([A-Z][a-z]+) worlds|([A-Z][a-z]+) worlds only|\*([A-Z][a-z]+) only\.?\*|\*\*([A-Z][a-z]+)-exclusive', c[5])
    if m: return m.group(1) or m.group(2) or m.group(3) or m.group(4)
    v = re.search(r'\(([A-Z][a-z]+)(?:-Elemental| Theory)? validated\)', c[4])
    if v: return v.group(1)
    for tm in R.terms(c[4]):
        if re.search(r'\bor\b', tm): continue
        for p in re.findall(R.IDRX, tm):
            if p in R.rows and p not in seen and (w := world(p, seen + (k,))): return w
    return None
def prereq_groups(k):
    """a list of AND-terms, each a list of OR-options (ids in the tree) — the shared parser (prereq.py)"""
    import prereq as PQ
    return [[[p for p in opt if p != k] for opt in grp if [p for p in opt if p != k]] for grp in PQ.parse(R.rows[k][4], set(R.rows))]
LIK = {'CORE': 1.0, 'STANDARD': 0.85, 'UNCOMMON': 0.4, 'RARE': 0.1, 'UNIQUE': 0.065}
FAMILIAR = {'Germ', 'Atomic'}   # the familiar world's values on the axes whose familiar branch is tagged
ROWS = {k: dict(id=k, focus=FOCUS.get(k, '?'), tier=c[2], era=c[3], pre=prereq_groups(k), world=world(k))
        for k, c in R.rows.items() if c[3] in EO}
familiar = {k: r for k, r in ROWS.items() if r['world'] in (None,) or r['world'] in FAMILIAR}
