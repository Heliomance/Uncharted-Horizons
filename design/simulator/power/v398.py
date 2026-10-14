"""v3.98: the end of the power pass — Mycological Knowledge as a path less travelled, the Biogas Plant, Selective Breeding's prerequisite."""
import json
exec(open('/home/user/Uncharted-Horizons/design/simulator/power/stage3a.py', encoding='utf-8').read().split('log = []')[0])
cel = json.load(open('/tmp/cellar.json'))
def edit_cell(rid, col, old, new):
    L = namespace['t'].split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]
    cells = L[i].split(' | '); assert cells[col].count(old) == 1, (rid, col, old); cells[col] = cells[col].replace(old, new)
    L[i] = ' | '.join(cells); namespace['t'] = '\n'.join(L)
# 1. nothing waits on Mycological Knowledge any more
edit_cell('MD06', 4, 'MD05 (Germ Theory validated) + G06 (Mycological Knowledge)', 'MD05 (Germ Theory validated) + CH07 (Organic Chemistry)')
edit_cell('FA06', 4, 'FA02 + G06 (Mycological Knowledge)', 'FA02 (Crop Rotation)')
edit_cell('ES13', 4, 'G06 (Mycological Knowledge) + CH04 (Distillation)', 'CH04 (Distillation) + CH07 (Organic Chemistry)')
edit_cell('MD04', 4, 'MD03 + (G06 (Mycological Knowledge) or AH02 (Herd Animal Domestication — the milkmaid observation))', 'MD03 + AH02 (Herd Animal Domestication — the milkmaid observation)')
# 2. Mycological Knowledge: the Mushroom Cellar, and a path less travelled
edit_row_text('G06', '**Compost Yard**ⁿ [20/0; ⟨[+1 Food] from [Forest] tiles [in this city]⟩ — fungal harvest]. Bridges to Medicine (MD04, MD06). Makes Bio-Organic Synthesis (CH09-W) cost ×0.5 (a multiplier, §1.2) — fungi and fermentation are its oldest tools.',
    f'**Mushroom Cellar**ⁿ [{cel["cost"]}/{cel["upkeep"]}; ⟨[+1 Food] from [Forest] tiles [in this city]⟩; ⟨[+1 Food] from [Jungle] tiles [in this city]⟩ — mushrooms from woods left standing]. '
    'A path less travelled: nothing needs it, but a civilisation that knows its moulds and ferments early is quicker down a whole biological lane — '
    'it makes Antibiotics (MD06), Bio-Organic Synthesis (CH09-W) and Biomass/Biogas (ES13) cost ×0.5 (a multiplier, §1.2). '
    '*Provisional:* how accelerators are stated — a cost factor or a head start — awaits the discovery-model decision, and these three will be restated with the rest.')
# 3. the Biogas Plant: weaker, not cheaper, like the Biomass Plant
edit_row_text('ES13', '310/2; requires a **Factory** in this city; +2 Production;', '440/2; requires a **Factory** in this city; +1 Production;')
edit_row_text('ES13', 'Waste into power, in any terrain.', 'Waste into power, in any terrain — it needs no fuel and gives up a point of Production for it.')
# 4. Selective Breeding: the OR that was meant
edit_cell('FA03', 4, 'G02 + G07 (Botanical Classification) or FA01 (Irrigation) + FA02 (Crop Rotation)', 'G02 + (G07 (Botanical Classification) or FA01 (Irrigation) + FA02 (Crop Rotation))')
namespace['t'] = namespace['t'].replace('Complete Tech Tree Design Document (v3.97)', 'Complete Tech Tree Design Document (v3.98)', 1)
open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(namespace['t']); print('applied')
