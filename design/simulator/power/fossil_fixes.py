"""v3.93: the fossil-fuel-absent guarantees, and Vaccination's vague prerequisite."""
exec(open('/home/user/Uncharted-Horizons/design/simulator/power/stage3a.py', encoding='utf-8').read().split('log = []')[0])
def edit_cell(rid, col, old, new):
    L = namespace['t'].split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]
    cells = L[i].split(' | '); assert cells[col].count(old) == 1, (rid, col, old); cells[col] = cells[col].replace(old, new)
    L[i] = ' | '.join(cells); namespace['t'] = '\n'.join(L)
# 1. the charcoal route's knowledge is not terrain-gated; its Coal still needs fuel tiles (or trade)
edit_cell('ME08-W', 4, 'ME04 + F03 (Charcoal) + CO02 + Forest biome (≥3 forest tiles in territory)', 'ME04 + F03 (Charcoal) + CO02')
# 2. Mycological Knowledge speeds Bio-Organic Synthesis rather than gating it
edit_cell('CH09-W', 4, 'CH07 + G06 (Mycological Knowledge) + FA03 (Selective Breeding)', 'CH07 + FA03 (Selective Breeding)')
edit_row_text('G06', 'Bridges to Medicine (MD04, MD06).', 'Bridges to Medicine (MD04, MD06). Makes Bio-Organic Synthesis (CH09-W) cost ×0.5 (a multiplier, §1.2) — fungi and fermentation are its oldest tools.')
# 3. Vaccination: the "empirical observation" is the milkmaid's, and it needs herds
edit_cell('MD04', 4, 'MD03 + G06 (Mycological Knowledge) or empirical observation', 'MD03 + (G06 (Mycological Knowledge) or AH02 (Herd Animal Domestication — the milkmaid observation))')
namespace['t'] = namespace['t'].replace('Complete Tech Tree Design Document (v3.92)', 'Complete Tech Tree Design Document (v3.93)', 1)
open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(namespace['t']); print('applied')
