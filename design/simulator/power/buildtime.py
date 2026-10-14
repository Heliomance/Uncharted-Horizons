"""Build-time ledger: the likelihood-weighted cost of a typical city's full building set, fork vs base, per era."""
import sys, re; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import ledger as Lg, ledger2 as L2, ledger3 as L3, ledger4 as L4, ledger6 as L6
CITIES = {'Primitive': 1, 'Ancient': 3, 'Classical': 5, 'Medieval': 6, 'Early Modern': 7, 'Modern': 8, 'Atomic': 8, 'Space': 8}
colcost = {col['columnNumber']: col.get('buildingCost', 0) for col in Lg.TECH}
def base_cost(b): return b['cost'] if 'cost' in b else colcost.get(Lg.tcol.get(b.get('requiredTech'), 0), 0)
def spec_cost(spec):
    m = re.search(r'(?<![\d/\w])(\d{2,4})(?:/\d+)?(?=;|$| )', spec); return int(m.group(1)) if m else 0
def parts(level, price=None, itemise=False, base_level=None):
    """base set cost B, fork canonical cost C, fork-made weighted cost F (price: optional {name: new cost}).
    The Power Plant slot holds one plant at a time: each era adds its best new plant once, as the city's upgrade.
    One city's infrastructure (capital-only, the spaceship stack) counts at 1 ÷ cities; a per-civilisation limit at limit ÷ cities."""
    B = C = F = 0.0; seenb = set(); seenf = set(); items = []; plants = {}
    def era_of(lv): return next((e for e in Lg.EO if Lg.ERA_END[e] >= lv), Lg.EO[-1])
    for b in Lg.B:
        if not L4.buildable(b): continue
        lv = Lg.colcum[Lg.tcol[b['requiredTech']]] if b.get('requiredTech') in Lg.tcol else 0
        if lv <= (level if base_level is None else base_level):
            g = 'NS' if b['name'] in ('Nuclear Plant', 'Solar Plant') else None
            if not g or g not in seenb: B += base_cost(b); seenb.add(g)
        if b['name'] in L3.ungated: flv = 0
        elif b['name'] in L2.assign and L2.assign[b['name']][0] in L2.rows: flv = Lg.ERA_END[L2.rows[L2.assign[b['name']][0]][2]]
        else: continue
        if flv > level: continue
        if L4.GROUP.get(b['name']) == 'Power Plant':
            e = era_of(flv); c = base_cost(b)
            if c > plants.get(e, (0,))[0]: plants[e] = (c, b['name'])
            continue
        g = L4.GROUP.get(b['name'])
        if not g or g not in seenf: C += base_cost(b); seenf.add(g); items.append(('canon', b['name'], base_cost(b)))
    for er, tier, rid, name, ff, pp, mm in L6.orig_newb:
        if Lg.ERA_END[er] > level: continue
        if name in L6.CONVERT and L6.when(L6.CONVERT[name]) is not None and L6.when(L6.CONVERT[name]) <= level: continue
        spec = [s for n, s, a, k in L2.bspecs(L2.rows[rid][3]) if n == name]
        if spec and re.match(r'\s*unit\b', spec[0]): continue            # units are not part of the building set
        sp = spec[0] if spec else ''
        cost = price.get(name, spec_cost(sp)) if price else spec_cost(sp)
        w = 0.1 if rid in L6.RARECHAIN else Lg.LIK[tier]; n = CITIES.get(er, 8)
        if re.search(r'⟨Launch Complex⟩|Spaceship part|\[SS [A-Z]|<in \[Capital\] cities>|Orbital Shipyard', sp + name): w /= n
        lim = re.search(r'Limited to \[(\d+)\] per Civilization', sp)
        if lim: w *= min(1, int(lim.group(1)) / n)
        if L4.GROUP.get(name) == 'Power Plant' or '⟨Power Plant⟩' in sp:
            if cost * w > plants.get(er, (0,))[0]: plants[er] = (cost * w, name)
            continue
        g = L4.GROUP.get(name)
        if g and g in seenf: continue
        seenf.add(g); F += cost * w; items.append(('fork', name, cost * w))
    F += sum(v[0] for v in plants.values()); items += [('plant', v[1], v[0]) for v in plants.values()]
    return (B, C, F, items) if itemise else (B, C, F)
def prod_ratio(level):
    (bf, _, _), (ff, _, _) = L6.ledger(level, 'base'), L6.ledger(level, 'fork'); return ff['Production'] / bf['Production']
if __name__ == '__main__':
    print(f"{'era end':13}{'base set':>10}{'fork canon':>12}{'fork-made':>11}{'set ×':>7}{'Prod ×':>8}{'time ×':>8}   canonical alone: time ×")
    for era in Lg.EO[1:]:
        L = Lg.ERA_END[era]; B, C, F = parts(L); r = prod_ratio(L)
        print(f"{era:13}{B:>10,.0f}{C:>12,.0f}{F:>11,.0f}{(C+F)/B:>7.2f}{r:>8.2f}{(C+F)/B/r:>8.2f}   {C/B/r:>6.2f}")
    print("\nfork-made buildings counted:", len(L6.orig_newb))
