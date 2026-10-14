"""Turn-aligned building column: each fork era's new buildings take TARGET × the share of a city's Production that base
Civ V's buildings arriving over the same turns take of base Production over those turns."""
import sys; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import eramodel as EM, ledger as Lg, ledger3 as L3, buildtime as BT
EO = Lg.EO; TARGET = 1.10
def base_curve():
    """base Civ V: (turn, Insight level, city Production) at each of its era ends, interpolated linearly within an era"""
    pts = [(0.0, 0.0, EM.city_production(0, 'base', 1))]; t = 0.0
    for e in EO:
        t += EM.TURNS['base'][e]; pts.append((t, Lg.BASE_END[e], EM.city_production(Lg.BASE_END[e], 'base', L3.POP[e])))
    return pts
PTS = base_curve()
def base_at(turn):
    for (t0, l0, p0), (t1, l1, p1) in zip(PTS, PTS[1:]):
        if turn <= t1:
            f = (turn - t0) / (t1 - t0) if t1 > t0 else 0; return l0 + f * (l1 - l0), p0 + f * (p1 - p0)
    return PTS[-1][1], PTS[-1][2]
def base_window(t0, t1, steps=40):
    """base new-building cost arriving over turns t0..t1, and base city Production over them"""
    l0, _ = base_at(t0); l1, _ = base_at(t1)
    cost = BT.parts(Lg.ERA_END['Space'], base_level=l1)[0] - BT.parts(Lg.ERA_END['Space'], base_level=l0)[0]
    prod = sum(base_at(t0 + (t1 - t0) * (i + 0.5) / steps)[1] for i in range(steps)) * (t1 - t0) / steps
    return cost, prod
def solve():
    L = EM.loads({e: 1.0 for e in EO}); m = {}; t = 0.0; win = {}
    for e in EO:
        T = EM.TURNS['fork'][e]; win[e] = (t, t + T); t += T
    def ratio(es):
        fc = sum(L[e][0] for e in es); fp = sum(L[e][1] for e in es)
        bc = bp = 0.0
        for e in es: c, p = base_window(*win[e]); bc += c; bp += p
        return TARGET * (bc / bp) / (fc / fp)
    m['Primitive'] = m['Ancient'] = m['Classical'] = ratio(['Ancient', 'Classical'])
    for e in EO[3:]: m[e] = ratio([e])
    return m, win
if __name__ == '__main__':
    m, win = solve(); print({e: round(v, 2) for e, v in m.items()})
