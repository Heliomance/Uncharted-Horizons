"""Stage 5 (v3.90): value pricing of fork buildings, the Water Mill's era, and the cost-scaling table."""
import sys, re, json, json5
sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
exec(open('/home/user/Uncharted-Horizons/design/simulator/power/stage3a.py', encoding='utf-8').read().split('log = []')[0])
import pricing as PR, buildtime as BT, ledger as Lg
ERA_COST = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/stage5_prices.json'))['ERA_COST']
UP = {'Primitive': 2.5, 'Ancient': 1.33, 'Classical': 1.17, 'Medieval': 0.85, 'Early Modern': 0.8, 'Modern': 0.55, 'Atomic': 0.55, 'Space': 0.55}
CANON = {b['name']: b for b in json5.load(open('/home/user/Uncharted-Horizons/design/simulator/unciv/Buildings.json', encoding='utf-8'))}
LEAD = r'\s*(\d+/\d+|\d{2,4}|maintenance \d+)\s*'
DRY = '--dry' in sys.argv

def classify(name, spec):
    if re.match(r'\s*unit\b', spec) or re.search(r'\bStrength \d', spec[:80]): return 'unit'
    if re.search(r'world wonder|national wonder|\bwonder\b', spec[:60]): return 'wonder'
    if re.search(r'Unbuildable|buy-only|improvement\b', spec[:60]): return 'not built'
    if re.search(r'⟨Launch Complex⟩|Spaceship part|\[SS [A-Z]', spec): return 'spaceship stack'
    if not any(re.fullmatch(LEAD, p) for p in split_top(spec)[:4]) and re.search(r'Costs \[\d+\] \[', spec): return 'stockpile-bought'
    if re.search(r'replaces ([A-Z][A-Za-z\' ]+?)\s*[;\]]', spec): return 'replacement'
    return 'value'

def new_cost(name, spec, era, kind):
    if kind == 'replacement':
        base = re.search(r'replaces ([A-Z][A-Za-z\' ]+?)\s*[;\]]', spec).group(1)
        if base in CANON: return BT.base_cost(CANON[base]), CANON[base].get('maintenance', 0), base
        return None                                   # replaces a fork building: priced by value like any other
    v = PR.spec_value(spec, era); p = 5 * round(ERA_COST[era] * min(1.5, max(0.25, v / 4)) / 5)
    return p, round(p * UP[era] / 100), f'{v:.1f} pts'

def rewrite(spec, cost, upkeep):
    parts = split_top(spec)
    idx = [n for n, p in enumerate(parts[:4]) if re.fullmatch(LEAD, p)]
    if idx:
        at = idx[0]
        for n in reversed(idx): del parts[n]
    else:
        at = 1 if re.fullmatch(r'\s*a grid plant: ⟨Power Plant⟩ \(tag\)\s*', parts[0]) else 0
    parts.insert(at, f'{" " if at else ""}{cost}/{upkeep}')
    return ';'.join(parts)

t = namespace['t']; body = t[:t.index('\n## 4.')]
import ledger2 as L2
plan = []
for l in body.split('\n'):
    c = [x.strip() for x in l.split('|')[1:-1]]
    if len(c) < 7 or not re.match(r'^[A-Z][A-Z0-9-]*$', c[0]) or not c[1].startswith('**'): continue
    era = c[3] if c[3] in UP else None
    for name, spec, a, k in L2.bspecs(c[5]):
        kind = classify(name, spec)
        if kind in ('value', 'replacement') and era:
            nc = new_cost(name, spec, era, kind)
            if nc is None: kind = 'value'; nc = new_cost(name, spec, era, 'value')
            plan.append((c[0], era, name, kind, nc, spec))
        else:
            plan.append((c[0], era, name, kind, None, spec))
from collections import Counter
print(Counter(k for _, _, _, k, _, _ in plan))
for kind in ('spaceship stack', 'stockpile-bought', 'not built'):
    print(f"  {kind}: {[n for _, _, n, k, _, _ in plan if k == kind]}")
print("  replacements priced from their base:", [(n, nc[2], nc[0]) for _, _, n, k, nc, _ in plan if k == 'replacement'][:12], '…')
if not DRY:
    for rid, era, name, kind, nc, spec in plan:
        if nc: assert edit_building(rid, name, lambda s, cc=nc: rewrite(s, cc[0], cc[1])) == 'edited', name
    L = namespace['t'].split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith('| WM05 |')]
    cells = L[i].split(' | '); assert cells[3] == 'Medieval'; cells[3] = 'Classical'; L[i] = ' | '.join(cells)
    namespace['t'] = '\n'.join(L)
    json.dump([(r, e, n, k, nc) for r, e, n, k, nc, _ in plan], open('/home/user/Uncharted-Horizons/design/simulator/power/stage5_applied.json', 'w'))
    open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(namespace['t']); print('written')
