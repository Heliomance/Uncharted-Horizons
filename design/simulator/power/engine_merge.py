"""v3.96: one Internal Combustion Engine, opened by either fuel; the Coal and Oil Plants in every world; the Biomass Plant weaker."""
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read(); L = t.split('\n')
def idx(k): (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {k} |')]; return i
cells = lambda k: [x.strip() for x in L[idx(k)].split('|')[1:-1]]
u = cells('MC09-W')[5]
depot = u[u.index('**Distillery Fuel Depot**ⁿ'):u.index('the surplus the grain would have become.') + len('the surplus the grain would have become.')]
L[idx('MC09')] = ('| MC09 | **Internal Combustion Engine** | CORE | Modern | MC08 + (MI07 + CH09 or CH04 + CH07) | '
    '**Landship**, **Tank**, **Anti-Tank Gun** (units — Tank requires **Oil**; the Landship and Tank take this row as their `requiredTech`). ' + depot +
    ' Either fuel opens the engine — petroleum refined where there are wells (Petroleum Discovery and Petrochemistry), distilled alcohol where there are none (Distillation and Organic Chemistry) — '
    'and every civilisation can raise Depots: an expensive way to get Oil, worth it to a civilisation short of wells, or to one pushing to field more tanks and aircraft than its wells could fuel. '
    '*Also discoverable through Chemistry.* | Brazil ran its economy on ethanol, and fuel-starved Europe ran its cars on alcohol and wood gas in the Second World War. |')
del L[idx('MC09-W')]
t = '\n'.join(L)
def rep(old, new):
    global t; assert t.count(old) == 1, (old[:70], t.count(old)); t = t.replace(old, new)
# dependents and cross-references of the engine
rep('Alcohol Combustion Engine (MC09-W, from Mechanics)', 'Internal Combustion Engine (MC09, from Mechanics)')
rep('*Available from: (MC09 or MC09-W), or AE01 (Hot Air Balloon)*', '*Available from: MC09, or AE01 (Hot Air Balloon)*')
rep('| AE01 + (MC09 or MC09-W) or EL05 |', '| AE01 + MC09 or EL05 |')
rep('| (MC09 or MC09-W) + MA04 (Trigonometry) |', '| MC09 + MA04 (Trigonometry) |')
rep('- **Oil is grown.** A Distillery Fuel Depot (MC09-W) provides', '- **Oil is grown.** A Distillery Fuel Depot (MC09) provides')
rep('{non-[Alcohol Combustion Engine]}', '{non-[Internal Combustion Engine]}')
rep('| Landship | Combustion | **MC09** or **MC09-W** |', '| Landship | Combustion | **MC09** |')
rep('| Tank | Combined Arms | **MC09** or **MC09-W** |', '| Tank | Combined Arms | **MC09** |')
rep('| Motorisation | Internal Combustion Engine (MC09) | Alcohol Combustion Engine (MC09-W) | persists — its Depots grow Oil from farmland |\n', '')
# the power plants: Coal and Oil Plants burn their fuel however it is made
L = t.split('\n')
def setcell(k, col, old, new):
    i = idx(k); c = L[i].split(' | '); assert c[col].count(old) == 1, (k, old); c[col] = c[col].replace(old, new); L[i] = ' | '.join(c)
setcell('ES03', 4, 'TH03 + MI06 (Coal)', 'TH03 + ME08 (Blast Furnace — coal or charcoal)')
setcell('ES03', 5, '**Absent in FOSSIL_FUELS_ABSENT worlds**, with Coal Discovery, which it needs.', 'It burns Coal from pits or Charcoal Kilns alike, so it exists in every world.')
setcell('ES05', 4, 'MI07 (Petroleum) + TH03', 'TH03 + (MI07 or MC09) — petroleum, or the engine that distils it')
setcell('ES05', 5, '**Absent in FOSSIL_FUELS_ABSENT worlds**, with Petroleum Discovery, which it needs.', 'It burns Oil from wells or Distillery Fuel Depots alike, so it exists in every world.')
setcell('ES03-W', 5, '310/2; requires a **Factory** in this city; +2 Production;', '440/2; requires a **Factory** in this city; +1 Production;')
setcell('ES03-W', 5, '— it needs no Coal and makes no smoke.; primary in FOSSIL_FUELS_ABSENT worlds.', '— it needs no Coal and makes no smoke, and gives up a point of Production for it. A power station costs what its peers do, whatever it burns.')
setcell('ES05-W', 4, 'MC09-W (Alcohol Engine) or ES13 (Biomass/Biogas) + TH03', 'MC09 (Internal Combustion Engine) or ES13 (Biomass/Biogas) + TH03')
setcell('ES05-W', 5, '— it needs no Oil.; primary in FOSSIL_FUELS_ABSENT worlds.', '— it needs no Oil.')
t = '\n'.join(L)
# prose: the fossil-free world, Guarantee Rule 9, tallies
import re
m = re.search(r'- \*\*FOSSIL_FUELS_ABSENT\*\*: ~10% of games\.[^\n]*', t); old = m.group(0)
new = ('- **FOSSIL_FUELS_ABSENT**: ~10% of games. MI06 (Coal) and MI07 (Petroleum) are removed, and with them Petrochemistry (CH09), which needs Petroleum. '
       'The Blast Furnace (ME08) and the Internal Combustion Engine (MC09) open without them — by charcoal and by distilled alcohol — and their Charcoal Kilns and Distillery Fuel Depots make the Coal and Oil, '
       'which the Coal and Oil Power Plants then burn. Bio-Organic Synthesis (CH09-W) can never be locked out there, its primary being absent, which makes it the primary chemistry path; '
       'the Biomass and Bio-Fuel Plants remain Competing Solutions, as in every world.')
rep(old, new)
m = re.search(r'9\. Vehicles/motorisation always achievable[^\n]*', t); rep(m.group(0),
    '9. Vehicles/motorisation always achievable: the Internal Combustion Engine (MC09) is CORE and opens with either fuel — petroleum, or distilled alcohol — so it exists in every world. Where there are no wells, its Distillery Fuel Depots make Oil from worked Farms, and trade can supply the rest (§1.2).')
rep('| Competing Solutions groups | 17 (11 persist, 6 are superseded) |', '| Competing Solutions groups | 16 (10 persist, 6 are superseded) |')
rep('| Total Breakthroughs | ~549 |', '| Total Breakthroughs | ~548 |')
rep('| CORE Breakthroughs | ~151 |', '| CORE Breakthroughs | ~152 |')
rep('| STANDARD Breakthroughs | ~246 |', '| STANDARD Breakthroughs | ~244 |')
rep('Complete Tech Tree Design Document (v3.95)', 'Complete Tech Tree Design Document (v3.96)')
open(p, 'w', encoding='utf-8').write(t); print('applied')
