"""Base Civ V's science victory, simulated on Unciv's Gods & Kings tech tree with the fork simulator's income (Tamsin, 15 Oct
2026: "run a simulation through the base unciv tech tree to victory, using the same income settings, and see how many turns
that takes").

Research as in Unciv: one tech at a time, all of the turn's science into it, overflow carried over. Each tech costs its listed
cost: the simulator's income is already net of Unciv's 5% a city, and the leader is assumed to research techs no rival knows
yet, so Unciv's discount of up to 30% for techs known by met civilisations does not apply. Two research orders:
  all      every tech but Future Tech, column by column (cheapest first within what is available): a player who researches
           the whole tree, as the era model's calibration assumes;
  beeline  only the prerequisites of the science victory (Rocketry for the Apollo Program, then Satellites, Advanced
           Ballistics, Particle Physics and Nanotechnology for the parts), column by column.
The science victory (VictoryTypes.json): the Apollo Program (750 Production, from Rocketry, cannot be hurried), then six parts
(750 each: the Cockpit from Satellites, three Boosters from Advanced Ballistics, the Engine from Particle Physics, the Stasis
Chamber from Nanotechnology; cannot be bought), each started when its tech and the Apollo Program are done, every part in a city
of its own at the era model's typical base Civ V city Production for the tech progress reached, +50% from a Spaceship Factory
once Robotics is known, and +75% for the last part, built in the Hubble Space Telescope's city once Satellites is known
(section 4's comparison: base Civ V's best city reaches +75%); then a turn to add the last part and launch.
Incomes: the simulator's good economy (income(cum), x1), its average one (x0.8, Production x0.8 too), and, for reference, base
Civ V's own economy from the era model (its calibration puts the whole tree at turn 320).
Usage: python3 base_race.py
"""
import sys, os, math, json5
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ledger as Lg, ledger3 as L3, eramodel as M
from harness import income
G = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'android', 'assets', 'jsons', 'Civ V - Gods & Kings'))
TECHS = json5.load(open(os.path.join(G, 'Techs.json'), encoding='utf-8'))
UNITS = json5.load(open(os.path.join(G, 'Units.json'), encoding='utf-8'))
BUILDINGS = json5.load(open(os.path.join(G, 'Buildings.json'), encoding='utf-8'))
VICTORY = next(v for v in json5.load(open(os.path.join(G, 'VictoryTypes.json'), encoding='utf-8')) if v['name'] == 'Scientific')

COST, COL, PRE = {}, {}, {}
for c in TECHS:
    for t in c['techs']:
        COST[t['name']] = t.get('cost', c['techCost']); COL[t['name']] = c['columnNumber']; PRE[t['name']] = t.get('prerequisites', [])
APOLLO = next(b for b in BUILDINGS if b['name'] == 'Apollo Program')
PARTS = [(p, next(u for u in UNITS if u['name'] == p)) for p in VICTORY['requiredSpaceshipParts']]
NEED = {APOLLO['requiredTech']} | {u['requiredTech'] for _, u in PARTS}


def closure(techs):
    out, stack = set(), list(techs)
    while stack:
        t = stack.pop()
        if t not in out: out.add(t); stack += PRE[t]
    return out


def order(wanted):   # column by column, the cheapest available first; prerequisites always before
    done, seq = set(), []
    while len(seq) < len(wanted):
        ready = [t for t in wanted if t not in done and all(p in done for p in PRE[t])]
        t = min(ready, key=lambda t: (COL[t], COST[t], t)); done.add(t); seq.append(t)
    return seq


base_rate = {}   # base Civ V's own economy (the era model): Insight a turn within each of base's eras, by cumulative tech cost
prev = 0
for e in Lg.EO:
    base_rate[e] = (Lg.BASE_END[e] - prev) / M.TURNS['base'][e]; prev = Lg.BASE_END[e]


def base_income(cum):
    for e in Lg.EO:
        if cum < Lg.BASE_END[e]: return base_rate[e]
    return base_rate[Lg.EO[-1]]


def production(cum, econ):   # a typical base Civ V city's Production for the tech progress reached (the era model)
    lv = min(cum, Lg.BASE_END['Space']); e = next((x for x in Lg.EO if lv <= Lg.BASE_END[x]), Lg.EO[-1])
    return M.city_production(lv, 'base', L3.POP[e]) * econ


def race(seq, inc_fn, econ):
    cum, pool, turn, done, i = 0.0, 0.0, 0, {}, 0
    cum_at = {}
    while i < len(seq):
        turn += 1; inc = inc_fn(cum) * econ; cum += inc; pool += inc
        while i < len(seq) and pool >= COST[seq[i]]:
            pool -= COST[seq[i]]; done[seq[i]] = turn; cum_at[seq[i]] = cum; i += 1
    def build(start, at_cum, bonus=0.0):   # turns to build 750 Production from turn `start`
        return start + math.ceil(750 / (production(at_cum, econ) * (1 + bonus)))
    ap = build(done[APOLLO['requiredTech']], cum_at[APOLLO['requiredTech']])
    last = max((u['requiredTech'] for _, u in PARTS), key=lambda t: done[t])
    def bonus(tech, start):   # the Spaceship Factory (+50%) once Robotics is known; Hubble's city (+25% more) for the last part
        return (0.5 if done.get('Robotics', 10 ** 6) <= start else 0.0) + (0.25 if tech == last and done.get('Satellites', 10 ** 6) <= start else 0.0)
    parts = [build(max(done[u['requiredTech']], ap), cum_at[u['requiredTech']], bonus(u['requiredTech'], max(done[u['requiredTech']], ap))) for _, u in PARTS]
    return dict(research=max(done[t] for t in NEED), last=max(NEED, key=lambda t: done[t]), apollo=ap, victory=max(parts) + 1,
                cost=sum(COST[t] for t in seq), cum=cum, prod=production(cum, econ))


ALL = [t for t in COST if t != 'Future Tech']
BEE = closure(NEED)
print(f"Unciv's Gods & Kings tree: {len(COST)} techs; the science victory needs {', '.join(sorted(NEED))}, whose prerequisites take "
      f"{len(BEE)} techs costing {sum(COST[t] for t in BEE):,} of the {sum(COST[t] for t in ALL):,} without Future Tech")
print(f"  techs left out by the beeline: {', '.join(sorted(set(ALL) - BEE))}")
for label, inc_fn, econ in (("the simulator's good economy", income, 1.0), ("the simulator's average economy", income, 0.8),
                            ("base Civ V's own economy (the era model, calibrated to 320)", base_income, 1.0)):
    print(f"\n{label}:")
    for name, seq in (('whole tree', order(ALL)), ('beeline', order(BEE))):
        r = race(seq, inc_fn, econ)
        print(f"  {name:10} research done turn {r['research']} (last: {r['last']}), Apollo Program built turn {r['apollo']}, "
              f"spaceship complete and launched turn {r['victory']} (a city's Production then {r['prod']:.0f})")
