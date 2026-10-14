"""Per-world realised discoveries by era (development era at discovery), worlds run in parallel."""
import sys, json, statistics as st, importlib
from multiprocessing import Pool
sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
CFG = None
def one_world(args):
    alt, n, seed0 = args
    import gen_data as G, harness as H1, harness2 as H, worlds as W
    W.set_world(alt)
    sc = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/premium_sweep.json'))['4.0']['scale']
    cfg = dict(model='Pmom', routing='spill', spread_floor=0.0, compress=4.0,
               window={'STANDARD': 0.5, 'UNCOMMON': 1.0, 'RARE': 1.0, 'UNIQUE': 1.0}, premium=4.0, scale=sc)
    EO = H.EO; per = {e: [] for e in EO}; tot = []; found = {}
    for s in range(n):
        have, log = H.run(H.P(**cfg), seed0 + s); c = {e: 0 for e in EO}
        for k, (t, d) in have.items(): c[EO[min(int(d), 7)]] += 1
        for e in EO: per[e].append(c[e])
        tot.append(len(have))
        for k in H.IDS: found[k] = found.get(k, 0) + (k in have)
    return str(alt), {e: (round(st.mean(v), 2), round(st.stdev(v) / len(v) ** .5, 2)) for e, v in per.items()}, \
           (round(st.mean(tot), 1), round(st.stdev(tot) / len(tot) ** .5, 2)), {k: v / n for k, v in found.items()}, \
           {k: H.ROWS[k]['era'] for k in H.IDS}, sum(H.TURNS.values())
if __name__ == '__main__':
    import worlds as W
    n_alt = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    jobs = [(None, 30, 3000)] + [(a, n_alt, 3000) for a in W.AXIS]
    with Pool(min(len(jobs), 9)) as pool: res = pool.map(one_world, jobs)
    out = {w: {'per': per, 'total': tot, 'row_p': rp, 'row_era': re_, 'turns': tn} for w, per, tot, rp, re_, tn in res}
    json.dump(out, open('/home/user/Uncharted-Horizons/design/simulator/power/world_baseline.json', 'w'))
    EO = list(out['None']['per'])
    print(f"{'world':10}" + ''.join(f"{e[:8]:>12}" for e in EO) + f"{'total':>14}")
    for w, v in out.items():
        print(f"{('familiar' if w == 'None' else w):10}" + ''.join(f"{v['per'][e][0]:>7.1f}±{v['per'][e][1]:<4.1f}" for e in EO) + f"{v['total'][0]:>8.1f}±{v['total'][1]:<4.1f}")
