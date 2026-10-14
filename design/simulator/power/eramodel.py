"""Era model: calibrated era lengths, city Production (worked tiles included), and per-era building loads, fork vs base."""
import sys, json; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import ledger as Lg, ledger3 as L3, ledger6 as L6, turnmodel as TM, buildtime as BT
EO = Lg.EO
TILE_PER_CITIZEN = 1.5; CENTRE = 2          # worked-tile Production: assumption
ANCHOR = 320                                # base Civ V science victory: good players by 300, rarely after 375
def science(level, side, pop, cities):
    if not level: return pop + 3 / cities
    f, p, _ = L6.ledger(level, side); return (pop + f['Science'] + 3 / cities) * (1 + p.get('Science', 0) / 100)
def raw_turns(side):
    out = {}; prev = 0; pop0 = 1
    for e in EO:
        lv = Lg.bounds(side)[e]; n = TM.CITIES[e]; pop1 = L3.POP[e]
        sci = (science(prev, side, pop0, n) + science(lv, side, pop1, n)) / 2
        out[e] = (lv - prev) * (1 + (n - 1) * TM.K) / (n * sci); prev, pop0 = lv, pop1
    return out
def ramp_factor(i, r): return 1 + (r - 1) * i / (len(EO) - 1)
def calibrate():
    rb = raw_turns('base'); lo, hi = 1.0, 10.0
    for _ in range(60):
        mid = (lo + hi) / 2; tot = sum(rb[e] / ramp_factor(i, mid) for i, e in enumerate(EO)); lo, hi = (mid, hi) if tot > ANCHOR else (lo, mid)
    return (lo + hi) / 2
R = calibrate()
TURNS = {side: {e: t / ramp_factor(i, R) for i, (e, t) in enumerate(raw_turns(side).items())} for side in ('base', 'fork')}
def city_production(level, side, pop):
    f, p, _ = L6.ledger(level, side); return (CENTRE + pop * TILE_PER_CITIZEN + f['Production']) * (1 + p.get('Production', 0) / 100)
def era_production(e, side):
    i = EO.index(e); bd = Lg.bounds(side); lv0 = bd[EO[i - 1]] if i else 0; p0 = L3.POP[EO[i - 1]] if i else 1
    return (city_production(lv0, side, p0) + city_production(bd[e], side, L3.POP[e])) / 2 * TURNS[side][e]
def loads(bmult, price=None):
    """per era: (fork new-building cost × multiplier, fork era Production, base new-building cost, base era Production)"""
    out = {}; prev = (0, 0, 0)
    for e in EO[1:]:
        B, C, F = BT.parts(Lg.ERA_END[e], price, base_level=Lg.BASE_END[e]); out[e] = (((C - prev[1]) + (F - prev[2])) * bmult[e], era_production(e, 'fork'), B - prev[0], era_production(e, 'base')); prev = (B, C, F)
    return out
def unit_ratio(e): return city_production(Lg.ERA_END[e], 'fork', L3.POP[e]) / city_production(Lg.BASE_END[e], 'base', L3.POP[e])
if __name__ == '__main__':
    print(f"ramp up to ×{R:.2f}; base {sum(TURNS['base'].values()):.0f} turns, fork {sum(TURNS['fork'].values()):.0f}")
    t = 0
    for e in EO: print(f"  {e:13} base enters at turn {t:4.0f}, lasts {TURNS['base'][e]:3.0f}; fork lasts {TURNS['fork'][e]:3.0f}"); t += TURNS['base'][e]
