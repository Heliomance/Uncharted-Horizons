# Usage: python3 design/simulator/power/early_availability.py   (reads design/tech_tree.md; prints both measures)
"""How many breakthroughs become available (prerequisites met) an era or more before their own era?
Direct measure: the earliest era in which a row's prerequisite breakthroughs, by their own eras, can all be held
(for each AND-term, the OR-option whose latest prerequisite era is earliest). Chain measure: the same, but each
prerequisite counted at its own earliest availability rather than its era label. Focus gates ("Available from") are
ignored, as in the simulator; the early-rows review (design/notes/early_rows_review.md) found one row they hold back
(the Ornithopter, behind Aeronautics)."""
import re, sys, collections
sys.path.insert(0, '/home/user/Uncharted-Horizons/design/verification-battery')
import prereq
EO = ['Primitive', 'Ancient', 'Classical', 'Medieval', 'Early Modern', 'Modern', 'Atomic', 'Space']
rows = {}
for line in open('/home/user/Uncharted-Horizons/design/tech_tree.md', encoding='utf-8'):
    m = re.match(r'^\| ([A-Z][A-Z0-9-]*[0-9][A-Z]?(?:-W|-V\d+)?|ME-B) \| \*\*(.+?)\*\* \| (\w+) \| ([^|]+?) \| ([^|]*?) \|', line)
    if not m: continue
    era = next((i for i, e in sorted(enumerate(EO), key=lambda x: -len(x[1])) if m.group(4).strip().startswith(e)), None)
    rows[m.group(1)] = dict(name=m.group(2), tier=m.group(3), era=era, pre=m.group(5))
known = set(rows)
for k, r in rows.items(): r['terms'] = prereq.parse(r['pre'], known)
def avail(k, f):
    best = 0
    for term in rows[k]['terms']:
        opts = [o for o in term if o]
        if not opts: continue
        best = max(best, min(max(f(x) for x in o) for o in opts))
    return best
direct = {k: avail(k, lambda x: rows[x]['era']) for k in rows}
chain = {}
def ch(k, seen=()):
    if k in chain: return chain[k]
    if k in seen: return rows[k]['era']
    v = avail(k, lambda x: ch(x, seen + (k,)))
    chain[k] = v; return v
for k in rows: ch(k)
print(len(rows), 'rows;', sum(1 for r in rows.values() if r['era'] is None), 'without a recognised era')
for name, A in (('direct', direct), ('chain', chain)):
    gaps = {k: rows[k]['era'] - A[k] for k in rows}
    c = collections.Counter(min(g, 3) for g in gaps.values())
    print(f'\n{name}: rows by eras early (3 = 3 or more):', dict(sorted(c.items())))
    by = collections.defaultdict(collections.Counter)
    for k, g in gaps.items():
        if g >= 1: by[rows[k]['tier']][min(g, 3)] += 1
    for t in ('CORE', 'STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE'):
        tot = sum(1 for r in rows.values() if r['tier'] == t)
        print(f'   {t:9} {sum(by[t].values()):3} of {tot:3} an era or more early   (1: {by[t][1]}, 2: {by[t][2]}, 3+: {by[t][3]})')
    if name == 'direct':
        byera = collections.Counter(EO[rows[k]['era']] for k, g in gaps.items() if g >= 1)
        tot_era = collections.Counter(EO[r['era']] for r in rows.values())
        print('   by own era:', ', '.join(f'{e} {byera[e]}/{tot_era[e]}' for e in EO))
        big = sorted((k for k, g in gaps.items() if g >= 2), key=lambda k: (-gaps[k], rows[k]['era']))
        print('   two or more eras early (direct):')
        for k in big[:40]: print(f'     {k:7} {rows[k]["name"][:38]:38} {rows[k]["tier"]:8} {EO[rows[k]["era"]]:12} prerequisites by {EO[A[k]]}')
        print('    ', len(big), 'in all')
