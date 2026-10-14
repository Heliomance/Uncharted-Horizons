"""Thinning batch 7: middle-era skeleton merges, and a prerequisite notation that never relies on operator precedence."""
import re, sys
sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power'); import prereq as PQ
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read()
def rep(old, new):
    global t; assert t.count(old) == 1, (old[:80], t.count(old)); t = t.replace(old, new)
def rows_of(text):
    return {l.split(' | ')[0][2:]: l for l in text.split('\n') if re.match(r'^\| [A-Z][A-Z0-9-]* \| \*\*', l)}
def cell_get(rid, col): return rows_of(t)[rid].split(' | ')[col]
def cell_set(rid, col, new):
    global t
    L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]
    cells = L[i].split(' | '); cells[col] = new; L[i] = ' | '.join(cells); t = '\n'.join(L)
def append(host, text): cell_set(host, 5, cell_get(host, 5).rstrip() + ' ' + text)
def repoint(src, host, label):
    """in every prerequisite cell naming src: drop it if host is already there, else write host in its place"""
    for rid in list(rows_of(t)):
        pre = cell_get(rid, 4)
        if not re.search(rf'\b{src}\b', pre) or rid == src: continue
        tok = rf'{src}(?: \([^()]*\))?'
        if re.search(rf'\b{host}\b', pre):
            new = re.sub(rf'\s*\+\s*{tok}', '', pre, count=1)
            if new == pre: new = re.sub(rf'{tok}\s*\+\s*', '', pre, count=1)
        else:
            new = re.sub(rf'\b{tok}', f'{host} ({label})', pre, count=1)
        assert new != pre, (rid, src); cell_set(rid, 4, new)
