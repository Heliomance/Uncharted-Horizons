"""v3.112, stage 4: the new §4. New sections from wip/s4_v112_head.md; 'FTL in Elemental Worlds' and 'How the Victories Are Built'
are kept from v3.111 with their corrections. Also fixes the old method letters outside §4 (changelog entries are history and stay)."""
import re
P = '/home/user/Uncharted-Horizons/design/simulator/outputs/wip/tt_v112_wip.md'
L = open(P, encoding='utf-8').read().split('\n')
a = [i for i, l in enumerate(L) if l.startswith('## 4. ENDGAME')][0]
b = [i for i, l in enumerate(L) if re.match(r'^## 5\b', l)][0]
old = '\n'.join(L[a:b])
el = old.index('### FTL in Elemental Worlds'); vi = old.index('### How the Victories Are Built')
elem, vict = old[el:vi], old[vi:]
def rep(s, a_, b_, n=1):
    assert s.count(a_) == n, (a_[:70], s.count(a_)); return s.replace(a_, b_)
# --- FTL in Elemental Worlds ---
elem = rep(elem, '(Quantum Tunneling, D)', '(Quantum Tunnelling)')
elem = rep(elem, '(Plenum Drive, F)', '(the Plenum Drive)')
elem = rep(elem, '(D atomic / F elemental)', '(Tunnelling in atomic worlds, Plenum in elemental ones)')
elem = rep(elem, 'D and F are not an awkward asymmetry', 'Tunnelling and Plenum are not an awkward asymmetry')
elem = re.sub(r'\| Superluminal matter \|[^\n]*\n', '| Superluminal matter | a tachyonic sector in the Standard Model (QP06), and dark energy as a tachyonic field (RC06) | a superluminal form in the complete catalogue (QM-E17), and a superluminal mode of the medium (RC06) | Tachyonic (the medium\'s mode also Plenum) |\n', elem, count=1)
elem = re.sub(r'\| Endgame energy \|[^\n]*\n', '| Endgame power (W9) | ES14 Advanced Fission or ES08 Fusion Reactor | QM-E05 Re-Tempering / Self-Feeding Cycle Reactor | Warp, Hyperspace, Tachyonic |\n', elem, count=1)
elem = rep(elem, 'Tachyonic still centres on the deep-matter big instrument (the Boundary Furnace, mirror to the atomic particle accelerator)',
           'Tachyonic still centres on cosmology and a converter ring (NP15, or its mirror TH20 in elemental worlds)')
elem = re.sub(r'see \*The Evidence Map\* above, which gives every deciding row\'s report in both ontologies\.',
              'see *Conditions and Their Tests* above, which gives every condition in both ontologies.', elem, count=1)
elem = re.sub(r' The Boundary Furnace remains an alternative carrier of the tachyonic signal where the interferometer route isn\'t taken\.', '', elem, count=1)
assert 'Evidence Map' not in elem and ', D)' not in elem
# --- How the Victories Are Built ---
vict, n = re.subn(r'whose further requirements are written at world creation.*?in one native countable\.',
    'whose one further requirement is written at world creation by the World-Truth ruleset derivation (§7.0): `Only available <when number of [Researched [P] Technologies] is more than [0]>`, '
    'where P is the prototype of the single method this world permits (§4, *The Prototype and the Hail Mary*) — so no failed prototype can satisfy it, and the puzzle this section describes is settled in one native countable.', vict, flags=re.S)
assert n == 1
vict = rep(vict, '- **Generation Ship Victory — the challenge.**',
           '- **Announcements.** Completing the prototype and the SS FTL Drive is announced to every civilisation, as base Civ V announces spaceship parts; committing to a prototype stays private.\n- **Generation Ship Victory — the challenge.**')
vict = rep(vict, 'Guarantee Rule 2 holds through the FTL Drive (the viable method\'s prerequisites are CORE or STANDARD)',
           'Guarantee Rule 2 holds through the FTL Drive (the viable method\'s build and prove rows are CORE or STANDARD, and its prototype is a Grand Endeavour)')
head = open('/home/user/Uncharted-Horizons/design/simulator/outputs/wip/s4_v112_head.md', encoding='utf-8').read().rstrip('\n') + '\n\n'
new = (head + elem.rstrip('\n') + '\n\n' + vict.rstrip('\n')).split('\n')
if new[-1].strip() != '---': new += ['', '---']
L[a:b] = new + ['']
# --- the old method letters outside §4 (not in the changelog) ---
fixes = 0
for i, l in enumerate(L):
    if l.startswith('### v3.') or l.startswith('*Version') or l.startswith('- **D/F') or l.startswith('- **Confirmed and logged'): continue
    l2 = l.replace('Method D (Quantum Tunnelling)', 'Tunnelling').replace('Method F (Plenum Drive)', 'the Plenum Drive') \
          .replace('Method D is atomic-only and F elemental-only', 'Tunnelling is atomic-only and Plenum elemental-only')
    if l2 != l: L[i] = l2; fixes += 1
open(P, 'w', encoding='utf-8').write('\n'.join(L))
s4 = [l for l in L[a:a + len(new)] if l.startswith('##')]
print('stage 4 written; §4 headings:', [h[:60] for h in s4]); print('method-letter lines fixed outside §4:', fixes)
