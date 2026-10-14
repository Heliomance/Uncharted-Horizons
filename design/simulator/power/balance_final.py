"""Final balance confirmation on the full design (round two, pools, rebalance, instrument gate), 60 games a cell, for all three players.
Victory = max(certainty, build) + prototype (5 / 6 turns) + SS FTL Drive (4 / 5, one fewer for Warp, Wormhole, Plenum) + 1 to deliver and launch."""
import json, statistics as st, math
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
W = ('familiar', 'Substance', 'Process'); NAME = {'familiar': 'atomic', 'Substance': 'Substance', 'Process': 'Process'}
MET = {'familiar': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Warp'), 'Substance': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp'), 'Process': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp')}
EXO = {'Warp', 'Wormhole', 'Plenum'}
PLAYERS = [('expert', 'XF3', 5, 4, 'about 295'), ('novice', 'NF3', 5, 4, 'about 295-305'), ('average', 'AV3', 6, 5, 'about 360-375')]
def vic(g, p, d): return max(g['cert'], g['built']) + p + (d - 1 if g['m'] in EXO else d) + 1 if g['cert'] and g['built'] else math.inf
def eta2(groups):
    allv = [x for v in groups.values() for x in v]; mu = st.mean(allv)
    return sum(len(v) * (st.mean(v) - mu) ** 2 for v in groups.values()) / sum((x - mu) ** 2 for x in allv)
def race(v, pool): return sum((x < y) + 0.5 * (x == y) for x in v for y in pool) / (len(v) * len(pool))
for lab, tag, p, d, win in PLAYERS:
    cells = {(w, m): [vic(g, p, d) for g in json.load(open(f'{R}w7f_{w}_{tag}_{m}.json'))] for w in W for m in MET[w]}
    pool = [x for v in cells.values() for x in v]; fin = {k: [x for x in v if x < math.inf] for k, v in cells.items()}
    rs = {k: race(v, pool) for k, v in cells.items()}; out = [k for k, x in rs.items() if not .40 <= x <= .60]
    fp = [x for x in pool if x < math.inf]; qs = st.quantiles(fp, n=4)
    print(f"\n{lab.upper()}: victory median turn {st.median(pool):.0f} (middle half {qs[0]:.0f}-{qs[2]:.0f}; target {win}), unwinnable {len(pool) - len(fp)} of {len(pool)}")
    print(f"   by world: " + ', '.join(f"{NAME[w]} {st.median([x for m in MET[w] for x in cells[(w, m)]]):.0f}" for w in W)
          + f"; method's share of variation: worst world {max(eta2({m: fin[(w, m)] for m in MET[w]}) for w in W):.0%}, all cells {eta2(fin):.0%}")
    print(f"   cells outside 40-60%: {len(out)} of 15" + (" (" + ', '.join(f"{NAME[w]} {m} {rs[(w, m)]:.0%}" for w, m in out) + ")" if out else "") + f"; range {min(rs.values()):.0%}-{max(rs.values()):.0%}")
    for w in W: print(f"      {NAME[w]:10}" + '  '.join(f"{m} {st.median(cells[(w, m)]):.0f} ({rs[(w, m)]:.0%})" for m in MET[w]))
