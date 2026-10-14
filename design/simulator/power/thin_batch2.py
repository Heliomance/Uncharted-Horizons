"""Thinning batch 2: Warfare, Construction, Philosophy and the Arts, Metallurgy, Observation — twelve rows merged."""
import re
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read()
def rep(old, new):
    global t; assert t.count(old) == 1, (old[:80], t.count(old)); t = t.replace(old, new)
def cell(rid, col):
    l = [x for x in t.split('\n') if x.startswith(f'| {rid} |')][0]; return [x.strip() for x in l.split('|')[1:-1]][col]
def spec(rid, name):
    u = cell(rid, 5); i = u.index(f'**{name}**ⁿ ['); d = 0
    for j in range(i + len(name) + 5, len(u)):
        d += u[j] == '['; d -= u[j] == ']'
        if d == 0: return u[i:j + 1]
moved_lab = spec('PH07', 'Experimental Laboratory')
L = t.split('\n')
for rid in ('WA02', 'WA15', 'CO16', 'CO12', 'PH13', 'CU16', 'PH07', 'CU08', 'ME10', 'ME11', 'O11', 'O17'):
    (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; del L[i]
t = '\n'.join(L)
# Warfare
rep('**Cavalry** (unit) — needing no gunpowder, so cavalry keeps its long relevance in gunpowder-less worlds.',
    '**Cavalry** and **Lancer** (units) — needing no gunpowder, so cavalry keeps its long relevance in gunpowder-less worlds; ⟨[+25]% Strength <for [Gunpowder] units> <vs [Mounted] units>⟩ — pike and shot in one formation (Pike and Shot, merged here in v3.100).')
rep('| Lancer | Metallurgy | **WA15** |', '| Lancer | Metallurgy | **WA28** |')
# Construction
rep('⟨Roads connect tiles across rivers⟩ (the canonical Engineering unique — bridges);',
    '**Road** (improvement — Road Building, merged here in v3.100: roads and their bridges together); ⟨Roads connect tiles across rivers⟩ (the canonical Engineering unique — bridges);')
for row_old in ('MC08 (Steam Engine) + CO16 (Road Building) + ME08 (Blast Furnace)', 'CO16 (Road Building) + CU02 (Monumental Architecture)', 'SO04 + CO16 (Road Building)'):
    rep(row_old, row_old.replace('CO16 (Road Building)', 'CO03 (Arch Construction — roads)'))
rep('| Road | The Wheel | **CO16** |', '| Road | The Wheel | **CO03** |')
rep('**Machine Gun** (unit) — the line moves, the workers stand.',
    '**Machine Gun** (unit) — the line moves, the workers stand; ⟨[+15]% Production when constructing [All] buildings [in all cities]⟩; ⟨[+25]% Production when constructing [Military Base] buildings [in all cities]⟩ — buildings made on the line, too: forward bases in weeks (Prefabrication, merged here in v3.100).')
rep('| CO12 + CP01 (Computer) + MS01 (Composites) |', '| MC11 (Assembly Line — prefabrication) + CP01 (Computer) + MS01 (Composites) |')
# Philosophy and the Arts
rep('**Angkor Wat** (world wonder). (Oxford University moves to the Translation Movement, PH13; the theology wonders to Scholastic Theology, CU15.)',
    '**Angkor Wat** (world wonder); **Oxford University** (national wonder — a great seat of learning, built on recovered knowledge: the Translation Movement, merged here in v3.100). (The theology wonders are Scholastic Theology\'s, CU15.)')
rep('| Oxford University | Education | **PH13** |', '| Oxford University | Education | **CU06** |')
rep('**Hermitage** (national wonder).',
    '**Hermitage** (national wonder); **Opera House** (and the Celtic **Ceilidh Hall**); **Theatre**; **Sistine Chapel** (world wonder) — music and drama for a paying public: opera began in Renaissance Florence, and the Sistine ceiling dates from 1512 (Opera, merged here in v3.100).')
rep('belong to Opera, CU16.)', 'belong to the Renaissance, CU07.)')
for w in ('Sistine Chapel | Acoustics', 'Opera House | Acoustics', 'Ceilidh Hall | Acoustics', 'Theatre | Printing Press'):
    rep(f'| {w} | **CU16** |', f'| {w} | **CU07** |')
rep('**Experiment** ability (our system: spend Gold to boost one Revealed breakthrough\'s roll). Game-changing.',
    '**Experiment** ability (our system: spend Gold to boost one Revealed breakthrough\'s roll). Game-changing. ' + moved_lab + ' — the experiment as institution (Empiricism, merged here in v3.100: Bacon\'s empiricism was the method).')
rep('⟨[+2 Gold] from all [Broadcast Tower] buildings⟩ — advertising revenue.',
    '⟨[+2 Gold] from all [Broadcast Tower] buildings⟩ — advertising revenue; **Sydney Opera House**, **CN Tower** (world wonders); ⟨Resting point for Influence with City-States is increased by [10]⟩ — soft power, broadcast (Mass Media, merged here in v3.100).')
rep('| Sydney Opera House | Ecology | **CU08** |', '| Sydney Opera House | Ecology | **EN05** |')
rep('| CN Tower | Telecommunications | **CU08** |', '| CN Tower | Telecommunications | **EN05** |')
# Metallurgy
rep('**Pikeman** (unit).', '**Pikeman** (unit); ⟨[+1 Gold] from [Iron] tiles [in all cities]⟩ — pots, pans and pipes (Cast Iron, merged here in v3.100: China cast iron and made steel from it in the same centuries).')
rep('Glassmaking (OP01), Cast Iron (ME10) and Geopolymer Concrete (S09)', 'Glassmaking (OP01) and Geopolymer Concrete (S09)')
rep('| WA10 (Gunpowder) + ME10 (Cast Iron) or ME08 (Blast Furnace) |', '| WA10 (Gunpowder) + ME05 (Steel Production — cast iron) or ME08 (Blast Furnace) |')
rep('(ME02 or ME10 — bronze or cast iron for the cylinder)', '(ME02 or ME05 — bronze or cast iron for the cylinder)')
rep('**Constabulary** and **Police Station** (both `<when espionage is enabled>`) — the state that polices its own territory.',
    '**Constabulary** and **Police Station** (both `<when espionage is enabled>`) — the state that polices its own territory; ⟨[+2] Unit Supply per city⟩ — the nation in arms, fed from cans: Napoleon offered the prize that Appert won in 1810 (Tinplate/Canning, merged here in v3.100).')
# Observation
rep('⟨[+1 Production] from [Quarry] tiles [in all cities]⟩.',
    '⟨[+1 Production] from [Quarry] tiles [in all cities]⟩; ⟨[+1 Production] from [Iron] tiles [in all cities]⟩ (magnetic ore sorting); ⟨[+1 Culture] [in capital]⟩ — the lodestone, a geological curiosity (Magnetism Discovery, merged here in v3.100). Prerequisite for the Compass (SF08).')
rep('| O11 (Magnetism) + SF04 |', '| O08 (Geological Observation — the lodestone) + SF04 |')
# tallies and version
rep('| Total Breakthroughs | ~545 |', '| Total Breakthroughs | ~533 |')
rep('| CORE Breakthroughs | ~152 |', '| CORE Breakthroughs | ~150 |')
rep('| STANDARD Breakthroughs | ~241 |', '| STANDARD Breakthroughs | ~231 |')
rep('Complete Tech Tree Design Document (v3.99)', 'Complete Tech Tree Design Document (v3.100)')
open(p, 'w', encoding='utf-8').write(t); print('batch 2 applied')
