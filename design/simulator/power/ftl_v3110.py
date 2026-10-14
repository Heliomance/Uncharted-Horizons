"""v3.110 — FTL re-audit, part 1: structure and era parity, grounded in Elemental Physics Models I and II."""
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global t; assert t.count(old) == n, (old[:90], t.count(old)); t = t.replace(old, new)
def cells(rid):
    L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; return L, i, L[i].split(' | ')
def set_cell(rid, col, new):
    global t
    L, i, c = cells(rid); c[col] = new; L[i] = ' | '.join(c); t = '\n'.join(L)
def append(rid, text):
    L, i, c = cells(rid); set_cell(rid, 5, c[5].rstrip() + ' ' + text)
# 1. Plenum Gravitation: the elemental mirror of Quantum Gravity
L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith('| QM-E26 |')]
L.insert(i + 1, '| QM-E27 | **Plenum Gravitation** | CORE | Space | QM-E04 (Unified Field) + RC02 (General Relativity) | '
 '⟨Reveal up to [all] [Strategic resource] within a [20] tile radius⟩ (a Triggerable on discovery — gravitational mapping: a dense body betrays itself by what it does to the medium); '
 'the critical node for the elemental Warp, Wormhole, Hyperspace and Plenum Drive, and the elemental reading of Closed Timelike Curves, Dark Energy and the Gravitational Coupling Experiment; '
 'fires the "the medium is more malleable than expected" report. '
 '*Substance:* "Rarefaction Mechanics" — bulk substance rarefies the Aether around it, and substance drifts toward rarer Aether (Model I, axiom 5): gravity as a theory of the Aether\'s density, so an ore body shows itself by the Aether it thins. '
 '*Process:* "Mechanics of the Inward Draw" — the world is a vast eddy whose Earth-movement draws every pattern inward (Model II, §2): gravity as a theory of the flow, so a heavy pattern shows itself by the draw it adds. '
 'The mirror of Quantum Gravity Theory (QP08), as Unified Field Theory (QM-E04) is of Quantum Field Theory. | '
 'Gravity read through the plenum: the density gradients that do curvature\'s work (see the Relativity & Cosmology note). |')
t = '\n'.join(L)
# 2. the elemental FTL rows that mirror Quantum Gravity's dependents now follow it
set_cell('QM-E06', 4, 'QM-E27 (Plenum Gravitation) + (CH21 or CH23)')
set_cell('QM-E12', 4, 'QM-E27 (Plenum Gravitation) + MA13 (Topology)')
set_cell('QM-E19', 4, 'QM-E27 (Plenum Gravitation) + RK05 (Satellite Technology)')
set_cell('RC08', 4, '(QP08 Quantum Gravity, or QM-E27 Plenum Gravitation) + (QP04 Particle Accelerator, or QM-E08 Grand Athanor)')
rep('The mirror of Quantum Field Theory and Quantum Gravity (QP05/QP08).', 'The mirror of Quantum Field Theory (QP05); Quantum Gravity\'s mirror is Plenum Gravitation (QM-E27).')
# 3. the four rows that stood only in atomic worlds, each given its elemental account
set_cell('RC04', 4, 'RC02 + (QP05 or QM-E04) + TH01')
append('RC04', '*Elemental:* the **dark star** — a body dense enough to rarefy the Aether so deeply that light, a tension-wave in it, cannot climb out, its rim glowing at the Aether\'s limiting fineness (Substance; Model I, axiom 5 and §5); '
 'or an eddy whose inward draw no Fire-movement can escape, its rim at the flow\'s fastest rhythm (Process; Model II, §2 and §5). Michell\'s dark star of 1783, read through Lorentzian aether-mechanics; the report speaks of a fold in the medium a vessel might pass.')
set_cell('RC06', 4, 'RC05 + (QP08 or QM-E27)')
append('RC06', '*Elemental:* the same accelerating expansion, read as the Aether\'s own tension at the scale of the heavens (Substance) or as yang\'s outward flow set against the world-eddy\'s inward draw (Process) — the observation is shared by every world; only its account differs.')
set_cell('RC07', 4, 'RC02 + (QP08 or QM-E27)')
append('RC07', '*Elemental:* **closed circuits of the medium** — the Aether\'s natural motion is the circle, and a fold lets a circuit close upon itself (Substance; Model I, axiom 4); loops of the flow that return to their own beginning across a fold (Process). '
 'Where the medium gives a preferred frame these are closed paths in space, not in time — and still the geometry of a stable throat.')
set_cell('MS08', 4, '(QP11 Exotic Matter Synthesis, or QM-E06 Exotic Matter) + MS02')
rep('Reads Exotic Matter Synthesis as EXOTIC_MATTER, so the elemental Exotic Matter Forge (QM-E06) satisfies it.',
    '*Elemental:* the same practical fabrication, of exotic Aether made in quantity — Aether held heavier or lighter than its rest density (Substance; Model I, §7) — or of broken-cycle matter held past its own closure (Process; Model II, §7).')
