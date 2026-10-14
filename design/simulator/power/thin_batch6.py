"""Thinning batch 6: Atomic-era skeleton merges — five rows into their natural partners."""
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read()
def rep(old, new):
    global t; assert t.count(old) == 1, (old[:80], t.count(old)); t = t.replace(old, new)
def append(host, text):
    global t
    L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {host} |')]
    cells = L[i].split(' | '); cells[5] = cells[5].rstrip() + ' ' + text; L[i] = ' | '.join(cells); t = '\n'.join(L)
def set_pre(host, new):
    global t
    L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {host} |')]
    cells = L[i].split(' | '); cells[4] = new; L[i] = ' | '.join(cells); t = '\n'.join(L)
L = t.split('\n')
for rid in ('CP02', 'CP03', 'CP05', 'FA12', 'TX09'):
    (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; del L[i]
t = '\n'.join(L)
# Operating System → Programmable Computer
append('CP01', '⟨[+1 Science] per [4] population [in all cities]⟩ — digital administration turns a populace into knowledge: a computer and the system that makes it usable (Operating System, merged here in v3.104). All later Computing breakthroughs build on this.')
set_pre('CP06', 'CP01 + MA13 (Topology — set theory)')
set_pre('CP07', 'CP01 + MA09 (Statistics)')
set_pre('CP10', '(QP07 + CP01 or GN10) — Entanglement Mastery with the Programmable Computer, or Bio-Quantum Coherence')
set_pre('GN08', 'GN03 + CP01 (Programmable Computer)')
# Networking and Database Systems → Internet
append('CP04', '⟨[+1 Science] [in all cities connected to capital]⟩ — the network follows the roads; ⟨[+1 Gold] from all [Stock Exchange] buildings⟩ — prices move at the speed of light, on fibre (Networking, merged here in v3.104, with Fiber Optics merged into it in v3.101). **Database Centre**ⁿ [625/3; +3 Gold; ⟨[+1 Gold] from each Trade Route⟩; ⟨[+25]% spy effectiveness [in this city]⟩ (`<when espionage is enabled>`)] — the networked age keeps its records in data centres (Database Systems, merged here in v3.104).')
set_pre('CP04', 'CP01 + EL09 (Wireless) or EL04 (Telegraph)')
rep('Prerequisite for Radio (EN11) and Networking (CP03).', 'Prerequisite for Radio (EN11) and the Internet (CP04).')
# Genetic Crop Engineering → Genetic Engineering
append('GN03', '⟨[+15]% growth [in all cities]⟩ — engineered crops that never fail (Genetic Crop Engineering, merged here in v3.104: the two were one idea).')
set_pre('GN03', 'GN02 + CP01 (Computer) + FA03 (Selective Breeding)')
# Kevlar → Carbon Fiber
append('TX08', '⟨All newly-trained [Land] units [in all cities] receive the [Flak Jacket] promotion⟩ (**Flak Jacket**ⁿ: ⟨[+15]% Strength <when defending> <vs [Ranged] units>⟩) — two engineered fibres of the same years (Kevlar/Armor Textiles, merged here in v3.104).')
set_pre('TX08', 'CH07 + CH11 (Polymer Science)')
rep('| Total Breakthroughs | ~506 |', '| Total Breakthroughs | ~501 |')
rep('| CORE Breakthroughs | ~144 |', '| CORE Breakthroughs | ~142 |')
rep('| STANDARD Breakthroughs | ~210 |', '| STANDARD Breakthroughs | ~207 |')
rep('Complete Tech Tree Design Document (v3.103)', 'Complete Tech Tree Design Document (v3.104)')
open(p, 'w', encoding='utf-8').write(t); print('batch 6 applied')
