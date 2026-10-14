"""Method balance under the standard player (smarter either-or choices, parallel engineering), 60 games a cell.
Race measure: chance of finishing before a rival whose finishing time varies like the design's average science player (50% neutral)."""
import json, statistics as st, collections
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
def vic(g): return max(g['cert'], g['built']) + 9 - g['space'] if g['cert'] and g['built'] else None
W = ('familiar', 'Substance', 'Process'); NAME = {'familiar': 'atomic', 'Substance': 'Substance', 'Process': 'Process'}
MET = {'familiar': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Warp'), 'Substance': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp'), 'Process': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp')}
def load(w, m, tag): return [x for x in map(vic, json.load(open(f'{R}w7f_{w}_{tag}.json'))) if x is not None], len(json.load(open(f'{R}w7f_{w}_{tag}.json')))
def eta2(groups):
    allv = [x for v in groups.values() for x in v]; mu = st.mean(allv)
    return sum(len(v) * (st.mean(v) - mu) ** 2 for v in groups.values()) / sum((x - mu) ** 2 for x in allv)
def report(title, choose):
    cells = {(w, m): load(w, m, choose(w, m)) for w in W for m in MET[w]}
    pool = [x for (v, n) in cells.values() for x in v]; fails = sum(n - len(v) for v, n in cells.values())
    print(f"\n== {title}: median {st.median(pool):.0f}, middle half {st.quantiles(pool, n=4)[0]:.0f}–{st.quantiles(pool, n=4)[2]:.0f}, spread (SD) {st.pstdev(pool):.1f}, cannot win {fails} of {sum(n for v, n in cells.values())}")
    print("   method's share of variation: " + ', '.join(f"{NAME[w]} {eta2({m: cells[(w, m)][0] for m in MET[w]}):.0%}" for w in W) + f", all {eta2({k: v for k, (v, n) in cells.items()}):.0%}")
    out = {}
    for (w, m), (v, n) in sorted(cells.items(), key=lambda kv: st.mean(kv[1][0])):
        p = sum((x < y) + 0.5 * (x == y) for x in v for y in pool) / (len(v) * len(pool)); out[(w, m)] = p
        flag = '' if 0.40 <= p <= 0.60 else '  <- outside 40–60%'
        print(f"   {NAME[w]:9} {m:11} median {st.median(v):>4.0f}  mean {st.mean(v):>5.1f} ± {st.pstdev(v) / len(v) ** 0.5:.1f}   beats an average rival {p:>4.0%}{flag}")
    return out
report("Current design (Wormhole row at 2.5x)", lambda w, m: f'P_{m}')
ADJ = {('Warp',): 'P_Warp_gx', ('Wormhole',): 'P_Wormhole_4x'}
report("Adjusted design (Warp both trims; Wormhole row at 4x; atomic Tachyonic without NP11)",
       lambda w, m: 'P_Warp_gx' if m == 'Warp' else 'P_Wormhole_4x' if m == 'Wormhole' else ('P_Tachyonic_ny' if (m, w) == ('Tachyonic', 'familiar') else f'P_{m}'))
