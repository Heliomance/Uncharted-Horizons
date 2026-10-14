"""Phase 3: redraw the fork's era boundaries on the Insight curve for an even pace, the good player's game matching base's.
Base keeps its own boundaries (its calibration); only the fork's move. A fork era's Science per turn depends on which
buildings it has — set by the era of their row — not on where its boundaries sit, so its length is proportional to its span."""
import sys, json, statistics as st, importlib; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import ledger as Lg, eramodel as EM, gen_data as G
EO = Lg.EO
OLD_END = dict(Lg.ERA_END)
OLD_SPAN = {e: OLD_END[e] - (OLD_END[EO[i - 1]] if i else 0) for i, e in enumerate(EO)}
RAW_F = EM.raw_turns('fork')                                   # unramped fork turns at the old spans
FACTOR = {e: RAW_F[e] / OLD_SPAN[e] for e in EO}               # turns per Insight, before the residual ramp
R_GOOD = EM.R                                                  # base calibrated to 320 on its own boundaries
EXPECTED = {e: sum(G.LIK[r['tier']] for r in G.familiar.values() if r['era'] == e) for e in EO}
def fork_turns(span, R=R_GOOD): return {e: span[e] * FACTOR[e] / EM.ramp_factor(i, R) for i, e in enumerate(EO)}
def span_for(turns, R=R_GOOD): return {e: turns[e] * EM.ramp_factor(i, R) / FACTOR[e] for i, e in enumerate(EO)}
def apply(span):
    import harness as H1, harness2 as H2
    end = {}; c = 0
    for e in EO: c += span[e]; end[e] = round(c)
    Lg.ERA_END.clear(); Lg.ERA_END.update(end)
    T = fork_turns(span); price = {e: span[e] / EXPECTED[e] for e in EO}
    start = {e: (end[EO[i - 1]] if i else 0) for i, e in enumerate(EO)}
    rate = {e: (end[e] - start[e]) / T[e] for e in EO}
    for m in (H1, H2):
        for name, val in (('TURNS', T), ('PRICE', price), ('START', start), ('RATE', rate)):
            if hasattr(m, name): getattr(m, name).clear(); getattr(m, name).update(val)
    return end, T, price
def measure(n=20, seed0=3000):
    import harness2 as H
    sc = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/premium_sweep.json'))['4.0']['scale']
    cfg = dict(model='Pmom', routing='spill', spread_floor=0.0, compress=4.0,
               window={'STANDARD': 0.5, 'UNCOMMON': 1.0, 'RARE': 1.0, 'UNIQUE': 1.0}, premium=4.0, scale=sc)
    per = {e: [] for e in EO}; tot = []
    for s in range(n):
        have, log = H.run(H.P(**cfg), seed0 + s); c = {e: 0 for e in EO}
        for k, (t, d) in have.items(): c[EO[min(int(d), 7)]] += 1
        for e in EO: per[e].append(c[e])
        tot.append(len(have))
    return {e: st.mean(v) for e, v in per.items()}, st.mean(tot)
if __name__ == '__main__':
    import worlds as W; W.set_world(None)
    GAME = 320
    span = dict(OLD_SPAN); hist = []
    real, total = measure(); T = fork_turns(span)
    print(f"start: {total:.0f} discoveries over {sum(T.values()):.0f} turns (pace {total / sum(T.values()):.2f})")
    for it in range(4):
        pace = total / GAME
        target = {e: real[e] / pace for e in EO}
        span = span_for(target); end, T, price = apply(span)
        real, total = measure()
        p = {e: real[e] / T[e] for e in EO}
        print(f"iteration {it + 1}: {total:.0f} over {sum(T.values()):.0f} turns; pace by era " + ' '.join(f"{e[:3]} {p[e]:.2f}" for e in EO))
        hist.append(dict(span=span, end=end, turns=T, price=price, real=real, total=total))
    json.dump(hist, open('/home/user/Uncharted-Horizons/design/simulator/power/redraw_iterations.json', 'w'), indent=1)