rep('nodes needing the deep account read the malleable-space primitive (QM-E04 elemental, QP08 atomic)',
    'nodes needing the deep account read the malleable-space primitive (QM-E27 elemental, QP08 atomic). Black Hole Thermodynamics, Dark Energy and Closed Timelike Curves each carry an elemental account — the dark star, the medium\'s tension at cosmic scale, closed circuits of the medium')
# 4. §4: the capability table, Method F, and the prerequisite lists both ontologies use
rep('| Malleable space | spacetime geometry (QP08 + RC02) | a dynamic, sculptable plenum (QM-E04) | Warp, Wormhole |',
    '| Malleable space | spacetime geometry (QP08 + RC02) | the plenum\'s gravitation — the Aether\'s rarefaction, or the world-eddy\'s inward draw (QM-E27 + RC02) | Warp, Wormhole, Hyperspace; Plenum |')
rep('| Exotic matter | negative-energy matter (QP11) | aether made heavy/light; broken-cycle matter (QM-E06) | Warp, Wormhole |',
    '| Exotic matter | negative-energy matter (QP11), fabricated (MS08) | Aether made heavy or light; broken-cycle matter (QM-E06), fabricated (MS08) | Warp, Wormhole |\n'
    '| Traversable geometry | black-hole horizons and closed timelike curves (RC04, RC07) | the dark star and closed circuits of the medium (RC04, RC07, read through Lorentzian aether-mechanics) | Wormhole |')
rep('| Deep high-energy theory | QP05 | HIGH_ENERGY_PHYSICS token (QM-E01) | shared prereq |',
    '| Deep high-energy theory | QP05 | Unified Field Theory (QM-E04), which grants HIGH_ENERGY_PHYSICS | Tachyonic; shared prereq |')
rep('- Requires: QM-E04 (Unified Field — Aetheric/Great-Harmony) + QM-E06', '- Requires: QM-E27 (Plenum Gravitation — the medium\'s gravitation) + QM-E06')
table = '''
**Prerequisites by ontology.** The rows each method needs, as the SS FTL Drive's derivation (§7.0) reads them — one condition per row, for the single method this world permits. A method's elemental column takes each atomic row's mirror where the row is atomic-only, and the row itself where it stands in both kinds of world.

| Method | Atomic worlds | Elemental worlds |
|---|---|---|
| A Warp | RC02, QP08, QP11, MS08; energy: ES08, ES06, ES12 or ES14 | RC02, QM-E27, QM-E06, MS08; energy: QM-E05 or ES15 |
| B Wormhole | RC02, QP08, QP11, RC04, RC07, MS08, QP12, MA13 | RC02, QM-E27, QM-E06, RC04, RC07, MS08, QM-E13, MA13 |
| C Hyperspace | QP09, QP08, MA13; energy: ES08, ES06, ES12 or ES14 | QM-E12, QM-E27, MA13; energy: QM-E05 or ES15 |
| D Tunnelling | QP02, CP10, MS02, and QP07 or GN10 | — (atomic worlds only) |
| E Tachyonic | RC01, RC03, QP05, QP06, QP04 | RC01, RC03, QM-E04, QM-E17, QM-E08 |
| F Plenum | — (elemental worlds only) | QM-E27, QM-E06, QM-E19; energy: QM-E05 or ES15 |

'''
rep('\n### FTL in Elemental Worlds', table + '### FTL in Elemental Worlds')
# 5. the Quintessic note: the new mirror, the FTL routes, and a stale mention of a removed row
rep('the Complete Catalogue (QM-E17) for the Standard Model,', 'the Complete Catalogue (QM-E17) for the Standard Model, Plenum Gravitation (QM-E27) for Quantum Gravity,')
rep('the Celestial Current Survey (QM-E19), the Medium Reservoir (QM-E22) and the Current Sail (QM-E23)', 'the Celestial Current Survey (QM-E19) and the Current Sail (QM-E23)')
rep('Supernal Spheres (QM-E12) and Aetheric Vacuum (QM-E13) carry the elemental routes to the FTL frontier (see §4).',
    'Plenum Gravitation (QM-E27) carries the elemental routes to the FTL frontier, with Exotic Matter (QM-E06), Supernal Spheres (QM-E12), the Aetheric Vacuum (QM-E13) and the Celestial Current Survey (QM-E19) (see §4).')
rep('| Total Breakthroughs | ~493 |', '| Total Breakthroughs | ~494 |')
rep('| CORE Breakthroughs | ~137 |', '| CORE Breakthroughs | ~138 |')
rep('Complete Tech Tree Design Document (v3.109)', 'Complete Tech Tree Design Document (v3.110)')
open(p, 'w', encoding='utf-8').write(t); print('v3.110 edits applied')
