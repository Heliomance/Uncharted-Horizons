"""Stage 3a of the power rebalance (v3.85): Food, Culture and Happiness.

Generic flat Food, Culture and Happiness come off fork-made buildings; a building
left with only a little Gold, a specialist slot or nothing is cut, and a row left
without a benefit gets one that adds no list entry. Growth and healing ladders
(which depend on the disease paradigm) are left for stage 3b.
"""
import re, sys

HELPERS = open('/home/user/Uncharted-Horizons/design/simulator/power/prod_pass.py', encoding='utf-8').read()
HELPERS = HELPERS[:HELPERS.index('log=[]')].replace("t=t.replace('(v3.80)','(v3.81)',1)\n", '')
namespace = {}
exec(HELPERS, namespace)          # find_spec, split_top, meaningful, edit_building, edit_row_text; loads tt.md as t
edit_building, edit_row_text, split_top = namespace['edit_building'], namespace['edit_row_text'], namespace['split_top']

STATS = ('Food', 'Production', 'Gold', 'Science', 'Culture', 'Happiness', 'Faith')


def set_flat(spec, **new_values):
    """Rewrite the flat-yield part of a building spec; a value of 0 removes that yield."""
    parts = split_top(spec)
    for index, part in enumerate(parts):
        body, _, flavour = part.partition(' — ')
        tokens = [tok.strip() for tok in body.split(',') if tok.strip()]
        if tokens and all(re.fullmatch(rf'\+\d+ ({"|".join(STATS)})', tok) for tok in tokens):
            kept = []
            for tok in tokens:
                stat = tok.split()[1]
                value = new_values.get(stat, int(tok.split()[0]))
                if value:
                    kept.append(f'+{value} {stat}')
            replacement = ', '.join(kept) + (f' — {flavour}' if flavour else '')
            if replacement:
                parts[index] = ' ' + replacement
            else:
                del parts[index]
            return ';'.join(parts)
    raise ValueError(f'no flat-yield part in: {spec[:80]}')


def unlock_cell_prepend(rid, benefit):
    """Put a row-level benefit at the start of the row's Unlocks cell."""
    lines = namespace['t'].split('\n')
    (i,) = [n for n, line in enumerate(lines) if line.startswith(f'| {rid} |')]
    cells = lines[i].split(' | ')
    rest = cells[5].strip()
    cells[5] = benefit + ('. ' + rest if rest and not rest.startswith(('.', ';')) else rest)
    lines[i] = ' | '.join(cells)
    namespace['t'] = '\n'.join(lines)


log = []

# ---- 1. Consolidation: buildings left thin once generic yields go -------------------------
CUT_WITH_BENEFIT = {
    ('CU04', 'Music Hall'): '⟨[Great Prophet] is earned [+10]% faster⟩ — music in ritual and worship',
    ('CU03', 'Gallery'): '⟨[Great Artist] is earned [+10]% faster⟩ — a tradition that trains its own masters',
    ('G10', 'Vision Lodge'): '⟨[+1 Faith] from [Incense] tiles [in all cities]⟩ — resins burned for visions',
    ('G05', 'Insect Farm'): '⟨[+1 Gold] from [Silk] tiles [in all cities]⟩ — sericulture',
    ('S02', 'Stonecutter'): '⟨[-25]% construction time for [Quarry] improvements⟩ — polished stone cuts stone',
    ('G04', 'Tavern'): '⟨[+1 Gold] from [Wine] tiles [in all cities]⟩ — fermentation makes the grape a trade good',
    ('AH09', 'Apiary'): '⟨[+1 Gold] from [Citrus] tiles [in all cities]⟩ — pollinated orchards',
    ('ME10', 'Cast Iron Works'): '⟨[+1 Gold] from [Iron] tiles [in all cities]⟩ — pots, pans and pipes',
    ('MA02', 'Counting House'): '⟨[+1 Gold] from all [Market] buildings⟩ — place value keeps the market\'s accounts',
    ('TX10', 'Paper Mill'): '⟨[+15]% Production when constructing [Library] buildings [in all cities]⟩ — cheap paper, cheap books',
    ('CH01', 'Laboratory'): '⟨[+1 Gold] from [Salt] tiles [in all cities]⟩ — salt, one of the three principles',
    ('OP01', 'Glassworks'): '⟨[+15]% Production when constructing [Lighthouse] buildings [in all cities]⟩ — glass for the lantern',
    ('MC05', 'Clock Tower'): '⟨[Great Engineer] is earned [+10]% faster⟩ — the clockmaker, the first precision engineer',
    ('EL01', 'Leyden Hall'): '⟨[+1 Culture] from all [Museum] buildings⟩ — galvanic demonstrations draw the crowds',
    ('EL03', 'Electromagnetics Institute'): '⟨[Great Scientist] is earned [+10]% faster⟩ — two forces found to be one',
    ('MA06', "Actuary's Office"): '⟨[+1 Gold] from all [Bank] buildings⟩ — insurance priced by probability',
    ('EL05', 'Tramway'): '⟨[-25]% construction time for [Railroad] improvements⟩ — electric traction',
    ('EN05', 'TV Station'): '⟨[+2 Gold] from all [Broadcast Tower] buildings⟩ — advertising revenue',
    ('TX07', 'Garment Factory'): '⟨[+15]% Production when constructing [Land] units [in all cities]⟩ — mass-produced uniforms and kit',
    ('NP01', 'Radiology Laboratory'): '⟨[+1 Gold] from [Uranium] tiles [in all cities]⟩ — radium, the costliest substance on Earth',
    ('OP06', 'Telecom Exchange'): '⟨[+1 Gold] from all [Stock Exchange] buildings⟩ — prices move at the speed of light',
}
CUT_ROW_KEEPS_CONTENT = [('MC06', 'Printing House'), ('O01', 'Calendar Stone'), ('ME11', 'Cannery'), ('MI13', 'Gasworks'),
                         ('MI10', 'Radiotherapy Ward'), ('QM-E16', 'Boundary Laboratory'), ('CP01', 'Computer Centre')]

