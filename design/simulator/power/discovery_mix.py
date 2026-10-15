"""Where each era's discoveries come from (the era-smoothing pass, 15 Oct 2026): for one benchmark player, per game, the
discoveries made while development is in each era up to the race's finish, by the era of the row discovered, the player's own
and those diffused from rivals (own / diffused). Read from results saved with SAVE_T=1, development as the run had it.
Usage: env <the run's settings> python3 discovery_mix.py <label> <X|N|A> [world:method ...], e.g.
  env $(python3 smooth.py) python3 discovery_mix.py d0 N familiar:Warp Process:Tachyonic Substance:Plenum
"""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import victory as V, gen_data as G

EO = V.EO
label, code = sys.argv[1].lstrip('_'), sys.argv[2]; cells = [c.split(':') for c in sys.argv[3:]]
econ = 0.8 if code == 'A' else 1.0
d, _ = V.clock(econ); start = {e: next(t for t, x in enumerate(d) if x >= i) for i, e in enumerate(EO)}
tab = collections.defaultdict(collections.Counter); turns = collections.Counter(); n = 0
for w, m in cells:
    for g in json.load(open(os.path.join(HERE, 'results', f'w7f_{w}_{label}{code}_{m}.json'))):
        if not (g['cert'] and g['built']): continue
        n += 1; fin = max(g['cert'], g['built']); dif = {k for _, k in (g.get('diffs') or [])}
        for i, e in enumerate(EO):
            lo = start[e]; hi = min(start[EO[i + 1]] if i + 1 < len(EO) else fin, fin)
            if hi <= lo: continue
            turns[e] += hi - lo
            for k, t in g['t'].items():
                if lo < t <= hi: tab[e][(G.ROWS[k]['era'] if k in G.ROWS else '?', 'dif' if k in dif else 'own')] += 1
print(f'{label}{code}: {n} games; per game, discoveries made while development is in each era, by the row\'s era (own / diffused)')
for e in EO:
    c = tab[e]; tot = sum(c.values())
    if not tot: continue
    parts = ', '.join(f"{r} {c[(r, 'own')] / n:.1f}" + (f"/{c[(r, 'dif')] / n:.1f}" if c[(r, 'dif')] else '') for r in EO + ['?'] if c[(r, 'own')] or c[(r, 'dif')])
    print(f"  {e:13} {turns[e] / n:5.1f} turns, {tot / n:5.1f} discoveries ({turns[e] / tot:.2f} turns each): {parts}")
