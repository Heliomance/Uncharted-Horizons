"""Total victory time with all agreed changes (round-two balance + signature pools), now including the ship:
victory = max(certainty, build complete) + prototype + FTL Drive construction + delivery and launch.
Prototype 9 turns (good economy) / 11 (average); Drive 4 / 5 turns, one fewer where exotic components exist (Warp, Wormhole, Plenum); launch 1."""
import json, statistics as st, math, collections
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
W = ('familiar', 'Substance', 'Process'); NAME = {'familiar': 'atomic', 'Substance': 'Substance', 'Process': 'Process'}
PLAYERS = [('expert', 'TPXq', 9, 4, (285, 320)), ('novice', 'TPNq', 9, 4, (285, 320)), ('average', 'TPAq', 11, 5, (355, 380))]
EXOTIC = {'Warp', 'Wormhole', 'Plenum'}
def vic(g, proto, drive):
    if not (g['cert'] and g['built']): return math.inf
    return max(g['cert'], g['built']) + proto + (drive - 1 if g['m'] in EXOTIC else drive) + 1
def q(v, p): v = sorted(v); x = v[min(len(v) - 1, int(round(p / 100 * (len(v) - 1))))]; return '∞' if x == math.inf else f"{x:.0f}"
print("Total victory turn, all agreed changes plus the ship. Windows: good economy about 295 (well before 320); average player about 360-375.")
for lab, tag, proto, drive, (lo, hi) in PLAYERS:
    gs = [g for w in W for g in json.load(open(f'{R}w7f_{w}_{tag}.json'))]; v = [vic(g, proto, drive) for g in gs]
    fin = [x for x in v if x < math.inf]
    print(f"\n{lab:8} median {q(v, 50)}  middle half {q(v, 25)}-{q(v, 75)}  90th {q(v, 90)}  unwinnable {len(v) - len(fin)} of {len(v)}  | within {lo}-{hi}: {sum(1 for x in fin if lo <= x <= hi) / len(v):.0%}, later than {hi}: {sum(1 for x in v if x > hi) / len(v):.0%}")
    byw = collections.defaultdict(list); bym = collections.defaultdict(list)
    for g, x in zip(gs, v):
        byw[g.get('_w', None)].append(x)
    for w in W:
        vw = [vic(g, proto, drive) for g in json.load(open(f'{R}w7f_{w}_{tag}.json'))]
        ms = collections.defaultdict(list)
        for g in json.load(open(f'{R}w7f_{w}_{tag}.json')): ms[g['m']].append(vic(g, proto, drive))
        print(f"   {NAME[w]:9} median {q(vw, 50)}  | " + ', '.join(f"{m} {q(x, 50)}" for m, x in sorted(ms.items(), key=lambda kv: st.median([y for y in kv[1] if y < math.inf] or [0]))))
