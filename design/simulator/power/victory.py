"""A benchmark game's victory turn, for the tools that report one (victory_table.py, space_timing.py).

victory = the race's finish (certainty and the build both done) + the prototype + the SS FTL Drive + 1 turn to deliver and
launch. The prototype is a Grand Endeavour (section 4) priced at PROTOX (default 5) x the Space era's price per discovery
(SPACEPRICE, as the run had it) x the model's calibration, with the ahead-of-time premium at the finish, when it is committed.
It is paid from the active focus's share (80%) of the Insight a turn then, so it lengthens as Space-era research grows dearer:
4 turns at x0.8 on a good economy, 8 at x2. The Drive takes 4 turns on a good economy and 5 on the average one, a turn fewer
where exotic components exist (Warp, Wormhole, Plenum). Until 15 October 2026 the prototype was a fixed 5 turns (6 on the
average economy).

Development follows DEVENDS (or SPACEFROM) as the runs had it: the defaults' unless set, so pass DEVENDS= (empty) and the
run's SPACEPRICE for results made under other settings.
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import defaults
from harness import income, EO
import harness_ftl_e as HF
HF.SPACE_FROM = float(os.environ['SPACEFROM']) if os.environ.get('SPACEFROM') else None
HF.DEV_ENDS = {e: float(x) for e, x in (i.split(':') for i in os.environ['DEVENDS'].split(','))} if os.environ.get('DEVENDS') else None
SPACEPRICE = float(os.environ.get('SPACEPRICE') or 1.0)
PROTOX = float(os.environ.get('PROTOX', '5'))
SCALE = json.load(open(os.path.join(HERE, 'w7c_cfg.json')))['scale']
P_SPACE = json.load(open(os.path.join(HERE, 'era_prices.json')))['Space']
EXOTIC = {'Warp', 'Wormhole', 'Plenum'}
SPACE = EO.index('Space')
_clocks = {}


def clock(econ, turns=700):
    """Development at the end of each turn, as the harness accumulates it, and the Insight a turn from then on."""
    if econ not in _clocks:
        cum, d, inc = 0.0, [0.0], [income(0.0) * econ]
        for _ in range(turns):
            cum += income(cum) * econ; d.append(HF.dev_at(cum)); inc.append(income(cum) * econ)
        _clocks[econ] = (d, inc)
    return _clocks[econ]


def prototype_turns(t, econ):
    d, inc = clock(econ)
    price = PROTOX * P_SPACE * SCALE * SPACEPRICE * 4 ** max(0.0, SPACE - d[t])
    return math.ceil(price / (0.8 * inc[t]))


def victory(g, econ):
    """The game's victory turn, or None if its race never finished."""
    if not (g['cert'] and g['built']): return None
    fin = max(g['cert'], g['built']); drive = 4 if econ >= 1.0 else 5
    return fin + prototype_turns(fin, econ) + (drive - 1 if g['m'] in EXOTIC else drive) + 1
