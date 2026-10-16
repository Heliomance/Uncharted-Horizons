"""How far apart the FTL methods' victories are, for one or more settings (Tamsin, 15 Oct 2026: bring the methods into sync).
For each benchmark player and world: each method's victory median against the world's field (all its methods' games), the
largest and the root-mean-square deviation, and each method's share of races won against the field (a game beats each field
game that finishes later and half of those that tie; 40-60% is balanced). Then the all-15-condition medians against base Civ V's
reference. Reads results/w7f_<world>_cmp<label><X|N|A>_<method>.json (victory needs no SAVE_T).
Usage: python3 ftl_sync.py <label> [<label> ...]   e.g.  python3 ftl_sync.py V125 F2; A+B pools two runs (e.g. two seed sets);
  label@x gives a run's Space price where it differs from the defaults' (e.g. F5+F5b@1.1)
"""
import sys, os, json, statistics as st, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import victory as V

WORLDS = {'familiar': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling'],
          'Process': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum'], 'Substance': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum']}
PLAYERS = [('X', 'expert', 1.0, 305), ('N', 'novice', 1.0, 305), ('A', 'average', 0.8, 380)]
R = os.environ.get('RESULTS') or os.path.join(HERE, 'results')


def wins(mine, field):
    srt = sorted(field); n = len(srt)
    def beat(x):
        import bisect
        lo, hi = bisect.bisect_left(srt, x), bisect.bisect_right(srt, x)
        return (n - hi + 0.5 * (hi - lo)) / n
    return st.mean(beat(x) for x in mine)


def table(label):
    label, _, sp = label.partition('@')   # label@x: the run's Space price, which the prototype's price follows (victory.py)
    V.SPACEPRICE = float(sp) if sp else float(os.environ.get('SPACEPRICE') or 1.0)
    out = {}
    for code, name, econ, ref in PLAYERS:
        allv = []
        for w, ms in WORLDS.items():
            raw = {m: [V.victory(g, econ) for lab in label.split('+') for g in json.load(open(os.path.join(R, f'w7f_{w}_cmp{lab}{code}_{m}.json')))] for m in ms}
            unfinished = sum(x is None for xs in raw.values() for x in xs); games = sum(len(xs) for xs in raw.values())
            v = {m: [x for x in xs if x is not None] for m, xs in raw.items()}
            field = [x for xs in v.values() for x in xs]; fm = st.median(field); allv += field
            dev = {m: st.median(xs) - fm for m, xs in v.items()}
            out[(name, w)] = dict(field=fm, dev=dev, win={m: wins(xs, field) for m, xs in v.items()},
                                  maxdev=max(abs(d) for d in dev.values()), rms=math.sqrt(st.mean(d * d for d in dev.values())), unfinished=unfinished, games=games)
        out[(name, 'all')] = dict(median=st.median(allv), ref=ref)
    return out


def main():
    labels = ['+'.join(x.lstrip('_').removeprefix('cmp') for x in a.split('+')) for a in sys.argv[1:]]
    T = {lab: table(lab) for lab in labels}
    for code, name, econ, ref in PLAYERS:
        print(f'\n=== {name} (all 15 conditions against base Civ V\'s {ref}: ' + ', '.join(f"{lab} {T[lab][(name, 'all')]['median']:.0f} ({T[lab][(name, 'all')]['median'] - ref:+.0f})" for lab in labels) + ')')
        for w, ms in WORLDS.items():
            print(f'  {w}')
            for lab in labels:
                r = T[lab][(name, w)]
                print(f'    {lab:6} field {r["field"]:5.0f} | ' + '  '.join(f'{m[:5]} {r["dev"][m]:+4.0f} ({r["win"][m]:.0%})' for m in ms)
                      + f' | max {r["maxdev"]:3.0f}, rms {r["rms"]:4.1f}')
    print('\n=== summary: mean over worlds and players of the largest deviation (rms)')
    for lab in labels:
        rs = [T[lab][(n, w)] for _, n, _, _ in PLAYERS for w in WORLDS]
        print(f'  {lab:6} largest {st.mean(r["maxdev"] for r in rs):4.1f}, rms {st.mean(r["rms"] for r in rs):4.1f}; win shares {min(min(r["win"].values()) for r in rs):.0%}-{max(max(r["win"].values()) for r in rs):.0%}; '
              f'unfinished {sum(r["unfinished"] for r in rs)} of {sum(r["games"] for r in rs)} games')


if __name__ == '__main__':
    main()
