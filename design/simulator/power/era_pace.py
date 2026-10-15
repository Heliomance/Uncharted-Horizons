"""Turns per discovery in each era (Tamsin, 15 Oct 2026: "show me the average turns per discovery for each age").

The fork: for each benchmark player, the turns its development spends in each era (up to its race's finish) divided by the
breakthroughs it gains meanwhile, of any era: all of them, and its own (without those diffused from rivals). Read from results
saved with SAVE_T=1, development as the defaults (DEVENDS) have it.
Base Civ V: the player who researches only what the spaceship needs (base_race.py), on the same income, over the same
stretches of research: the fork era's span of base Civ V's tech costs (ledger.BASE_END, as the era model maps them), the turns
its research spends there divided by the techs it completes there.
Usage: python3 era_pace.py <label> [world:method ...]   (results/w7f_<world>_<label><X|N|A>_<method>.json; all 15 victory
conditions unless some are named), e.g.
  python3 era_pace.py _cmpPBT
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import victory as V
import base_race as B
import ledger as Lg
from harness import income

EO = Lg.EO
WORLDS = {'familiar': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling'],
          'Process': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum'], 'Substance': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum']}
PLAYERS = [('X', 'expert', 1.0), ('N', 'novice', 1.0), ('A', 'average', 0.8)]


def fork_pace(label, code, econ, cells=None):
    d, _ = V.clock(econ); start = {e: next(t for t, x in enumerate(d) if x >= i) for i, e in enumerate(EO)}
    own, dif, turns = ({e: 0 for e in EO} for _ in range(3))
    for w, ms in WORLDS.items():
        for m in ms:
            if cells and (w, m) not in cells: continue
            for g in json.load(open(os.path.join(HERE, 'results', f'w7f_{w}{label.lstrip("_") and "_" + label.lstrip("_")}{code}_{m}.json'))):
                if not (g['cert'] and g['built']): continue
                fin = max(g['cert'], g['built']); diffused = {k for _, k in (g.get('diffs') or [])}
                for i, e in enumerate(EO):
                    lo = start[e]; hi = min(start[EO[i + 1]] if i + 1 < len(EO) else fin, fin)
                    if hi <= lo: continue
                    got = [k for k, t in g['t'].items() if lo < t <= hi]
                    own[e] += sum(1 for k in got if k not in diffused); dif[e] += sum(1 for k in got if k in diffused); turns[e] += hi - lo
    return {e: (turns[e] / (own[e] + dif[e]) if own[e] + dif[e] else None, turns[e] / own[e] if own[e] else None, turns[e]) for e in EO}


def base_pace(econ):
    r = B.race(B.order(B.BEE), income, econ); cum, t, at = 0.0, 0, {}
    for i, e in enumerate(EO):   # the turn base Civ V's research passes the end of each fork era's span of its tech costs
        while cum < Lg.BASE_END[e] and t < 700: t += 1; cum += income(cum) * econ
        at[e] = t
    out, prev_t, prev_c = {}, 0, 0
    for e in EO:
        n = sum(1 for k, c in r['cum_at'].items() if prev_c < c <= Lg.BASE_END[e])
        end_t = min(at[e], r['research']); out[e] = ((end_t - prev_t) / n if n else None, n); prev_t, prev_c = at[e], Lg.BASE_END[e]
    return out


if __name__ == '__main__':
    label = sys.argv[1]; cells = {tuple(c.split(':')) for c in sys.argv[2:]} or None
    fork = {code: fork_pace(label, code, econ, cells) for code, _, econ in PLAYERS}
    base = {econ: base_pace(econ) for econ in (1.0, 0.8)}
    f = lambda x: '—' if x is None else f'{x:.1f}'
    print('Turns per discovery while development is in each era (all discoveries; own only, without rivals\' knowledge, in brackets),')
    print('the fork to each player\'s race finish; base Civ V, turns per tech over the same stretch of research, on the same income.\n')
    print('| Era | Expert | Novice | Average | Base Civ V, good economy | Base Civ V, average economy |')
    print('|---|---|---|---|---|---|')
    for e in EO:
        cells = [f'{f(fork[c][e][0])} ({f(fork[c][e][1])})' for c, _, _ in PLAYERS]
        print(f"| {e} | {' | '.join(cells)} | {f(base[1.0][e][0])} ({base[1.0][e][1]} techs) | {f(base[0.8][e][0])} |")
