"""Victory turns from benchmark runs, by player and method, for comparing settings.
victory = max(certainty, build complete) + prototype + SS FTL Drive + 1 (delivery and launch), as victory.py computes it: the
prototype priced at 5x the Space era's price (SPACEPRICE), the Drive 4 turns for a good economy (expert, novice) and 5 for the
average player, one turn shorter for Warp, Wormhole and Plenum. Results made under other settings than the defaults need the
run's SPACEPRICE and DEVENDS (empty for today's boundaries) set when tabulating them.

Usage: python3 victory_table.py <world> <label>=<suffix pattern> ...
  each pattern names result files results/w7f_<world><suffix>.json, with {p} for the player code (X, N, A) and {m} for the method,
  e.g.  python3 victory_table.py familiar w16=_cmpPkgQ{p}_{m} fundedwin=_cmpPkgFW{p}_{m}
"""
import sys, os, json, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import victory as V
WORLD = sys.argv[1]; SETS = [a.split('=', 1) for a in sys.argv[2:]]
METHODS = ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling' if WORLD == 'familiar' else 'Plenum']
PLAYERS = [('X', 'expert', 1.0), ('N', 'novice', 1.0), ('A', 'average', 0.8)]   # the player's economy


def victories(path, econ):
    g = json.load(open(path))
    v = [t for t in (V.victory(x, econ) for x in g) if t is not None]
    return v, len(g) - len(v)


for code, player, econ in PLAYERS:
    lines = []
    for label, pat in SETS:
        cells = []; every = []; unfinished = 0
        for m in METHODS:
            path = os.path.join(HERE, 'results', f"w7f_{WORLD}{pat.format(p=code, m=m)}.json")
            if not os.path.exists(path): cells.append('  —'); continue
            v, u = victories(path, econ); every += v; unfinished += u
            cells.append(f"{st.median(v):5.0f}" + (f" ({u} unfinished)" if u else '') if v else '  —')
        if every:
            lines.append(f"  {label:14} median {st.median(every):.0f}, mean {st.mean(every):.1f}, unfinished {unfinished} | " +
                         ', '.join(f"{m} {c.strip()}" for m, c in zip(METHODS, cells)))
    if lines: print(f"{player}:"); print('\n'.join(lines))
