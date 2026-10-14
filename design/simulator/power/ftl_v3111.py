"""v3.111 — FTL re-audit, part 2: the evidence map, a scientific register for elemental names, the Aether Tension Engine,
Plenum's sail, and gravitic engineering without exotic matter. Grounded in Elemental Physics, Models I and II."""
import re
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read()
cl = t.index('## Changelog'); body, log = t[:cl], t[cl:]
def rep(old, new, n=1):
    global body; assert body.count(old) == n, (old[:90], body.count(old)); body = body.replace(old, new)
# ---- renames, line by line, leaving the version footers as history ----
RENAMES = [('Grand Athanor / Great Observatory', 'Boundary Furnace / Cycle-Limit Observatory'), ('Grand Athanor', 'Boundary Furnace'),
           ('Great Observatory of Cycles', 'Cycle-Limit Observatory'), ('Great Work Reactor', 'Re-Tempering Reactor'), ('Perpetual Cycle', 'Self-Feeding Cycle'),
           ('Transcendent Engine', 'Aether Tension Engine'), ('Compact Athanor (Compact Wheel)', 'Compact Re-Tempering Reactor (Compact Cycle Reactor)'),
           ('Compact Athanor', 'Compact Re-Tempering Reactor'), ('"Compact Wheel"', '"Compact Cycle Reactor"'),
           ('Supernal Spheres (Higher Realms)', 'Higher Strata Theory'), ('Supernal Spheres (QM-E12)', 'Higher Strata Theory (QM-E12)'),
           ('Great Harmony (The Great Wheel)', 'Full-Cycle Coupling (The Great Wheel)'), ('Great Harmony (QM-E11)', 'Full-Cycle Coupling (QM-E11)'),
           ('"Great Harmony Theory"', '"Flow Field Theory"')]
L = body.split('\n'); counts = {a: 0 for a, b in RENAMES}
for i, l in enumerate(L):
    if l.startswith('*Version'): continue
    for a, b in RENAMES:
        if a in l: counts[a] += l.count(a); l = l.replace(a, b)
    L[i] = l
body = '\n'.join(L); print('renamed:', {k: v for k, v in counts.items() if v})
def cells(rid):
    L = body.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; return L, i, L[i].split(' | ')
def set_cell(rid, col, new):
    global body
    L, i, c = cells(rid); c[col] = new; L[i] = ' | '.join(c); body = '\n'.join(L)
def append(rid, text):
    L, i, c = cells(rid); set_cell(rid, 5, c[5].rstrip() + ' ' + text)
# ---- the rows renamed, now grounded ----
rep('| The alchemists\' Great Work — or the endless turning of the Wheel — powering a starship. |', '| Endless re-tempering (Model I, §7) — or a generative loop that feeds itself (Model II, §7) — powering a starship. |')
rep('*Substance:* the Boundary Furnace; *Process:* the Cycle-Limit Observatory.',
    '*Substance:* the Boundary Furnace — it drives substance to the boundary of form and reads what it does there (Model I, §7); *Process:* the Cycle-Limit Observatory — it drives patterns to their limits and reads the flow (Model II, §7).')
rep('| QM-E10 | **Elixir of Life** |', '| QM-E10 | **Temperament Medicine** |')
rep('**Elixir of Life**ⁿ [world wonder;', '**Institute of Temperament**ⁿ [world wonder;')
rep('— a flourishing, long-lived realm;', '— the living body kept in ideal balance of the Qualities (Model I, §7): a flourishing, long-lived people;')
rep('and the Elixir of Life (QM-E10) crowns a flourishing, self-contained realm', 'and Temperament Medicine (QM-E10) crowns a flourishing, self-contained civilisation')
rep('— the harmony studied everywhere, if not the Wheel itself.', '— the coupling studied everywhere, if not the Wheel itself.')
set_cell('QM-E12', 5, 'The elemental prerequisite for Hyperspace FTL (Method C), and fires the report that decides it (§4, *The Evidence Map*). '
    '*Substance:* "Aether Strata Theory" — the Aether in strata of ever-greater purity, in which distance itself is different (Model I, §7). '
    '*Process:* "Higher-Order Cycle Theory" — cycles of higher order than the five, in which distance is measured differently (Model II, §7).')