before = {k: PQ.parse(l.split(' | ')[4], None) for k, l in rows_of(t).items()}
L = t.split('\n')
for rid in ('MA04', 'PH03', 'CH02', 'SF18', 'TR18', 'EL01', 'OP04', 'SO15'):
    (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; del L[i]
t = '\n'.join(L)
# Trigonometry → Basic Algebra
append('MA03', '⟨[+10]% Strength <for [Siege] units>⟩ (artillery by angle); ⟨[+1 Culture] from all [World Wonder] buildings⟩ (proportion in stone) — algebra and trigonometry, the mathematics of Alexandria and Baghdad (Trigonometry, merged here in v3.105).')
repoint('MA04', 'MA03', 'Basic Algebra — trigonometry')
# Epistemology → Formal Logic
append('PH01', '⟨[+1 Science] from every specialist [in all cities]⟩; ⟨[-25]% enemy spy effectiveness [in all cities]⟩ (`<when espionage is enabled>`) — scepticism as defence: Aristotle\'s logic and his account of knowledge (Epistemology, merged here in v3.105).')
repoint('PH03', 'PH01', 'Formal Logic — epistemology')
rep('a civilisation that knows Writing, Epistemology and the Printing Press', 'a civilisation that knows Writing, Formal Logic and the Printing Press')
# Acid/Base Discovery → Distillation
append('CH04', '⟨[+1 Production] from [Mine] tiles [in all cities]⟩ (acid leaching — the canonical Chemistry mine bonus): the mineral acids were themselves products of distillation — vitriol distilled into oil of vitriol, saltpetre and alum into *aqua fortis* (Acid/Base Discovery, merged here in v3.105). Discoverable through alchemy or through iron-working practice. Prerequisite for Electricity (EL02).')
cell_set('CH04', 4, 'CH01 or (F03 + ME04) — Alchemy, or Charcoal with Iron Smelting')
repoint('CH02', 'CH04', 'Distillation — acids')
rep('*Available from: O06 (Natural Philosophy) + CH02 (Acid/Base Discovery)*', '*Available from: O06 (Natural Philosophy) + CH04 (Distillation — acids)*')
rep('*reveals* Acid/Base Discovery (CH02) and Distillation (CH04) as concepts centuries early.', '*reveals* Distillation (CH04), and the acids it yields, as a concept centuries early.')
# Sternpost Rudder → Caravel
append('SF09', '**Galleass** (unit) — a hinged rudder on the centreline steers a far larger hull: the rudder made the great hulls possible (Sternpost Rudder, merged here in v3.105).')
cell_set('SF09', 4, 'SF08 + SF05 (Trireme/Galley) + ME04 (Iron Smelting)')
rep('| Galleass | Compass | **SF18** |', '| Galleass | Compass | **SF09** |')
# Double-Entry Bookkeeping → Banking
append('SO11', '**National Treasury** (national wonder) — every debit matched by a credit: the Medici kept double-entry books (Double-Entry Bookkeeping, merged here in v3.105).')
rep('| National Treasury | Guilds | **TR18** |', '| National Treasury | Guilds | **SO11** |')
# Static Electricity → Voltaic Pile
append('EL02', '⟨[+1 Culture] from all [Museum] buildings⟩ — galvanic demonstrations draw the crowds: Galvani\'s frogs and Volta\'s pile were one line of experiment (Static Electricity, merged here in v3.105). Foundation of electrical science.')
cell_set('EL02', 4, 'O06 (Natural Philosophy) + CH04 (Distillation — acids) + ME01')
rep('*reveals* Static Electricity (EL01) as a concept a millennium early.', '*reveals* the Voltaic Pile (EL02) as a concept a millennium early.')
# Microscope → Telescope
append('OP03', '⟨[-25]% enemy spy effectiveness [in all cities]⟩ (`<when espionage is enabled>` — forensics): the same lens-makers made both, Janssen around 1590 (Microscope, merged here in v3.105). Unlocks the Germ Theory path (MD05).')
repoint('OP04', 'OP03', 'Telescope — the microscope')
# Nation-State → Public Education
append('SO16', '**Constabulary** and **Police Station** (both `<when espionage is enabled>`) — the state that polices its own territory; ⟨[+2] Unit Supply per city⟩ — the nation in arms, fed from cans: Napoleon offered the prize that Appert won in 1810. The nineteenth-century state schooled and conscripted together (Nation-State, merged here in v3.105, with Tinplate/Canning merged into it in v3.100).')
rep('| Constabulary | Banking | **SO15** |', '| Constabulary | Banking | **SO16** |')
rep('| Police Station | Electricity | **SO15** |', '| Police Station | Electricity | **SO16** |')
# ---- notation: no prerequisite relies on which operator binds tighter ----
explicit = {
    'FA03': ('(G07 or FA01 + FA02)', '(G07 or (FA01 + FA02))'),
    'MC09': ('(MI07 + CH09 or CH04 + CH07)', '((MI07 + CH09) or (CH04 + CH07))'),
    'EN06': ('(EN02 Transistor + CH11 Polymer, or QM-E03 Resonant-State Computing)', '((EN02 Transistor + CH11 Polymer) or QM-E03 Resonant-State Computing)'),
    'CP10': ('(QP07 + CP01 or GN10)', '((QP07 + CP01) or GN10)'),
    'AE11': ('AE03 + EL12 (Room Temp Superconductor) or EL02 (Voltaic Pile — batteries) + EN10 (Miniaturization)', 'AE03 + (EL12 (Room Temp Superconductor) or (EL02 (Voltaic Pile — batteries) + EN10 (Miniaturization)))'),
}
for rid, (old, new) in explicit.items():
    pre = cell_get(rid, 4); assert pre.count(old) == 1, rid; cell_set(rid, 4, pre.replace(old, new))
def wrap_or_groups(pre):
    """parenthesise every top-level OR group that names a row, in a cell that also uses '+'"""
    # keep any trailing commentary after a dash outside parentheses
    head, tail = pre, ''
    for i, ch, d in PQ._depth0(pre):
        if d == 0 and pre.startswith(' — ', i): head, tail = pre[:i], pre[i:]; break
    terms = PQ._split(head, ['+'])
    if len(terms) < 2: return pre
    out = []
    for term in terms:
        tt = term.strip()
        has_ids = re.search(PQ.IDRX, PQ._strip_descriptions(tt))
        if re.search(r'\bor\b', PQ._strip_descriptions(tt)) and has_ids and not (tt.startswith('(') and tt.endswith(')')) and not re.match(r'[A-Z_]+ (token )?\(', tt):
            tt = f'({tt})'
        out.append(tt)
    return ' + '.join(out) + tail
for rid in list(rows_of(t)):
    pre = cell_get(rid, 4); new = wrap_or_groups(pre)
    if new != pre: cell_set(rid, 4, new)
# the notation, in §7
old_note = t[t.index('**Notation in the Prerequisites column.**'):]
old_note = old_note[:old_note.index('\n')]
rep(old_note, '**Notation in the Prerequisites column.** Row IDs joined by "+" are all required; "or" offers alternatives. A cell never relies on which of the two binds tighter: whenever it uses both, each group of alternatives is in parentheses — "WA10 + (ME05 or ME08)" — and so is each alternative that needs several rows — "G02 + (G07 or (FA01 + FA02))", "CH01 or (F03 + ME04)". Inside a group, commas also separate the alternatives ("(NP03 Fission, or QM-E02 Bound-Energy Release)"). A parenthesis whose content begins with a row ID is a group; any other parenthesis is a description — "(Kiln Construction)", "(but NOT SO04)" — and so is commentary after a dash outside every parenthesis. Plain text with no ID, such as "Coastal location" or "Temperate or Tropical biome", is an environmental condition. The battery, the generator and the derivation all read prerequisites through one parser (check 18), and check 19 holds every cell to this notation.')
rep('| Total Breakthroughs | ~501 |', '| Total Breakthroughs | ~493 |')
rep('| CORE Breakthroughs | ~142 |', '| CORE Breakthroughs | ~137 |')
rep('| STANDARD Breakthroughs | ~207 |', '| STANDARD Breakthroughs | ~204 |')
rep('Complete Tech Tree Design Document (v3.104)', 'Complete Tech Tree Design Document (v3.105)')
open(p, 'w', encoding='utf-8').write(t)
# ---- the parsed meaning must not change, except where it was meant to ----
after = {k: PQ.parse(l.split(' | ')[4], None) for k, l in rows_of(t).items()}
norm = lambda x: sorted(sorted(sorted(o) for o in g) for g in x)
changed = sorted(k for k in after if k in before and norm(after[k]) != norm(before[k]))
print('batch 7 applied; rows whose parsed prerequisites changed:', changed)
