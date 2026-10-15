"""Victory and era alignment for a smoothing candidate screened by smooth_screen.sh (run with its settings in the environment),
and the discoveries a game holds by the race's finish (the player's own in brackets), with the turns each over the whole game.
Usage: env <settings> python3 smooth_report.py <label> [world:method ...]"""
import sys, os, json, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import victory as V, gen_data as G
EO = V.EO; REF = {'X': 305, 'N': 305, 'A': 380}
ENTRY = {'Ancient': 5, 'Classical': 3, 'Medieval': 3, 'Early Modern': 5, 'Modern': 7, 'Atomic': 6, 'Space': 4}
label = sys.argv[1].lstrip('_'); cells = [c.split(':') for c in sys.argv[2:]]
for code, name, econ in (('X', 'expert', 1.0), ('N', 'novice', 1.0), ('A', 'average', 0.8)):
    d, _ = V.clock(econ); start = {e: next(t for t, x in enumerate(d) if x >= i) for i, e in enumerate(EO)}
    vic, un, gap, fins, tot, own = [], 0, {e: [] for e in ENTRY}, [], [], []
    for w, m in cells:
        for g in json.load(open(os.path.join(HERE, 'results', f'w7f_{w}_{label}{code}_{m}.json'))):
            x = V.victory(g, econ)
            if x is None: un += 1; continue
            vic.append(x); fin = max(g['cert'], g['built']); dif = {k for _, k in (g.get('diffs') or [])}
            got = [k for k, t in (g['t'] or {}).items() if 0 < t <= fin]; fins.append(fin); tot.append(len(got)); own.append(sum(1 for k in got if k not in dif))
            for e, n in ENTRY.items():
                ts = sorted(t for k, t in (g['t'] or {}).items() if k in G.ROWS and EO.index(G.ROWS[k]['era']) >= EO.index(e))
                if len(ts) >= n: gap[e].append(ts[n - 1] - start[e])
    m_ = st.median(vic)
    print(f"  {name:8} victory {m_:.0f} ({m_ - REF[code]:+.0f} against base Civ V's {REF[code]}), unfinished {un}; enters each era by count minus development: "
          + ', '.join(f"{e} {st.median(v):+.0f}" for e, v in gap.items() if v)
          + f"; discoveries a game by the finish {st.mean(tot):.0f} ({st.mean(own):.0f}), {st.mean(fins) / st.mean(tot):.2f} turns each")