rep('Extra dimensions and the higher spheres are one truth wearing two faces.', 'Extra dimensions and the higher strata are one truth wearing two faces.')
rep('| A furnace in every keel. |', '| A reactor in every keel. |')
rep("read as the Aether's own tension at the scale of the heavens (Substance)", "read as the Aether's own tension at cosmological scale (Substance)")
# ---- QM-E07: the Aether Tension Engine, governed by FQ4 as its mirror is ----
L, i, c = cells('QM-E07')
c[1] = '**Aether Tension Engine**'; c[4] = 'QM-E13 (Aetheric Vacuum) + QM-E27 (Plenum Gravitation)'
c[5] = ('⟨[+1 Production] from all [Power Plant] buildings⟩ — the medium hums faintly in every plant. **Aether Tension Engine**ⁿ [world wonder; 1500; '
        '⟨[+15]% [Production] [in all cities]⟩; ⟨Provides [2] [Aluminum]⟩; ⟨Provides [2] [Rare Earths]⟩ — power drawn from the medium at scale, and spent on making the rare common]. '
        '**Frontier Question FQ4 (Vacuum Energy):** where vacuum energy is extractable (~20% of worlds) it validates; otherwise it dead-ends with a clear negative report — '
        '"the medium\'s tension yields only traces" — exactly as Zero-Point Energy (ES12) does in atomic worlds. '
        '*Substance:* "Aether Tension Engine" — power drawn from the Aether\'s tension, the vacuum tap at power scale (Model I, §7); with power this abundant, re-tempering\'s loss stops mattering, '
        'and common substance is re-tempered into the rare metals. *Process:* "Still-Point Engine" — power drawn at the still point where the cycle turns (Model II, §7); '
        'so much flow drives Earth-patterns forward into Metal — Earth bears Metal — faster than any mine. The mirror of Zero-Point Energy (ES12), as its prerequisites are of ES12\'s '
        '(Casimir Effect Amplification and Quantum Gravity Theory).')
c[6] = 'Power from the medium itself — where the medium allows it.'
L[i] = ' | '.join(c); body = '\n'.join(L)
rep('| **FQ4: Vacuum Energy** | Extractable (20%) / Trace-only (80%) | ES12 validates or dead-ends; QP12 always works as science (Casimir sensors) either way. |',
    '| **FQ4: Vacuum Energy** | Extractable (20%) / Trace-only (80%) | ES12 (Zero-Point Energy) validates or dead-ends — in elemental worlds QM-E07 (Aether Tension Engine) does the same; QP12 (Casimir Effect Amplification) and QM-E13 (Aetheric Vacuum) always work as science either way. |')
# ---- the deciding rows point to the evidence map; the two vacuum rows are science in every world ----
rep('| Fires the FTL report on traversable geometries. *Elemental:*', '| Fires the report that decides Wormhole FTL (§4, *The Evidence Map*). *Elemental:*')
append('RC07', 'With Black Hole Thermodynamics (RC04), fires the report that decides Wormhole FTL (§4, *The Evidence Map*).')
append('QM-E06', 'Fires the report that decides Warp and Wormhole FTL (§4, *The Evidence Map*).')
append('QP12', 'Always works as science, whatever FQ4 (Vacuum Energy) decides: a throat is held open by the Casimir effect\'s negative energy, real in every world. Its report concerns vacuum energy, not the FTL method.')
rep('The elemental prerequisite for Wormhole FTL (Method B), and fires the "the medium yields more energy than theory predicts" report.',
    'The elemental prerequisite for Wormhole FTL (Method B). Like Casimir it always works as science; whether the medium\'s tension can be drawn at power scale is FQ4 (Vacuum Energy), read at the Aether Tension Engine (QM-E07).')
# ---- gravitic engineering answers to FQ7 alone; exotic matter must exist to be fabricated ----
set_cell('MS08', 4, '(QP11 Exotic Matter Synthesis, validated, or QM-E06 Exotic Matter, validated) + MS02')
append('MS08', 'It needs exotic matter that holds: where none can be sustained, there is nothing to fabricate.')
set_cell('RC09', 4, 'RC08 (validated) + MS02 (Nanotechnology / Fine Structuring)')
append('RC09', 'Gravity control needs no exotic matter in either kind of world — it is control of spacetime\'s coupling, of the Aether\'s rarefaction, or of the world-eddy\'s inward draw (Models I and II, §8) — '
       'so once the Gravitational Coupling Experiment validates, it is built with ordinary fine structure.')
