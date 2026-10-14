"""Value-based pricing: value points per building, and each era's canonical price per point."""
import sys, re, statistics, json5; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import ledger as Lg, ledger2 as L2, ledger3 as L3, ledger4 as L4, ledger6 as L6, buildtime as BT
STATS = ('Food', 'Production', 'Gold', 'Science', 'Culture', 'Happiness', 'Faith')
EO = Lg.EO
def era_of_level(lv): return next((e for e in EO if Lg.ERA_END[e] >= lv), EO[-1])
def canon_value(b):
    v = sum(b.get(s.lower(), 0) for s in STATS)
    v += sum(b.get('percentStatBonus', {}).values()) / 10
    v += sum(b.get('specialistSlots', {}).values())
    v += b.get('cityStrength', 0) / 5 + b.get('cityHealth', 0) / 50
    u = [x for x in b.get('uniques', []) if not re.match(r'(Destroyed|Must be|Only available|Cannot be|Unsellable|Can only)', x)]
    ex = L3.extra([re.sub(r'\s*<[^>]*>', '', x) for x in u], 'Modern')
    v += sum(ex.get(s, 0) for s in STATS) + sum(1 for x in u if not any(s in x for s in STATS))
    return v
def spec_value(spec, era):
    plain = re.sub(r'⟨[^⟩]*⟩', '', spec)
    v = sum(int(x) for s in STATS for x in re.findall(rf'(?<![\w\[])\+(\d+) {s}\b', plain))
    v += sum(int(n) for n in re.findall(r'(\w+) ×(\d)', spec) and [n for _, n in re.findall(r'(\w+) ×(\d)', spec)])
    v += sum(int(x) for x in re.findall(r'cityStrength \+(\d+)', spec)) / 5 + sum(int(x) for x in re.findall(r'cityHealth \+(\d+)', spec)) / 50
    us = [u for u in re.findall(r'⟨([^⟩]+)⟩', spec) if not re.match(r'(Must |Only available|Can only|Destroyed|Remove |Unavailable|Power Plant|Launch Complex|Regimen Hall|Caloric Reservoir|Ironworks)', u)]
    for u in us:
        pm = re.search(r'\[([+-]?\d+)\]% \[(\w+)\]', u)
        if pm and pm.group(2) in STATS: v += abs(int(pm.group(1))) / 10; continue
        ex = L3.extra([re.sub(r'\s*<[^>]*>', '', u)], era)
        y = sum(ex.get(s, 0) for s in STATS)
        v += y if y > 0 else 1
    v += len(re.findall(r'Provides \[(\d+)\]', spec))            # a resource is worth a point on top of its unique
    return max(v, 0.5)
def canon_ppp():
    out = {}
    for b in Lg.B:
        if not L4.buildable(b) or b.get('isWonder') or b.get('isNationalWonder'): continue
        lv = Lg.colcum[Lg.tcol[b['requiredTech']]] if b.get('requiredTech') in Lg.tcol else 0
        c = BT.base_cost(b); v = canon_value(b)
        if c and v: out.setdefault(era_of_level(lv), []).append((b['name'], c, v, c / v, b.get('maintenance', 0)))
    return out
if __name__ == '__main__':
    P = canon_ppp()
    print(f"{'era':13}{'n':>3}{'price/point median':>20}{'IQR':>18}{'upkeep per 100 cost':>22}")
    for e in EO:
        if e not in P: continue
        r = sorted(x[3] for x in P[e]); q = statistics.quantiles(r, n=4) if len(r) > 3 else (r[0], r[-1], r[-1])
        up = statistics.median(x[4] / x[1] * 100 for x in P[e])
        print(f"{e:13}{len(r):>3}{statistics.median(r):>20.0f}{f'{q[0]:.0f}–{q[2]:.0f}':>18}{up:>22.2f}")
        print("      ", ', '.join(f"{n} {c}/{v:.1f}" for n, c, v, _, _ in sorted(P[e], key=lambda x: x[3])[:9]))
