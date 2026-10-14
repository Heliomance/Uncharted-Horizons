"""Insight-threshold generator, run per civilisation at world creation (design agreed in the previous session)."""
import random, json, sys
sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power'); import gen_data as G, ledger as Lg
EO = Lg.EO
PRICE = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/era_prices.json'))
START = {e: (Lg.ERA_END[EO[i - 1]] if i else 0) for i, e in enumerate(EO)}; END = dict(Lg.ERA_END)
SPAN = {e: END[e] - START[e] for e in EO}
def at(era_i, frac):
    """a point on the total-Insight timeline, given as era index + fraction through that era"""
    era_i = min(max(era_i, 0), len(EO) - 1); e = EO[era_i]; return START[e] + frac * SPAN[e]
def era_coord(x):
    """the inverse: era index + fraction"""
    for i, e in enumerate(EO):
        if x <= END[e]: return i + (x - START[e]) / SPAN[e]
    return len(EO) - 1 + (x - START[EO[-1]]) / SPAN[EO[-1]]
def topo(rows):
    order, seen = [], set()
    def visit(k):
        if k in seen: return
        seen.add(k)
        for grp in rows[k]['pre']:
            for opt in grp:
                for p in opt:
                    if p in rows: visit(p)
        order.append(k)
    for k in sorted(rows): visit(k)
    return order

_DEP = {}
def dependents(rows):
    key = id(rows)
    if key not in _DEP:
        d = {}
        for k, r in rows.items():
            for grp in r['pre']:
                for opt in grp:
                    for p in opt: d.setdefault(p, set()).add(k)
        _DEP[key] = d
    return _DEP[key]
_ANC = {}
def anchors(rows):
    """COREs, plus every non-CORE option in a CORE's prerequisite OR-group that offers no CORE option (and their own such feeders)"""
    key = id(rows)
    if key in _ANC: return _ANC[key]
    out = {k for k, r in rows.items() if r['tier'] == 'CORE'}; changed = True
    while changed:
        changed = False
        for k in list(out):
            for grp in rows[k]['pre']:
                if not any(all(rows.get(p, {}).get('tier') == 'CORE' or p in out for p in opt) for opt in grp):
                    for opt in grp:
                        for p in opt:
                            if p in rows and p not in out: out.add(p); changed = True
    _ANC[key] = out; return out

def generate(rows, spill, rng, gap=0.5, weight=None, slack=0.5):
    weight = weight or (lambda k: 1.0)
    pos = {}
    anchored = anchors(rows)                                            # COREs, and the non-COREs a CORE must wait on
    order = topo(rows); rank = {k: i for i, k in enumerate(order)}
    tail = {}                                                           # room each anchored row must leave for its same-era chain
    for k in reversed(order):
        if k in anchored:
            ds = [d for d in dependents(rows).get(k, ()) if d in anchored and rows[d]['era'] == rows[k]['era']]
            tail[k] = max([gap * PRICE[rows[d]['era']] * weight(d) + tail[d] for d in ds], default=0)
    blocks = {}
    for k in anchored: blocks.setdefault((rows[k]['focus'], rows[k]['era']), []).append(k)
    for (f, e), ks in blocks.items():                                   # 1a. anchored rows: stratified within their era
        ks.sort(key=lambda k: (rank[k], rng.random())); m = len(ks)
        for j, k in enumerate(ks): pos[k] = START[e] + (j + rng.random()) / m * max(SPAN[e] - tail[k], 0.5 * SPAN[e])
    for k, r in rows.items():                                           # 1b. everything else: spread with a symmetric spill
        if k not in anchored:
            u = rng.uniform(-spill, 1 + spill); i = EO.index(r['era'])
            pos[k] = at(i - 1, 1 + u) if u < 0 else at(i + 1, u - 1) if u > 1 else at(i, u)
    events = {'core_out': [], 'far': []}
    for k in order:                                                     # 2. repair, in dependency order
        need = 0
        for grp in rows[k]['pre']:
            opts = [max(pos[p] for p in opt) for opt in grp if all(p in pos for p in opt)]
            if opts: need = max(need, min(opts))
        need += gap * PRICE[rows[k]['era']] * weight(k)
        if pos[k] < need: pos[k] = need
        i = EO.index(rows[k]['era']); c = era_coord(pos[k])             # 3. drift bounds (recorded, never clamped)
        if k in anchored and not (i <= c <= i + 1): events['core_out'].append(k)
        elif not (i - 1 <= c <= i + 2): events['far'].append(k)
    total = {k: pos[k] - slack * SPAN[rows[k]['era']] for k in rows}   # 4. total thresholds
    focus = {}; run = {}
    for k in sorted(rows, key=lambda k: pos[k]):                         # 5. focus thresholds: running weighted price
        f = rows[k]['focus']; run[f] = run.get(f, 0) + PRICE[rows[k]['era']] * weight(k) * G.LIK[rows[k]['tier']]; focus[k] = run[f]
    return pos, total, focus, events
