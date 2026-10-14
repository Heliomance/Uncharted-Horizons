"""Balance across design rounds for every benchmark player, on the shared clock. Current: <tag>_<m>; round 1: <tag>K_<m> in the package's
cells, current elsewhere; round 2: <tag>2_<m> in every cell. Race measure: chance of beating that player's own average rival."""
import json, statistics as st, math
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
W = ('familiar', 'Substance', 'Process'); NAME = {'familiar': 'atomic', 'Substance': 'Substance', 'Process': 'Process'}
MET = {'familiar': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Warp'), 'Substance': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp'), 'Process': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp')}
PKG = {('familiar', 'Wormhole'), ('familiar', 'Warp'), ('familiar', 'Tachyonic'), ('Substance', 'Wormhole'), ('Substance', 'Warp'), ('Substance', 'Plenum'), ('Process', 'Wormhole'), ('Process', 'Warp'), ('Process', 'Plenum')}
PLAYERS = [('expert', 'XF', 9), ('novice', 'NF', 9), ('average', 'AV', 11)]
def absv(g, p): return max(g['cert'], g['built']) + p if g['cert'] and g['built'] else math.inf
def eta2(groups):
    allv = [x for v in groups.values() for x in v]; mu = st.mean(allv)
    return sum(len(v) * (st.mean(v) - mu) ** 2 for v in groups.values()) / sum((x - mu) ** 2 for x in allv)
def race(v, pool): return sum((x < y) + 0.5 * (x == y) for x in v for y in pool) / (len(v) * len(pool))
def load(tag, w, m, p): return [absv(g, p) for g in json.load(open(f'{R}w7f_{w}_{tag}_{m}.json'))]
for lab, tag, p in PLAYERS:
    designs = {'current': {(w, m): load(tag, w, m, p) for w in W for m in MET[w]}}
    designs['round 1'] = {k: (load(tag + 'K', k[0], k[1], p) if k in PKG else v) for k, v in designs['current'].items()}
    designs['round 2'] = {(w, m): load(tag + '2', w, m, p) for w in W for m in MET[w]}
    print(f"\n{lab.upper()}")
    rs2 = None
    for name, cells in designs.items():
        pool = [x for v in cells.values() for x in v]; fin = {k: [x for x in v if x < math.inf] for k, v in cells.items()}
        rs = {k: race(v, pool) for k, v in cells.items()}
        if name == 'round 2': rs2 = rs
        print(f"   {name:8}: median turn {st.median(pool):.0f}, unwinnable {sum(1 for x in pool if x == math.inf):>2}, method's share (worst world) {max(eta2({m: fin[(w, m)] for m in MET[w]}) for w in W):>4.0%}, "
              f"outside 40-60%: {sum(1 for x in rs.values() if not .4 <= x <= .6):>2} of 15, range {min(rs.values()):.0%}-{max(rs.values()):.0%}")
    for w in W: print("      " + NAME[w].ljust(10) + '  '.join(f"{m} {rs2[(w, m)]:.0%}{'*' if not .4 <= rs2[(w, m)] <= .6 else ''}" for m in MET[w]))
