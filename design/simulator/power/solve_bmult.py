"""§7's building column: per era, the share of a city's Production over the era that its new buildings take,
fork ÷ base, solved to TARGET (the Ancient and Classical eras pooled; the Primitive era takes the pooled value)."""
import sys, json; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import eramodel as EM, ledger as Lg
EO = Lg.EO; TARGET = 1.10
def shares():
    L = EM.loads({e: 1.0 for e in EO})                # (fork new cost, fork era Production, base new cost, base era Production)
    return {e: (fc / fp, bc / bp) for e, (fc, fp, bc, bp) in L.items()}
def solve():
    S = shares(); m = {}
    pooled_f = sum(EM.loads({e: 1.0 for e in EO})[e][0] for e in ('Ancient', 'Classical')) / sum(EM.loads({e: 1.0 for e in EO})[e][1] for e in ('Ancient', 'Classical'))
    pooled_b = sum(EM.loads({e: 1.0 for e in EO})[e][2] for e in ('Ancient', 'Classical')) / sum(EM.loads({e: 1.0 for e in EO})[e][3] for e in ('Ancient', 'Classical'))
    m['Primitive'] = m['Ancient'] = m['Classical'] = TARGET * pooled_b / pooled_f
    for e in EO[3:]:
        fs, bs = S[e]; m[e] = TARGET * bs / fs
    return m, S
if __name__ == '__main__':
    m, S = solve()
    print({e: round(v, 2) for e, v in m.items()})
