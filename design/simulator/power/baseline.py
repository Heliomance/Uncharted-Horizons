"""Thinning baseline: realised discoveries per era for every world, and each familiar row's discovery probability."""
import sys, json, statistics as st, importlib; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
def measure(n_fam=30, n_alt=10, out='/home/user/Uncharted-Horizons/design/simulator/power/thin_baseline.json'):
    import gen_data as G; importlib.reload(G)
    import harness as H1; importlib.reload(H1)
    import harness2 as H; importlib.reload(H)
    import worlds as W; importlib.reload(W)
    EO = H.EO
    sc = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/premium_sweep.json'))['4.0']['scale']
    CFG = dict(model='Pmom', routing='spill', spread_floor=0.0, compress=4.0,
               window={'STANDARD': 0.5, 'UNCOMMON': 1.0, 'RARE': 1.0, 'UNIQUE': 1.0}, premium=4.0, scale=sc)
    base = {}; rowp = {}
    for alt in [None] + list(W.AXIS):
        W.set_world(alt); n = n_fam if alt is None else n_alt
        per = {e: [] for e in EO}; tot = []; found = {}
        for s in range(n):
            have, log = H.run(H.P(**CFG), 3000 + s)
            c = {e: 0 for e in EO}
            for k, (t, d) in have.items(): c[EO[min(int(d), 7)]] += 1
            for e in EO: per[e].append(c[e])
            tot.append(len(have))
            if alt is None:
                for k in H.IDS: found[k] = found.get(k, 0) + (k in have)
        base[str(alt)] = {e: round(st.mean(v), 1) for e, v in per.items()}; base[str(alt)]['total'] = round(st.mean(tot), 1)
        if alt is None: rowp = {k: v / n for k, v in found.items()}
    W.set_world(None)
    json.dump({'by_world': base, 'row_p': rowp}, open(out, 'w'), indent=1)
    return base, rowp, H.TURNS
if __name__ == '__main__':
    base, rowp, TURNS = measure()
    EO = list(TURNS)
    print(f"{'world':11}" + ''.join(f"{e[:8]:>9}" for e in EO) + f"{'total':>8}{'per turn':>10}")
    for w, v in base.items():
        print(f"{('familiar' if w == 'None' else w):11}" + ''.join(f"{v[e]:>9}" for e in EO) + f"{v['total']:>8}{v['total'] / sum(TURNS.values()):>10.2f}")
