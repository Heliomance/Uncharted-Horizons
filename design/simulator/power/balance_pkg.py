"""Balance before and after an adjustment package, for each benchmark player, on the shared clock (absolute victory turn).
Package cells come from <base tag>K_<method> runs; untouched cells from the current design."""
import json, statistics as st, math
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
W = ('familiar', 'Substance', 'Process'); NAME = {'familiar': 'atomic', 'Substance': 'Substance', 'Process': 'Process'}
MET = {'familiar': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Warp'), 'Substance': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp'), 'Process': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp')}
PKG = {('familiar', 'Wormhole'), ('familiar', 'Warp'), ('familiar', 'Tachyonic'), ('Substance', 'Wormhole'), ('Substance', 'Warp'), ('Substance', 'Plenum'), ('Process', 'Wormhole'), ('Process', 'Warp'), ('Process', 'Plenum')}
PLAYERS = [('expert', 'XF', 9), ('novice', 'NF', 9), ('average', 'AV', 11)]
def absv(g, proto): return max(g['cert'], g['built']) + proto if g['cert'] and g['built'] else math.inf
def eta2(groups):
    allv = [x for v in groups.values() for x in v]; mu = st.mean(allv)
    return sum(len(v) * (st.mean(v) - mu) ** 2 for v in groups.values()) / sum((x - mu) ** 2 for x in allv)
def race(v, pool): return sum((x < y) + 0.5 * (x == y) for x in v for y in pool) / (len(v) * len(pool))
print("Chance of beating an average rival (each player against its own average), before -> after the package; * outside 40-60%")
summary = []
for lab, tag, proto in PLAYERS:
    before = {(w, m): [absv(g, proto) for g in json.load(open(f'{R}w7f_{w}_{tag}_{m}.json'))] for w in W for m in MET[w]}
    after = {k: ([absv(g, proto) for g in json.load(open(f'{R}w7f_{k[0]}_{tag}K_{k[1]}.json'))] if k in PKG else v) for k, v in before.items()}
    pb = [x for v in before.values() for x in v]; pa = [x for v in after.values() for x in v]
    out = [lab]
    for name, cells, pool in (('before', before, pb), ('after', after, pa)):
        fin = {k: [x for x in v if x < math.inf] for k, v in cells.items()}
        rs = {k: race(v, pool) for k, v in cells.items()}
        out.append((st.median(pool), sum(1 for x in pool if x == math.inf), max(eta2({m: fin[(w, m)] for m in MET[w]}) for w in W), sum(1 for p in rs.values() if not .40 <= p <= .60), min(rs.values()), max(rs.values()), rs))
    summary.append(out)
    print(f"\n{lab}: median turn {out[1][0]:.0f} -> {out[2][0]:.0f}; unwinnable {out[1][1]} -> {out[2][1]}; method's share (worst world) {out[1][2]:.0%} -> {out[2][2]:.0%}; "
          f"cells outside 40-60%: {out[1][3]} -> {out[2][3]}; range {out[1][4]:.0%}-{out[1][5]:.0%} -> {out[2][4]:.0%}-{out[2][5]:.0%}")
    for w in W:
        print("   " + NAME[w].ljust(9) + '  '.join(f"{m} {out[1][6][(w, m)]:.0%}{'*' if not .4 <= out[1][6][(w, m)] <= .6 else ''}->{out[2][6][(w, m)]:.0%}{'*' if not .4 <= out[2][6][(w, m)] <= .6 else ''}" for m in MET[w]))
