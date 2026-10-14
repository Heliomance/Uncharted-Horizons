"""Thinning batch 4: Ancient-era skeleton merges — eight rows into their natural partners."""
import re
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read()
def rep(old, new):
    global t; assert t.count(old) == 1, (old[:80], t.count(old)); t = t.replace(old, new)
def append(host, text):
    global t
    L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {host} |')]
    cells = L[i].split(' | '); cells[5] = cells[5].rstrip() + ' ' + text; L[i] = ' | '.join(cells); t = '\n'.join(L)
def set_cell(host, col, new):
    global t
    L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {host} |')]
    cells = L[i].split(' | '); cells[col] = new; L[i] = ' | '.join(cells); t = '\n'.join(L)
L = t.split('\n')
for rid in ('MC02', 'MA02', 'WM04', 'TR13', 'AH04', 'MI04', 'S06', 'TR04'):
    (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; del L[i]
t = '\n'.join(L)
# Lever and Pulley → Gearing
append('MC03', '⟨[+10]% Production when constructing [All] wonders [in all cities]⟩ — the crane lifts what the arm cannot: lever, pulley and gear together, as in Hellenistic mechanics (Lever and Pulley, merged here in v3.102).')
rep('| MC01 + MC02 |', '| MC01 + MA01 (Geometry) |')
rep('+ MC02 (Lever and Pulley — the beam)', '+ MC03 (Gearing — the lever and the beam)')
# Zero and Place Value → Geometry
append('MA01', '⟨[+1 Gold] from all [Market] buildings⟩ — place value keeps the market\'s accounts: arithmetic and geometry together, as in Babylon and Alexandria (Zero and Place Value, merged here in v3.102).')
rep('| MA02 |', '| MA01 (Geometry — place value) |')
rep('| MA02 + PH01 (Formal Logic) |', '| MA01 (Geometry — place value) + PH01 (Formal Logic) |')
rep('| MA02 + Tropical/jungle biome |', '| MA01 (Geometry — place value) + Tropical/jungle biome |')
rep('| SO11 (Banking) + MA02 (Zero and Place Value) |', '| SO11 (Banking) + MA01 (Geometry — place value) |')
# Flood Control → Aqueduct
append('WM02', '**Remove Marsh** (improvement; and the Dutch **Polder** is gated here); draining is one use of a bog — Turbary (F16) offers the other, cutting it for peat; ⟨[+1 Food] from [Flood plains] tiles [in all cities]⟩ — the river kept in its bed (Flood Control, merged here in v3.102: the two shared their prerequisites, and Roman hydraulic engineering did both).')
rep('| WM04 + CO11 (Reinforced Concrete) |', '| WM02 (Aqueduct — flood control) + CO11 (Reinforced Concrete) |')
rep('| Remove Marsh | Masonry | **WM04** |', '| Remove Marsh | Masonry | **WM02** |')
rep('| Polder | Guilds | **WM04** |', '| Polder | Guilds | **WM02** |')
rep('A bog can now be drained (Flood Control, WM04) or cut.', 'A bog can now be drained (the Aqueduct\'s flood control, WM02) or cut.')
# Postal System → Arch Construction
append('CO03', '**Post Office**ⁿ [55/1; +1 Gold; ⟨[+1 Gold] from each Trade Route⟩; ⟨[+25]% spy effectiveness [in this city]⟩ (`<when espionage is enabled>`)] — the post rides the roads: the Persian royal road, the Roman *cursus publicus* (Postal System, merged here in v3.102).')
# Selective Breeding: plants and animals, discoverable through Farming or Animal Husbandry
rep('| FA03 | **Selective Breeding (Plants)** |', '| FA03 | **Selective Breeding** |')
set_cell('FA03', 4, 'G02 + AH02 + (G07 or FA01 + FA02) — Seed Saving and Herd Animal Domestication; then Botanical Classification, or Irrigation with Crop Rotation')
append('FA03', '⟨[+1 Production] from [Pasture] tiles [in all cities]⟩ (wool, hide, horn); **War Dog**ⁿ [unit, Melee; cost 35; mv 3; str 7; ⟨Can move after attacking⟩] — the same idea applied to herds (Selective Breeding (Animals), merged here in v3.102). *Also discoverable through Animal Husbandry.*')
rep('*Also reachable in this focus (dual-path; home focus in parentheses): Vaccination (MD04, from Medicine).*', '*Also reachable in this focus (dual-path; home focus in parentheses): Vaccination (MD04, from Medicine); Selective Breeding (FA03, from Farming).*')
rep('| AH04 + O09 (Migratory Patterns) |', '| FA03 (Selective Breeding) + O09 (Migratory Patterns) |')
rep('| AH04 + MD01 (Surgical Techniques) |', '| FA03 (Selective Breeding) + MD01 (Surgical Techniques) |')
rep('| Dual-Path Breakthroughs | ~15 (discoverable through multiple Focus Areas) |', '| Dual-Path Breakthroughs | ~19 (discoverable through multiple Focus Areas) |')
# Sulphur Mining → Geological Observation
append('O08', '⟨[+1 Gold] from all [Dye Works] buildings⟩ (bleaching); ⟨[+1 Happiness] [in capital]⟩ (antiseptic, and matches that strike anywhere) — sulphur, gathered where the vents and springs bring it up (Sulfur Mining, merged here in v3.102). Knowledge, not a resource: sulfur was always the *available* half of gunpowder. Prerequisite for Advanced Pyrotechnics (F07) and Gunpowder (WA10).')
rep('| F07 (Pyrotechnics) + MI08 (Saltpeter) + MI04 (Sulfur) |', '| F07 (Pyrotechnics) + MI08 (Saltpeter) + O08 (Geological Observation — sulphur) |')
rep('| F03 + MI04 (Sulfur) |', '| F03 + O08 (Geological Observation — sulphur) |')
rep('| F03 (Charcoal Production — wood tar) + MI04 (Sulfur Mining) |', '| F03 (Charcoal Production — wood tar) + O08 (Geological Observation — sulphur) |')
# Megalithic Construction → Monumental Architecture
append('CU02', '⟨[-25]% Culture cost of natural border growth [in all cities]⟩ — the stones mark whose land this is. **Stonehenge**, **The Pyramids**, **Mausoleum of Halicarnassus** (world wonders) — the first monuments, and the first alignments with the sky (Megalithic Construction, merged here in v3.102).')
rep('| S06 (Megalithic Construction) + O01 + Isolated start or Coastal start |', '| CU02 (Monumental Architecture — the megaliths) + O01 + Isolated start or Coastal start |')
for w in ('Stonehenge | Calendar', 'The Pyramids | Masonry', 'Mausoleum of Halicarnassus | Masonry'):
    rep(f'| {w} | **S06** |', f'| {w} | **CU02** |')
# Maritime Trade → Sail Invention
append('SF03', '**Port**ⁿ [40/1; +1 Gold; ⟨[+1 Gold] from [Water resource] tiles [in this city]⟩; ⟨Must be next to [Coast]⟩] — the sea pays before it connects (over-water connection arrives with the Harbor, SF08); the Phoenicians traded as soon as they sailed (Maritime Trade, merged here in v3.102).')
rep('| Total Breakthroughs | ~522 |', '| Total Breakthroughs | ~514 |')
rep('| CORE Breakthroughs | ~150 |', '| CORE Breakthroughs | ~147 |')
rep('| STANDARD Breakthroughs | ~220 |', '| STANDARD Breakthroughs | ~215 |')
rep('Complete Tech Tree Design Document (v3.101)', 'Complete Tech Tree Design Document (v3.102)')
open(p, 'w', encoding='utf-8').write(t); print('batch 4 applied')
