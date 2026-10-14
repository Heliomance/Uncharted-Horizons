"""Phase 2: per-world realised discoveries by era, against the familiar world, with standard errors."""
import sys, json, statistics as st, importlib; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
def measure(n=60, out='/home/user/Uncharted-Horizons/design/simulator/power/parity.json'):
    import gen_data as G, harness as H1, harness2 as H, worlds as W
    for m in (G, H1, H, W): importlib.reload(m)
    sc = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/premium_sweep.json'))['4.0']['scale']
    CFG = dict(model='Pmom', routing='spill', spread_floor=0.0, compress=4.0,
               window={'STANDARD': 0.5, 'UNCOMMON': 1.0, 'RARE': 1.0, 'UNIQUE': 1.0}, premium=4.0, scale=sc)
    EO = H.EO; res = {}; rowp = {}
    for alt in [None] + list(W.AXIS):
        W.set_world(alt); per = {e: [] for e in EO}; tot = []; found = {}
        for s in range(n):
            have, log = H.run(H.P(**CFG), 5000 + s)
            c = {e: 0 for e in EO}
            for k, (t, d) in have.items(): c[EO[min(int(d), 7)]] += 1
            for e in EO: per[e].append(c[e])
            tot.append(len(have))
            for k in have: found[k] = found.get(k, 0) + 1
        res[str(alt)] = {'mean': {e: st.mean(v) for e, v in per.items()}, 'se': {e: st.stdev(v) / n ** .5 for e, v in per.items()},
                         'total': st.mean(tot), 'total_se': st.stdev(tot) / n ** .5}
        rowp[str(alt)] = {k: v / n for k, v in found.items()}
    W.set_world(None)
    json.dump({'res': res, 'row_p': rowp}, open(out, 'w'), indent=1)
    return res, EO
if __name__ == '__main__':
    res, EO = measure()
    f = res['None']
    print(f"{'world':10}" + ''.join(f"{e[:8]:>12}" for e in EO) + f"{'total':>13}")
    print(f"{'familiar':10}" + ''.join(f"{f['mean'][e]:>7.1f}±{f['se'][e]:.1f}  " for e in EO) + f"{f['total']:>7.1f}±{f['total_se']:.1f}")
    for w, v in res.items():
        if w == 'None': continue
        print(f"{w:10}" + ''.join(f"{v['mean'][e] - f['mean'][e]:>+12.1f}" for e in EO) + f"{v['total'] - f['total']:>+13.1f}")
