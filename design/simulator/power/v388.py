"""v3.88: the requirement audit, the safe-predecessor rule, the military chain, the culture first-rung rule."""
exec(open('/home/user/Uncharted-Horizons/design/simulator/power/stage3a.py', encoding='utf-8').read().split('log = []')[0])
article = lambda b: 'an' if b[0] in 'AEIOU' else 'a'
def add_requirement(spec, required):
    parts = split_top(spec)
    lead = r'\s*(\d+(?:/\d+)?|maintenance \d+|a grid plant: ⟨Power Plant⟩ \(tag\))\s*'
    i = max(n for n, p in enumerate(parts[:4]) if re.fullmatch(lead, p))
    parts.insert(i + 1, f' requires {article(required)} **{required}** in this city')
    return ';'.join(parts)
def edit_cell(rid, col, old, new):
    L = namespace['t'].split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]
    cells = L[i].split(' | '); assert cells[col].count(old) == 1, (rid, col, old); cells[col] = cells[col].replace(old, new)
    L[i] = ' | '.join(cells); namespace['t'] = '\n'.join(L)
def replace_once(old, new):
    assert namespace['t'].count(old) == 1, old[:60]; namespace['t'] = namespace['t'].replace(old, new)

# ---- 0. the Melancholic Hall lost its Science in Stage 1 and was left empty ----------------
edit_row_text('MD19', '**Melancholic Hall**ⁿ [500/2; ⟨Regimen Hall⟩ (tag);',
              '**Melancholic Hall**ⁿ [500/2; ⟨[+25]% Great Person generation [in this city]⟩ — the temperament of genius; ⟨Regimen Hall⟩ (tag);')
# ---- 1. nineteen new requirements from the audit -----------------------------------------
AUDIT = [('MD01','Surgery','Herbalist'), ('MD03','Medical School','Library'), ('PH07','Experimental Laboratory','University'),
         ('NP02','Nuclear Physics Lab','Research Lab'), ('QM-E01','Deep Matter Lab','Research Lab'), ('CP07','AI Lab','Research Lab'),
         ('CP14','Perceptron Laboratory','Research Lab'), ('TR06','Trading Company','Bank'), ('TR10','Commodity Exchange','Bank'),
         ('SF10','Drydock','Harbor'), ('MC16','Automated Workshop','Workshop'), ('TX05','Textile Mill','Weaver'),
         ('EN06','Fab','Microchip Foundry'), ('MC09-W','Distillery Fuel Depot','Distillery')] + \
        [('MD19', h, 'Balancing Clinic') for h in ('Choleric Hall','Melancholic Hall','Phlegmatic Hall','Sanguine Hall')]
for rid, name, req in AUDIT:
    assert edit_building(rid, name, lambda s, r=req: add_requirement(s, r)) == 'edited', name

# ---- 2. the two Scientist-slot shells Stage 3a missed ------------------------------------
for rid, name in (('O07','Anatomy Theatre'), ('PH01','Logic School')):
    assert edit_building(rid, name, lambda s: None) == 'removed'

# ---- 3. the military chain: Castle and Armory rows to CORE; the Ring Fortress --------------
edit_cell('CO24', 2, 'STANDARD', 'CORE'); edit_cell('ME18', 2, 'STANDARD', 'CORE')
assert edit_building('CO11', 'Bunker', lambda s: None) == 'removed'
edit_row_text('MC10', '**Military Base**; ', '')
L = namespace['t'].split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith('| CO25 |')]
L.insert(i + 1, '| CO26 | **Ring Fortress** | STANDARD | Modern | CO25 (Star Fort) + CO11 (Reinforced Concrete) | '
    '**Military Base**; **Bunker**ⁿ [500/1; requires a **Military Base** in this city; cityStrength +8; cityHealth +50] — detached forts in concrete and steel. | '
    'Rifled shells made the bastion obsolete, and after 1885 high explosive did the same to masonry: the forts were rebuilt as a ring of detached works in concrete and steel — Liège, Verdun. Neither prerequisite needs gunpowder: Star Fort also accepts the Trebuchet. |')
namespace['t'] = '\n'.join(L)
replace_once('| Military Base | Replaceable Parts | **MC10** |', '| Military Base | Replaceable Parts | **CO26** |')

# ---- 4. requirement overrides for canonical buildings (the culture first-rung rule) ------
replace_once('| Pagoda | — | *Faith-purchased worship building — gated by Belief, not a breakthrough* |\n',
 '| Pagoda | — | *Faith-purchased worship building — gated by Belief, not a breakthrough* |\n\n'
 '**Requirement overrides.** The ruleset derivation changes these canonical `requiredBuilding` values. Every requirement must name a safe predecessor: one whose row is certain to come first, or a CORE row of the same or an earlier era that is reachable wherever the dependent is (battery check 13). Vanilla chains its culture and happiness buildings rung by rung, for pacing rather than realism — a museum does not need an opera house. In this tree the middle rungs sit on STANDARD rows, so a rung-by-rung chain could leave a top building unbuildable. Instead a top rung requires its line\'s *first* rung: cheap, always reachable, and still no way to buy only the best building. The Broadcast Tower needs nothing, because its +33% Culture multiplies whatever the city already has.\n\n'
 '| Building | Vanilla requires | Fork requires |\n|---|---|---|\n'
 '| Opera House | Amphitheater | Monument |\n| Ceilidh Hall | Amphitheater | Monument |\n| Museum | Opera House | Monument |\n'
 '| Stadium | Theatre | Colosseum |\n| Broadcast Tower | Museum | — |\n')

# ---- 5. tallies and version --------------------------------------------------------------
replace_once('| Total Breakthroughs | ~549 |', '| Total Breakthroughs | ~550 |')
replace_once('| CORE Breakthroughs | ~148 |', '| CORE Breakthroughs | ~150 |')
replace_once('| STANDARD Breakthroughs | ~249 |', '| STANDARD Breakthroughs | ~248 |')
replace_once('Complete Tech Tree Design Document (v3.87)', 'Complete Tech Tree Design Document (v3.88)')
open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(namespace['t']); print('applied')
