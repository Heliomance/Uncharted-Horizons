"""Method balance on the shared clock (absolute game turn of victory), for both benchmark players, 60 games a cell.
Race measure: chance a science player with this method wins before a rival whose victory turn varies like that player's average."""
import json, statistics as st, math, sys
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
PROTO = {}
def absv(g, tag=None): return max(g['cert'], g['built']) + PROTO.get(tag, 9) if g['cert'] and g['built'] else math.inf
W = ('familiar', 'Substance', 'Process'); NAME = {'familiar': 'atomic', 'Substance': 'Substance', 'Process': 'Process'}
MET = {'familiar': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Warp'), 'Substance': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp'), 'Process': ('Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum', 'Warp')}
ARGS = [a.split('=') for a in sys.argv[1:]] or [['expert', 'XF'], ['novice', 'NF']]
PLAYERS = [(a[0], a[1]) for a in ARGS]; PROTO.update({a[1]: int(a[2]) for a in ARGS if len(a) > 2})
def eta2(groups):
    allv = [x for v in groups.values() for x in v]; mu = st.mean(allv)
    return sum(len(v) * (st.mean(v) - mu) ** 2 for v in groups.values()) / sum((x - mu) ** 2 for x in allv)
cells = {}
for lab, tag in PLAYERS:
    for w in W:
        for m in MET[w]: cells[(lab, w, m)] = [absv(g, tag) for g in json.load(open(f'{R}w7f_{w}_{tag}_{m}.json'))]
for lab, tag in PLAYERS:
    allv = [x for (l, w, m), v in cells.items() if l == lab for x in v]; fin = [x for x in allv if x < math.inf]
    print(f"{lab}: victory at a median game turn of {st.median(allv):.0f} (middle half {st.quantiles(fin, n=4)[0]:.0f}–{st.quantiles(fin, n=4)[2]:.0f}), "
          f"spread {st.pstdev(fin):.1f} turns, unwinnable {len(allv) - len(fin)} of {len(allv)}")
    print("   by world: " + ', '.join(f"{NAME[w]} {st.median([x for m in MET[w] for x in cells[(lab, w, m)]]):.0f}" for w in W)
          + f"; method's share of variation within worlds: " + ', '.join(f"{NAME[w]} {eta2({m: [x for x in cells[(lab, w, m)] if x < math.inf] for m in MET[w]}):.0%}" for w in W)
          + f"; methods and worlds together {eta2({(w, m): [x for x in cells[(lab, w, m)] if x < math.inf] for w in W for m in MET[w]}):.0%}")
print(f"\n{'':20}" + ''.join(f"{lab + ' median':>16}{'beats rival':>12}" for lab, _ in PLAYERS))
for w in W:
    for m in MET[w]:
        row = f"{NAME[w]:9} {m:10}"
        for lab, _ in PLAYERS:
            v = cells[(lab, w, m)]; pool = [x for (l, ww, mm), vv in cells.items() if l == lab for x in vv]
            p = sum((x < y) + 0.5 * (x == y) for x in v for y in pool) / (len(v) * len(pool))
            row += f"{st.median(v):>16.0f}{p:>11.0%}{'*' if not .40 <= p <= .60 else ' '}"
        print(row)
print("(* outside 40–60%)")
if len(PLAYERS) >= 2:
    a, b = PLAYERS[0][0], PLAYERS[1][0]
    worse = [(w, m) for w in W for m in MET[w] if st.median(cells[(a, w, m)]) > st.median(cells[(b, w, m)])]
    print(f"\n{a} slower than {b} in {len(worse)} of 15 cells" + (": " + ', '.join(f"{NAME[w]} {m}" for w, m in worse) if worse else ""))
