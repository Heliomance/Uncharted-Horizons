"""A benchmark game's victory turn, for the tools that report one (victory_table.py, space_timing.py).

victory = the race's finish (certainty and the build both done) + the prototype + the SS FTL Drive + 1 turn to deliver and
launch. The prototype is a Grand Endeavour (section 4) priced at PROTOX (default 5) x the Space era's price per discovery
(SPACEPRICE, as the run had it) x the model's calibration, with the ahead-of-time premium at the finish, when it is committed.
It is paid from the active focus's share (80%) of the Insight a turn then, so it lengthens as Space-era research grows dearer:
4 turns at x0.8 on a good economy, 8 at x2. The Drive, which needs the successful prototype, is built from Production: 1,500
(section 4) x1.20 (section 7's cost scaling for Space-era parts) in the best city, at the era model's typical fork city
Production for the Insight reached, with section 4's spaceship bonuses in the best city (+125%), and an exotic component
(+15%) for the methods that use one (Warp, Wormhole, Plenum); the average player's Production is x0.8, like its Insight. The
other parts (the Apollo Program, three Boosters, the Cockpit) come from CORE Atomic-era breakthroughs that every simulated
player holds 40-70 turns before its finish, so they are built in parallel and never hold the launch up.
Until 15 October 2026 the prototype was a fixed 5 turns (6 on the average economy) and the Drive a pencilled-in 4 (5; a turn
fewer for the exotic methods).

Development follows DEVENDS (or SPACEFROM) as the runs had it: the defaults' unless set, so pass DEVENDS= (empty) and the
run's SPACEPRICE for results made under other settings.
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import defaults
from harness import income, EO
import harness_ftl_e as HF
import ledger as Lg, ledger3 as L3, eramodel as M
HF.SPACE_FROM = float(os.environ['SPACEFROM']) if os.environ.get('SPACEFROM') else None
HF.DEV_ENDS = {e.replace('_', ' '): float(x) for e, x in (i.split(':') for i in os.environ['DEVENDS'].split(','))} if os.environ.get('DEVENDS') else None
SPACEPRICE = float(os.environ.get('SPACEPRICE') or 1.0)
PROTOX = float(os.environ.get('PROTOX', '5'))
SCALE = json.load(open(os.path.join(HERE, 'w7c_cfg.json')))['scale']
P_SPACE = json.load(open(os.path.join(HERE, 'era_prices.json')))['Space']
EXOTIC = {'Warp', 'Wormhole', 'Plenum'}
DRIVE_COST = 1500 * 1.20   # section 4's SS FTL Drive, x1.20 (section 7: units, wonders and spaceship parts, Space era)
DRIVE_BONUS = 1.25         # section 4: the best city's spaceship bonuses (Spaceship Factory, Hubble, lift, assembly)
EXOTIC_BONUS = 0.15        # section 4: an exotic component speeds only the Drive
SPACE = EO.index('Space')
_clocks = {}


def clock(econ, turns=700):
    """Development at the end of each turn, as the harness accumulates it, the Insight a turn from then on, and the Insight
    accumulated."""
    if econ not in _clocks:
        cum, d, inc, cums = 0.0, [0.0], [income(0.0) * econ], [0.0]
        for _ in range(turns):
            cum += income(cum) * econ; d.append(HF.dev_at(cum)); inc.append(income(cum) * econ); cums.append(cum)
        _clocks[econ] = (d, inc, cums)
    return _clocks[econ][:2]


def city_production(t, econ):
    """The era model's typical fork city's Production at turn t, for the Insight accumulated by then (the era model's own
    spans, which the simulated economy follows)."""
    clock(econ); lv = min(_clocks[econ][2][t], Lg.ERA_END['Space'])
    e = next((x for x in Lg.EO if lv <= Lg.ERA_END[x]), Lg.EO[-1])
    return M.city_production(lv, 'fork', L3.POP[e]) * econ


def drive_turns(t, econ, exotic):
    return math.ceil(DRIVE_COST / (city_production(t, econ) * (1 + DRIVE_BONUS + (EXOTIC_BONUS if exotic else 0.0))))


def prototype_turns(t, econ):
    d, inc = clock(econ)
    price = PROTOX * P_SPACE * SCALE * SPACEPRICE * 4 ** max(0.0, SPACE - d[t])
    return math.ceil(price / (0.8 * inc[t]))


def victory(g, econ):
    """The game's victory turn, or None if its race never finished."""
    if not (g['cert'] and g['built']): return None
    fin = max(g['cert'], g['built']); proto = fin + prototype_turns(fin, econ)
    return proto + drive_turns(proto, econ, g['m'] in EXOTIC) + 1
