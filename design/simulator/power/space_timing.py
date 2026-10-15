"""When development reaches the Space era, against the science race (Tamsin, 15 Oct 2026: "the development thresholds
aren't set right if the game is reliably ending before the space era even begins").

Development (section 2) is cumulative Insight laid on the era spans. In the simulator it depends on the turn alone for a
given economy, since by default no Insight is withheld from it. For each player, pooled over the victory conditions given,
from results saved with SAVE_T=1 and ACCT=<path>:
  the median turn of the first Space-era discovery, the unified theory, the civilisation's entry to the Space era (its
  fourth Space-era breakthrough), certainty, the build and victory, with the development reached at each;
  for every era, the median turn a civilisation enters it by section 2's count against the turn its development does;
  the share of its Space-era breakthroughs each player holds before its development reaches the Space era;
  the share of the Insight spent studying each era's rows that the ahead-of-time premium takes (Grand Endeavours are
  priced separately and not included);
  discoveries a turn (diffusion included) while development is in each of the last three eras.
Usage: [SPACEFROM=<Insight>] python3 space_timing.py <label> world:method ...   (SPACEFROM as the runs had it; reads
results/w7f_<world>_<label><X|N|A>_<method>.json and results/acct_<label><X|N|A>_<world>_<method>.json), e.g.
  python3 space_timing.py _dev familiar:Warp Process:Tachyonic Substance:Plenum
"""
import sys, os, json, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen_data as G
from harness import income, EO
import harness_ftl_e as HF
HF.SPACE_FROM = float(os.environ['SPACEFROM']) if os.environ.get('SPACEFROM') else None   # as the runs had it (harness_ftl_e.SPACE_FROM)

PLAYERS = [('X', 'expert', 1.0, 5, 4), ('N', 'novice', 1.0, 5, 4), ('A', 'average', 0.8, 6, 5)]   # economy, prototype, Drive
EXOTIC = {'Warp', 'Wormhole', 'Plenum'}
SPACE = EO.index('Space')
ENTRY = {'Ancient': 5, 'Classical': 3, 'Medieval': 3, 'Early Modern': 5, 'Modern': 7, 'Atomic': 6, 'Space': 4}   # section 2's era entry
NAMES = dict(space='first Space-era discovery', close='unified theory', entry='enters the Space era (4th Space-era breakthrough)',
             cert='certainty', built='build complete', finish='race finished', victory='victory')


def clock(econ, turns=700):   # development at the end of each turn, as the harness accumulates it
    cum, d = 0.0, [0.0]
    for _ in range(turns):
        cum += income(cum) * econ; d.append(HF.dev_at(cum))
    return d


def reach(d, level): return next(t for t, x in enumerate(d) if x >= level)


def med(v): return st.median(v) if v else float('nan')


def era(k): return EO.index(G.ROWS[k]['era']) if k in G.ROWS else 0


label, cells = sys.argv[1].lstrip('_'), [c.split(':') for c in sys.argv[2:]]
for code, name, econ, proto, drive in PLAYERS:
    d = clock(econ); start = {e: reach(d, i) for i, e in enumerate(EO)}; t_space = start['Space']
    rows = {k: [] for k in NAMES}; entry = {e: [] for e in ENTRY}; early, unfinished, n = [], 0, 0
    att, prem, pace = {}, {}, {e: [0, 0] for e in EO[SPACE - 2:]}
    for w, m in cells:
        games = json.load(open(os.path.join(HERE, 'results', f'w7f_{w}_{label}{code}_{m}.json')))
        accts = json.load(open(os.path.join(HERE, 'results', f'acct_{label}{code}_{w}_{m}.json')))
        for g, a in zip(games, accts):
            n += 1
            for e, x in a.get('att_era', {}).items(): att[e] = att.get(e, 0.0) + x
            for e, x in a.get('prem_era', {}).items(): prem[e] = prem.get(e, 0.0) + x
            if not (g['cert'] and g['built']): unfinished += 1; continue
            fin = max(g['cert'], g['built'])
            sp = sorted(t for k, t in g['t'].items() if era(k) >= SPACE and t <= fin)
            vals = dict(space=g['space'], close=g['close'], entry=sp[3] if len(sp) > 3 else None, cert=g['cert'], built=g['built'],
                        finish=fin, victory=fin + proto + (drive - 1 if g['m'] in EXOTIC else drive) + 1)
            for k, v in vals.items():
                if v is not None: rows[k].append(v)
            early.append(sum(1 for t in sp if t < t_space) / len(sp) if sp else 0.0)
            for e, need in ENTRY.items():
                ts = sorted(t for k, t in g['t'].items() if era(k) >= EO.index(e))
                if len(ts) >= need: entry[e].append(ts[need - 1])
            for e in pace:   # discoveries while development is in era e, up to the finish
                lo = start[e]; hi = min(start[EO[EO.index(e) + 1]] if EO.index(e) + 1 < len(EO) else fin, fin)
                pace[e][0] += sum(1 for t in g['t'].values() if lo < t <= hi); pace[e][1] += max(hi - lo, 0)
    print(f'\n{name.upper()} ({n} games, {unfinished} unfinished; economy x{econ}): development enters the Atomic era on turn '
          f"{start['Atomic']}, the Space era on {t_space}, and ends it on {reach(d, SPACE + 1)}")
    for k, v in rows.items():
        m_ = med(v); print(f'  {NAMES[k]:51} turn {m_:5.0f}   development {d[min(int(round(m_)), len(d) - 1)]:.2f}')
    print('  enters each era by count / development reaches it: ' + ', '.join(f'{e} {med(v):.0f}/{start[e]}' for e, v in entry.items()))
    print(f'  Space-era breakthroughs held at the finish that came before development reached the Space era: {100 * med(early):.0f}% (median)')
    print('  the premium\'s share of the Insight spent on study, by era of the row: ' +
          ', '.join(f'{e} {100 * prem.get(e, 0) / att[e]:.0f}%' for e in EO if att.get(e, 0) > 0 and EO.index(e) >= SPACE - 2))
    print('  discoveries a turn while development is in each era (diffusion included): ' +
          ', '.join(f'{e} {a / b:.2f}' for e, (a, b) in pace.items() if b))
