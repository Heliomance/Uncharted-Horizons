"""Parity confirmation for a design version (CLAUDE.md's check): each benchmark player's science victory on all 15 victory
conditions against base Civ V's on the same income (base_race.py: 305 on a good economy, 380 on an average one), with the
games that never finished, the prototype's and the Drive's turns, the late pace (discoveries from the turn development
enters the Modern era to the race's finish, rivals' knowledge included) and Competing Solutions' lock-outs.
Reads results/w7f_<world>_cmp<label><X|N|A>_<method>.json as compare_settings.sh writes them; the pace needs SAVE_T=1.
Set RESULTS to read the files from another folder (e.g. a full copy kept outside the repository).
Usage: python3 confirm_report.py <label>   e.g.  python3 confirm_report.py V124"""
import sys, os, json, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import victory as V, competing

REF = {'X': 305, 'N': 305, 'A': 380}
WORLDS = {'familiar': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling'],
          'Process': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum'], 'Substance': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum']}
PLAYERS = [('X', 'expert', 1.0), ('N', 'novice', 1.0), ('A', 'average', 0.8)]
PRIMARY = {a: p for p, a, _ in competing.groups()}
label = sys.argv[1]; R = os.environ.get('RESULTS') or os.path.join(HERE, 'results')


def q(v, p):
    v = sorted(v); return v[min(len(v) - 1, int(round(p / 100 * (len(v) - 1))))]


def game(g, econ, modern):
    """victory, prototype turns, Drive turns, (discoveries, turns) from the Modern era to the finish, lock-outs (all; Modern on)"""
    v = V.victory(g, econ)
    if v is None: return None
    fin = max(g['cert'], g['built']); pt = V.prototype_turns(fin, econ); dt = V.drive_turns(fin + pt, econ, g['m'] in V.EXOTIC)
    t = g.get('t') or {}
    pace = (sum(1 for x in t.values() if modern < x <= fin), fin - modern) if t else None
    lk = g.get('locked') or []
    return v, pt, dt, pace, (len(lk), sum(1 for a in lk if t.get(PRIMARY.get(a), 0) > modern))


every = {c: [] for c, _, _ in PLAYERS}; unfinished = {c: 0 for c, _, _ in PLAYERS}
for w, methods in WORLDS.items():
    print(f'== {w}')
    for code, name, econ in PLAYERS:
        d, _ = V.clock(econ); modern = next(i for i, x in enumerate(d) if x >= V.EO.index('Modern'))
        res, per, un = [], {}, 0
        for m in methods:
            gs = json.load(open(os.path.join(R, f'w7f_{w}_cmp{label}{code}_{m}.json')))
            rs = [game(g, econ, modern) for g in gs]; un += sum(1 for r in rs if r is None); rs = [r for r in rs if r]
            per[m] = st.median(r[0] for r in rs) if rs else None; res += rs
        every[code] += res; unfinished[code] += un
        vic = [r[0] for r in res]; pace = [r[3] for r in res if r[3]]
        line = f'  {name:8} median {st.median(vic):.0f}, mean {st.mean(vic):.1f}, unfinished {un} | ' + ', '.join(f'{m} {x:.0f}' for m, x in per.items() if x)
        if pace: line += f' | from the Modern era: {st.mean(p[0] for p in pace):.0f} discoveries in {st.mean(p[1] for p in pace):.0f} turns'
        print(line)
print('\n== all 15 conditions')
for code, name, econ in PLAYERS:
    res = every[code]; vic = [r[0] for r in res]; m_ = st.median(vic); pace = [r[3] for r in res if r[3]]
    line = (f'{name:8} {len(res) + unfinished[code]} games, {unfinished[code]} unfinished: victory median {m_:.0f} ({m_ - REF[code]:+.0f} against '
            f'{REF[code]}), middle half {q(vic, 25):.0f}-{q(vic, 75):.0f}, mean {st.mean(vic):.1f}; prototype {st.median(r[1] for r in res):.0f} turns, '
            f'Drive {st.median(r[2] for r in res):.0f}')
    if pace:
        n_, t_ = st.mean(p[0] for p in pace), st.mean(p[1] for p in pace)
        line += f'; from the Modern era {n_:.0f} discoveries in {t_:.0f} turns ({n_ / t_:.2f} a turn)'
    lk = [r[4] for r in res]
    if any(x[0] for x in lk): line += f'; lock-outs a game {st.mean(x[0] for x in lk):.1f} ({st.mean(x[1] for x in lk):.1f} from the Modern era)'
    print(line)
