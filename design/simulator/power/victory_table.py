"""Victory turns from benchmark runs, by player and method, for comparing settings.
victory = max(certainty, build complete) + prototype + SS FTL Drive + 1 (delivery and launch): prototype 5 turns and Drive 4
for a good economy (expert, novice), 6 and 5 for the average player; the Drive one turn shorter for Warp, Wormhole and Plenum.

Usage: python3 victory_table.py <world> <label>=<suffix pattern> ...
  each pattern names result files results/w7f_<world><suffix>.json, with {p} for the player code (X, N, A) and {m} for the method,
  e.g.  python3 victory_table.py familiar w16=_cmpPkgQ{p}_{m} fundedwin=_cmpPkgFW{p}_{m}
"""
import sys, os, json, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = sys.argv[1]; SETS = [a.split('=', 1) for a in sys.argv[2:]]
METHODS = ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling' if WORLD == 'familiar' else 'Plenum']
PLAYERS = [('X', 'expert', 5, 4), ('N', 'novice', 5, 4), ('A', 'average', 6, 5)]
EXOTIC = {'Warp', 'Wormhole', 'Plenum'}


def victories(path, proto, drive):
    g = json.load(open(path))
    v = [max(x['cert'], x['built']) + proto + (drive - 1 if x['m'] in EXOTIC else drive) + 1 for x in g if x['cert'] and x['built']]
    return v, len(g) - len(v)


for code, player, proto, drive in PLAYERS:
    lines = []
    for label, pat in SETS:
        cells = []; every = []; unfinished = 0
        for m in METHODS:
            path = os.path.join(HERE, 'results', f"w7f_{WORLD}{pat.format(p=code, m=m)}.json")
            if not os.path.exists(path): cells.append('  —'); continue
            v, u = victories(path, proto, drive); every += v; unfinished += u
            cells.append(f"{st.median(v):5.0f}" + (f" ({u} unfinished)" if u else '') if v else '  —')
        if every:
            lines.append(f"  {label:14} median {st.median(every):.0f}, mean {st.mean(every):.1f}, unfinished {unfinished} | " +
                         ', '.join(f"{m} {c.strip()}" for m, c in zip(METHODS, cells)))
    if lines: print(f"{player}:"); print('\n'.join(lines))
