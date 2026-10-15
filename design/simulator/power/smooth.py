"""Settings for a set of era price multipliers (Tamsin, 15 Oct 2026: smooth the discovery rate through the game, counting rivals'
knowledge, keeping parity with base Civ V's science victory).

Each multiplier scales its era's price per discovery against v3.108's. Up to the Early Modern era the era's span of Insight moves
with its price, as section 2's rule has it (span = price x expected discoveries), so that development crosses the era about as fast
as players research it; the later boundaries stay at base Civ V's era timing (v3.122). Idea windows follow the eras' new lengths
on a good economy. Prints the environment assignments for a run (ERAPRICE, MODERNPRICE, ATOMICPRICE, SPACEPRICE, DEVENDS, WINTURNS).
A span can also move on its own (span.Era=y, up to the Early Modern era), for an era whose players make more or fewer
discoveries in it than its span expects.
Usage: python3 smooth.py Primitive=1 Ancient=1.3 ... Space=1.2 [span.Primitive=1.3]   (eras not named stay at 1)
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ledger as Lg
from harness import income
import harness_ftl_e as HF

EO = Lg.EO; LATE = {'Modern': 66231.0, 'Atomic': 113629.0, 'Space': 209676.0}   # base Civ V's era timing on a good economy (v3.122)
mult = {e: 1.0 for e in EO}; span = {e: 1.0 for e in EO}
for a in sys.argv[1:]:
    e, x = a.split('=')
    if e.startswith('span.'): span[e[5:].replace('_', ' ')] = float(x)
    else: mult[e.replace('_', ' ')] = float(x)
ends, prev, cum = {}, 0.0, 0.0
for e in EO:
    if e in LATE: ends[e] = LATE[e]
    else: cum += (Lg.ERA_END[e] - prev) * mult[e] * span[e]; ends[e] = cum
    prev = Lg.ERA_END[e]
def starts(dev_ends):
    HF.DEV_ENDS = dev_ends; d, c = [0.0], 0.0
    for _ in range(700): c += income(c); d.append(HF.dev_at(c))
    return [next(t for t, x in enumerate(d) if x >= i) for i in range(len(EO) + 1)]
old_s = starts({e: LATE.get(e, Lg.ERA_END[e]) for e in EO}); new_s = starts(ends)
win = {'Modern': 47, 'Atomic': 36, 'Space': 56}   # the defaults (v3.122); an era whose span moved takes its new length in turns
for i, e in enumerate(EO):
    if (old_s[i], old_s[i + 1]) != (new_s[i], new_s[i + 1]) and e != 'Space': win[e] = new_s[i + 1] - new_s[i]
early = ','.join(f"{e}:{mult[e]:g}" for e in EO if e not in LATE and mult[e] != 1.0)
print(' '.join([f"ERAPRICE={early.replace(' ', '_')}" if early else 'ERAPRICE=', f"MODERNPRICE={mult['Modern']:g}", f"ATOMICPRICE={mult['Atomic']:g}",
                f"SPACEPRICE={mult['Space']:g}", 'DEVENDS=' + ','.join(f"{e.replace(' ', '_')}:{ends[e]:.0f}" for e in EO),
                'WINTURNS=' + ','.join(f"{e.replace(' ', '_')}:{win[e]}" for e in EO if e in win)]))
