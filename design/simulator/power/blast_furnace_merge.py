"""v3.94: one Blast Furnace, opened by either fuel; the Charcoal Kiln as a Coal source for everyone."""
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read(); L = t.split('\n')
def row(k): (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {k} |')]; return i
iW = row('ME08-W'); cW = [x.strip() for x in L[iW].split('|')[1:-1]]
u = cW[5]
start = u.index('**Charcoal Kiln**ⁿ'); end = u.index('which is why coal won.') + len('which is why coal won.')
kiln = u[start:end]
assert 'Charcoal Ironworks' not in kiln and 'Managed Forest' not in kiln
i8 = row('ME08')
L[i8] = ('| ME08 | **Blast Furnace** | CORE | Medieval | ME04 + CO02 (Post and Lintel) + (MI06 (Coal Discovery) or F03 (Charcoal Production)) | '
         '**Ironworks** (national wonder). Requires **Coal**. ' + kiln + ' Either fuel opens the furnace — coal where there are seams, charcoal where there are none — '
         'and every civilisation can raise kilns: an expensive way to get Coal, worth it to a civilisation short of seams, or to one pushing to raise a coal-powered army '
         'larger than its seams could supply. | In our world, Sweden ran charcoal blast furnaces into the 19th century, and England\'s iron was charcoal-smelted until coke took over in the 1700s. |')
del L[iW]
t = '\n'.join(L)
def rep(old, new, n=1):
    global t; assert t.count(old) == n, (old[:60], t.count(old)); t = t.replace(old, new)
for old in ('| (ME08 or ME08-W) + CH05 (Oxygen Theory) |', '| (ME08 or ME08-W) + CO03 |', '+ ME08 or ME08-W (Blast Furnace) |', '| SF11 + (ME08 or ME08-W) |', '| ME08 or ME08-W (Blast Furnace — coal or charcoal) +'):
    rep(old, old.replace('(ME08 or ME08-W)', 'ME08').replace('ME08 or ME08-W', 'ME08'))
rep('a fuel tile for a Charcoal Kiln (ME08-W)', 'a fuel tile for a Charcoal Kiln (ME08)')
rep("toward its Charcoal Kiln's fuel (ME08-W)", "toward its Charcoal Kiln's fuel (ME08)")
rep('- **Coal is charcoal.** A Charcoal Kiln (ME08-W) provides', '- **Coal is charcoal.** A Charcoal Kiln (ME08) provides')
rep('MI06 (Coal) and MI07 (Petroleum) removed along with all breakthroughs requiring them (ME08, MC09, CH09, ES03, ES05). The UNCOMMON alternatives (ME08-W, MC09-W, CH09-W, ES03-W, ES05-W) can never be obsoleted, making bio-fuel and charcoal the primary industrial paths.',
    'MI06 (Coal) and MI07 (Petroleum) removed along with all breakthroughs requiring them (MC09, CH09, ES03, ES05). The Blast Furnace (ME08) opens with Charcoal Production instead, and its Charcoal Kilns make the Coal. The Competing Solution alternatives (MC09-W, CH09-W, ES03-W, ES05-W) can never be locked out, making bio-fuel and charcoal the primary industrial paths.')
rep('8. Mass iron/steel production always achievable (ME08-W charcoal blast furnace, a STANDARD Competing Solution; in FOSSIL_FUELS_ABSENT worlds its primary is absent, so it has no detour margin and can never be locked out). Its knowledge has no terrain condition; the Charcoal Kiln\'s Coal needs worked fuel tiles — Forest, Jungle or Peat Cutting — or trade (§1.2).',
    '8. Mass iron/steel production always achievable: the Blast Furnace (ME08) is CORE and opens with either fuel, Coal Discovery or Charcoal Production, so it exists in every world. Where there are no coal seams, its Charcoal Kilns make Coal from worked fuel tiles — Forest, Jungle or Peat Cutting — and trade can supply the rest (§1.2).')
rep('| Furnaces hot enough for mass steel | Blast Furnace (ME08) | Charcoal Blast Furnace (ME08-W) | persists — its kilns make Coal from worked woodland and peat |\n', '')
rep('one grid plant, one temperament, one Ironworks, bank or draw,', 'one grid plant, one temperament, bank or draw,')
rep('| Competing Solutions groups | 18 (12 persist, 6 are superseded) |', '| Competing Solutions groups | 17 (11 persist, 6 are superseded) |')
rep('| Total Breakthroughs | ~550 |', '| Total Breakthroughs | ~549 |')
rep('| CORE Breakthroughs | ~150 |', '| CORE Breakthroughs | ~151 |')
rep('| STANDARD Breakthroughs | ~248 |', '| STANDARD Breakthroughs | ~246 |')
rep('Complete Tech Tree Design Document (v3.93)', 'Complete Tech Tree Design Document (v3.94)')
open(p, 'w', encoding='utf-8').write(t); print('merged')