for (rid, name), benefit in CUT_WITH_BENEFIT.items():
    log.append((rid, name, edit_building(rid, name, lambda spec: None)))
    unlock_cell_prepend(rid, benefit)
for rid, name in CUT_ROW_KEEPS_CONTENT:
    log.append((rid, name, edit_building(rid, name, lambda spec: None)))

# the elemental mirror of Radioactivity's radium trade (atomic: NP01 gold + MI10 reveal; elemental: QM-E16 both)
unlock_cell_prepend('QM-E16', '⟨[+1 Gold] from [Uranium] tiles [in all cities]⟩ — the warm ores sold as cures')
# Direct-Current Stations folded Happiness onto the Tramway, which is gone
edit_row_text('EL14', '; ⟨[+1 Happiness] from all [Tramway] buildings⟩ (the trams ran on DC)', '')

# ---- 2. Stripping: generic flat Food, Culture and Happiness; situational effects stay ----
STRIP = {
    ('G01', "Forager's Hut"): dict(Happiness=0),         # keeps +1 Food: the Primitive food landmark
    ('G03', 'Herbalist'): dict(Happiness=0),
    ('O04', 'Tidal Weir'): dict(Food=0),                 # keeps +1 Food from Fish, coastal
    ('G06', 'Compost Yard'): dict(Food=0),               # keeps +1 Food from Forest
    ('TX02', 'Dye Works'): dict(Culture=0),
    ('MD02', 'Quarantine Station'): dict(Happiness=0),
    ('CH04', 'Distillery'): dict(Happiness=0),
    ('EL09', 'Radio Transmitter'): dict(Culture=0),
    ('EL13', 'Telephone Exchange'): dict(Happiness=0),
    ('MD07', 'Surgical Theatre'): dict(Happiness=0),
    ('MD16', 'Sanitation Works'): dict(Happiness=0),
    ('MD17', 'Balancing Clinic'): dict(Happiness=0),
    ('MD18', 'Pharmacopoeia'): dict(Happiness=0),
    ('GN12', 'Essence Reservoir'): dict(Food=0, Happiness=0),
    ('MD-V01', 'Essence Clinic'): dict(Happiness=0),
    ('CO13', 'Biome Dome'): dict(Food=0, Happiness=0),
    ('MD13', 'Cryo Chamber'): dict(Happiness=0),
    ('FA10', 'Hydroponics Lab'): dict(Food=2),
    ('WM07', 'Desalination Plant'): dict(Food=2),
    ('SE01', 'Biosphere'): dict(Food=2, Happiness=0),
    ('SE05', 'Bio-Recycler'): dict(Food=1),
}
for (rid, name), values in STRIP.items():
    log.append((rid, name, edit_building(rid, name, lambda spec, v=values: set_flat(spec, **v))))

# ---- 3. Carry-over family: only the Kiln keeps 10% (the Tavern, Glassworks and Cannery are cut above)

from collections import Counter
print(Counter(status for _, _, status in log))
unexpected = [(r, n, s) for r, n, s in log if (s == 'removed') != ((r, n) in CUT_WITH_BENEFIT or (r, n) in CUT_ROW_KEEPS_CONTENT)]
print('unexpected outcomes:', unexpected)
open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(namespace['t'])
