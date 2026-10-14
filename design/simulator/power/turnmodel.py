"""Turn model: era lengths from the ledger's typical city, the Food surplus that growth implies, and Space-era build capacity."""
import sys, math, json; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import ledger as Lg, ledger3 as L3, ledger6 as L6, buildtime as BT
EO = Lg.EO
CITIES = {'Primitive': 1, 'Ancient': 3, 'Classical': 5, 'Medieval': 6, 'Early Modern': 7, 'Modern': 8, 'Atomic': 8, 'Space': 8}   # assumption
K = 0.05                                    # per-city threshold modifier: Civ V's standard-map value, unverified for Unciv
def box(p): return 15 + 8 * (p - 1) + math.floor((p - 1) ** 1.5)
def carry(side, e):                         # Aqueduct from the Classical era, Medical Lab from the Modern (base) or Atomic (Germ fork)
    i = EO.index(e); c = 0.4 if i >= EO.index('Classical') else 0
    return c + (0.25 if i >= EO.index('Modern' if side == 'base' else 'Atomic') else 0)
def per_city(level, side, stat):
    f, p, m = L6.ledger(level, side); return f[stat] * (1 + p.get(stat, 0) / 100), f, p
def era_table(side):
    out = {}; prev_lv = 0; prev_pop = 1
    for e in EO:
        lv = Lg.bounds(side)[e]; E = lv - prev_lv
        pop0, pop1 = prev_pop, L3.POP[e]
        s0 = per_city(prev_lv, side, 'Science')[0] if prev_lv else 0; s1 = per_city(lv, side, 'Science')[0]
        sci = ((pop0 + pop1) / 2 + (s0 + s1) / 2)          # 1 Science per citizen, plus buildings
        need = E * (1 + (CITIES[e] - 1) * K)
        turns = need / (CITIES[e] * sci)
        food = sum(box(p) for p in range(pop0, pop1)) * (1 - carry(side, e))
        out[e] = dict(turns=turns, sci=sci, surplus=food / turns if turns else 0, E=E)
        prev_lv, prev_pop = lv, pop1
    return out
if __name__ == '__main__':
    B, F = era_table('base'), era_table('fork')
    S = {'Primitive': 2, 'Ancient': 3, 'Classical': 3, 'Medieval': 4, 'Early Modern': 5, 'Modern': 6, 'Atomic': 7, 'Space': 8}
    print(f"{'era':13}{'Insight':>9}{'Sci/city base':>14}{'fork':>7}{'turns base':>12}{'fork':>7}{'implied surplus base':>22}{'fork':>7}{'assumed in 3b':>15}")
    tb = tf = 0
    for e in EO:
        b, f = B[e], F[e]; tb += b['turns']; tf += f['turns']
        print(f"{e:13}{b['E']:>9,}{b['sci']:>14.1f}{f['sci']:>7.1f}{b['turns']:>12.0f}{f['turns']:>7.0f}{b['surplus']:>22.1f}{f['surplus']:>7.1f}{S[e]:>15}")
    print(f"{'total':13}{'':>9}{'':>14}{'':>7}{tb:>12.0f}{tf:>7.0f}")
    json.dump({'base': B, 'fork': F}, open('/home/user/Uncharted-Horizons/design/simulator/power/turnmodel.json', 'w'))
