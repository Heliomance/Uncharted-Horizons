"""Stage 3a, Food: one enclosed-farming building (the Hydroponics Lab); farm and terrain Food only where situational."""
exec(open('/home/user/Uncharted-Horizons/design/simulator/power/stage3a.py',encoding='utf-8').read().split('log = []')[0])
log = []
CUT_WITH_BENEFIT = {
    ('FA08', 'Seed Drill Works'): '⟨[-25]% construction time for [Farm] improvements⟩ — one machine sows what many hands did',
    ('O12', 'Weather Bureau'): '⟨[+1 Gold] from all [Harbor] buildings⟩ — storm warnings for shipping',
    ('SE01', 'Biosphere'): '⟨[+10]% Strength <for [Submarine] units>⟩ — the sealed hull breathes',
    ('SE05', 'Bio-Recycler'): '⟨[-10]% maintenance cost for [All] buildings [in all cities]⟩ — nothing wasted',
    ('CO13', 'Biome Dome'): '⟨[+15]% Production when constructing [Stadium] buildings [in all cities]⟩ — the dome over the arena',
    ('FA11', 'Vertical Farm'): '⟨[+1 Gold] from all [Hydroponics Lab] buildings⟩ — produce grown and sold inside the city',
    ('SE07', 'Climate Control'): '⟨[-25]% construction time for [All] improvements⟩ — hard land made gentle',
}
for (rid, name), benefit in CUT_WITH_BENEFIT.items():
    log.append((rid, name, edit_building(rid, name, lambda spec: None)))
    unlock_cell_prepend(rid, benefit)
edit_row_text('FA11', ' The city feeds itself in proportion to its size.', '')
for (rid, name), values in {('WM07', 'Desalination Plant'): dict(Food=0), ('FA09', 'Greenhouse'): dict(Food=0)}.items():
    log.append((rid, name, edit_building(rid, name, lambda spec, v=values: set_flat(spec, **v))))
print(log)
open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(namespace['t'])
