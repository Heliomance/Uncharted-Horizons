"""Stage 3b (v3.86): growth and healing across the disease paradigms; Kiln and Mud Brick."""
exec(open('/home/user/Uncharted-Horizons/design/simulator/power/stage3a.py', encoding='utf-8').read().split('log = []')[0])
lines = lambda: namespace['t'].split('\n')

def edit_cell(rid, col, old, new):
    L = lines(); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]
    cells = L[i].split(' | '); assert cells[col].count(old) == 1, (rid, col, old); cells[col] = cells[col].replace(old, new)
    L[i] = ' | '.join(cells); namespace['t'] = '\n'.join(L)

# --- Kiln Construction: the storage jar goes; fired brick strengthens walls ---------------
edit_building('F02', 'Kiln', lambda spec: None)
edit_row_text('F02', 'Brickmaking is the prerequisite for Mud Brick Construction (CO01).',
              '⟨[+25]% City Strength from defensive buildings⟩ — walls of fired brick. Kiln heat — fired pots, glazes, fired brick — leads on to Glassmaking (OP01), Cast Iron (ME10), Portland Cement (CH16) and Geopolymer Concrete (S09).')
# --- Mud Brick is sun-dried: it follows the first harvests, not the kiln -----------------
edit_cell('CO01', 4, 'F02 (Kiln)', 'G02 (Seed Saving)')
edit_row_text('CO01', 'Basic buildings: the first permanent architecture.',
              'Sun-dried brick bound with the straw of the first harvests: the first permanent architecture.')
for rid in ('S09', 'ME10', 'CH16', 'OP01'):
    edit_cell(rid, 4, 'F02 (Kiln)', 'F02 (Kiln Construction)')
edit_cell('TX10', 4, 'F02 (Kiln — bark processing)', 'F02 (Kiln Construction — bark processing)')

# --- Shared healing ladder: +20 next to cities by the Classical era; field surgery --------
edit_row_text('G03', 'heal [+10] HP', 'heal [+5] HP')
edit_row_text('MD01', 'heal [+20] HP', 'heal [+10] HP')
edit_row_text('MD03', 'heal [+10] HP', 'heal [+5] HP')
edit_building('MD07', 'Surgical Theatre', lambda spec: None)
unlock_cell_prepend('MD07', '⟨[+5] HP when healing⟩ — surgery in the field')
edit_cell('MD07', 1, '**Anesthesia**', '**Anaesthesia**')
# --- Shared growth: Gene Therapy keeps long lives, not growth ----------------------------
edit_row_text('MD11', '⟨[+10]% growth [in all cities]⟩; ', '')

# --- Germ: the canonical Hospital and Medical Lab, empire-wide and late -------------------
edit_row_text('MD05', '⟨[+15]% growth [in all cities]⟩ (sanitation)', '⟨[+10]% growth [in all cities]⟩ (sanitation)')
edit_row_text('MD06', '⟨[+10]% growth [in all cities]⟩; ', '')
edit_row_text('MD20', '[500/3; ⟨[+15]% growth [in this city]⟩;',
              '[500/3; ⟨[+15]% growth [in this city]⟩; ⟨[15]% Food is carried over after population increases [in this city]⟩;')
# --- Miasma: public works — the Hospital and Medical Lab in one, an era early -------------
edit_row_text('MD16', '**Sanitation Works**ⁿ [500/2; ⟨[+10]% growth [in this city]⟩]',
              '**Sanitation Works**ⁿ [500/2; +3 Food; ⟨[25]% Food is carried over after population increases [in this city]⟩ — stores kept sweet in clean air]')
edit_row_text('MD16', 'Only in Miasma worlds.',
              "The miasma world's Hospital and Medical Lab in one, an era before the Germ world's Medical Lab. Only in Miasma worlds.")
# --- Humoral: the physician's art — healing and choice, a little less Food ---------------
edit_row_text('MD17', '**Balancing Clinic**ⁿ [300/2; ', '**Balancing Clinic**ⁿ [300/2; +2 Food; ')
edit_row_text('MD18', '**Pharmacopoeia**ⁿ [500/2; ⟨[+10]% growth [in this city]⟩]',
              '**Pharmacopoeia**ⁿ [500/2; ⟨[+10]% growth [in this city]⟩; ⟨[20]% Food is carried over after population increases [in this city]⟩]')
# --- Vitalist layer ----------------------------------------------------------------------
edit_row_text('MD-V01', 'heal [+20] HP', 'heal [+10] HP')

namespace['t'] = namespace['t'].replace('Complete Tech Tree Design Document (v3.85)', 'Complete Tech Tree Design Document (v3.86)', 1)
open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(namespace['t'])
print('applied')