rep('Sets derived truths: Methods A/B force exotic matter viable (QP11 or QM-E06 by world); Method C forces the higher-realms primitive (QP09 / QM-E12) to validate; Method D guarantees macro-coherence; Method E forces tachyonic anomalies; Method F forces a rideable plenum current.',
    'Sets derived truths — the deciding rows of §4\'s evidence map: Methods A/B make exotic matter viable (QP11 Exotic Matter Synthesis or QM-E06 Exotic Matter, by world); Method B also makes traversable geometry real (RC04 Black Hole Thermodynamics and RC07 Closed Timelike Curves validate); Method C makes the higher-strata primitive validate (QP09 String Theory Validation / QM-E12 Higher Strata Theory); Method D guarantees macro-coherence (QP07 Quantum Entanglement Mastery, CP10 Quantum Computing); Method E makes tachyonic anomalies real (QP04 Particle Accelerator and QP06 Standard Model Completion / QM-E08 Boundary Furnace and QM-E17 Complete Catalogue); Method F makes the plenum\'s currents faster than light (QM-E19 Celestial Current Survey). Every deciding row validates where its method is the world\'s, and dead-ends with a clear negative report everywhere else.')
# ---- §4 ----
rep('- Guidance triggers: RC04 → "black hole mathematics reveal unexpected traversable geometries" report. RC07 → "closed timelike curves appear stable under certain conditions" report. QP12 success → "vacuum energy extraction exceeds theoretical predictions" report.',
    '- Guidance triggers: RC04 (Black Hole Thermodynamics) → "horizon thermodynamics admits geometries a vessel could pass" — available an era before exotic matter can be tested. RC07 (Closed Timelike Curves) → "closed timelike curves are stable under certain conditions". Both fail clearly in every other world (§4, *The Evidence Map*). QP12 (Casimir Effect Amplification) is a prerequisite but not a decider: it always works as science, and its report answers FQ4 (Vacuum Energy).')
rep('- Requires: QM-E27 (Plenum Gravitation — the medium\'s gravitation) + QM-E06 (Exotic Matter, elemental) + QM-E19',
    '- Requires: QM-E27 (Plenum Gravitation — the medium\'s gravitation) + MS02 (Fine Structuring — the sail, cut at the medium\'s fineness) + QM-E19')
rep('Process: "Celestial Current Drive" — enter the flow of the turning cosmos, riding the ten thousand transformations.', 'Process: "Celestial Current Drive" — a vessel carried on the currents of the Great Cycle\'s flow.')
rep('QM-E19 → "a current runs through the plenum that a vessel might ride" report (the decisive one). QM-E06 → "the medium can be made to bear a sail" report.',
    'QM-E19 (Celestial Current Survey) → "the currents run faster than light could cross the same distance" (the decisive one); elsewhere, "the currents are real, but slower than light". The sail is fine structure, not exotic matter: the models keep the Plenum Drive apart from exotic Aether, the material of warps and throats.')
rep('| F Plenum | — (elemental worlds only) | QM-E27, QM-E06, QM-E19; energy: QM-E05 or ES15 |', '| F Plenum | — (elemental worlds only) | QM-E27, MS02, QM-E19; energy: QM-E05 or ES15 |')
rep('**higher realms** (Hyperspace)', '**higher strata of space** (Hyperspace)')
rep('| Higher realms | extra dimensions (QP09) | supernal spheres / higher cycles (QM-E12) | Hyperspace |', '| Higher strata | extra dimensions (QP09) | strata of purer Aether, or a cycle of higher order than the five (QM-E12) | Hyperspace |')
rep("quintessence's celestial mode, read on the Boundary Furnace and confirmed by the Complete Catalogue", 'a mode of substance that outruns light at the boundary of form, or a transformation that completes before it begins, read on the Boundary Furnace / Cycle-Limit Observatory and confirmed by the Complete Catalogue')
rep('whether it proves extra dimensions or charts the supernal spheres', "whether it proves extra dimensions or charts the medium's higher strata")
old_g = body[body.index('The guidance reports follow the same *shapes* in elemental idiom'):]; old_g = old_g[:old_g.index('\n')]
rep(old_g, 'The guidance reports follow the same shapes in elemental terms, and every method can be ruled out in both kinds of world: see *The Evidence Map* above, which gives every deciding row\'s report in both ontologies.')
emap = '''
### The Evidence Map

Each method has **deciding rows** — FQ1 (FTL Method)'s derived truths. A deciding row validates and reports its finding in a world whose method it decides; in every other world it dead-ends with a clear negative report, and the negative is always the plainer of the two (Principle 3). Reports describe observations, never methods. Elemental negatives name only what fails: exotic matter is the medium *inverted*, below its zero — not the thinning that is gravity (Model I, axiom 5), nor the opening of a cycle to the Great Cycle that every Generative Cycle Engine performs (Model II, axiom 6).

| Decides | Atomic row | Elemental row | Where it is the method | Everywhere else |
|---|---|---|---|---|
| Warp and Wormhole | QP11 Exotic Matter Synthesis | QM-E06 Exotic Matter (Elemental) | "Exotic matter of negative energy density has been synthesised." / Substance: "We have held the Aether below its zero density, and it stays there." / Process: "A pattern has been sustained below zero flow." | "Negative energy densities cannot be sustained." / "The Aether can be thinned, never inverted." / "A pattern can be opened, never turned below zero flow." |
| Wormhole | RC04 Black Hole Thermodynamics *(Atomic era)* | the same row, as the dark star | "Horizon thermodynamics admits geometries a vessel could pass." / "The dark star's rim admits a fold in the medium a vessel could pass." | "Every throat pinches shut faster than light could cross it." / Substance: "Every dark star closes smoothly: depth, but no fold." / Process: "Every still eddy closes on itself; nothing passes through." |
| Wormhole | RC07 Closed Timelike Curves | the same row, as closed circuits of the medium | "Closed timelike curves are stable under certain conditions." / "Closed circuits of the medium hold stable across a fold." | "Every closed curve proves unstable." / "Every closed circuit of the medium unwinds back into the flow." |
| Hyperspace | QP09 String Theory Validation (else QP10 Loop Quantum Gravity validates) | QM-E12 Higher Strata Theory | "Additional spatial dimensions are confirmed." / Substance: "The medium is stratified: purer strata lie beyond, and distance there is not what it is here." / Process: "A cycle of higher order than the five runs through everything." | "Spacetime is discrete at the smallest scales." / "The medium is one grade throughout." / "The five phases are complete: there is no higher cycle." |
| Tunnelling | QP07 Quantum Entanglement Mastery, CP10 Quantum Computing | — (atomic only) | "Coherence persists far beyond what theory predicts." | "Quantum coherence decays exactly as predicted at macro scales." |
| Tachyonic | QP04 Particle Accelerator, QP06 Standard Model Completion *(Atomic era)* | QM-E08 Boundary Furnace / Cycle-Limit Observatory, QM-E17 Complete Catalogue *(Atomic era)* | "Particle tracks arrive before they were emitted"; "the equations contain superluminal solutions." / Substance: "At the boundary of form, a disturbance arrives before it is made." / Process: "A transformation completes before it begins." | "Everything behaves exactly as the Standard Model predicts." / "Nothing at the boundary of form outruns light." / "No transformation completes before it begins." |
| Plenum | — (elemental only) | QM-E19 Celestial Current Survey | "The currents run faster than light could cross the same distance — a vessel might ride them." | "The currents are real, but slower than light: a vessel would ride them as a ship rides a river." |

**Context, in every world:** QP08 Quantum Gravity Theory and QM-E27 Plenum Gravitation report that space, or the medium, "is more malleable than expected"; QM-E04 Unified Field Theory (Elemental) that "the medium is not still — it has structure". **Not deciders:** QP12 Casimir Effect Amplification and QM-E13 Aetheric Vacuum always work as science, whatever FQ4 (Vacuum Energy) decides — Wormhole still needs them, since a throat is held open by the Casimir effect's negative energy, but their reports answer vacuum energy, not the method. **The matter-axis methods** are ruled out at the decisive experiment itself: an elemental world's CH19 Systematic Element Analysis finds matter continuous — nothing passes without crossing between, so no Tunnelling — and an atomic world's finds space a vacuum, with no medium to ride.

'''
rep('\n### FTL in Elemental Worlds', emap + '### FTL in Elemental Worlds')
body = body.replace('Complete Tech Tree Design Document (v3.110)', 'Complete Tech Tree Design Document (v3.111)', 1)
open(p, 'w', encoding='utf-8').write(body + log); print('v3.111 edits applied')
