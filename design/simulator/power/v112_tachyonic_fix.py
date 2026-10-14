"""v3.112 amendment: the tachyonic-sector test moves to the Space era (W1), on new rows QP15 / QM-E28 with their national wonders."""
import re, sys
for P in ('/home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_v112.md', '/home/user/Uncharted-Horizons/design/simulator/outputs/wip/tt_v112_wip.md'):
    s = open(P, encoding='utf-8').read()
    def rep(a, b):
        global s; assert s.count(a) == 1, (P, a[:70], s.count(a)); s = s.replace(a, b)
    INSTR = 'national wonder — every civilisation may build its own; cost set at spec, about 3–6 turns of construction; +6 Science; 2 Scientist slots'
    L = s.split('\n')
    i = [n for n, l in enumerate(L) if l.startswith('| QP14 |')][0]
    L.insert(i + 1, f"| QP15 | **Beyond the Standard Model** | STANDARD | Space | QP08 (Quantum Gravity Theory) + QP06 (Standard Model Completion) | "
        f"Hosts *a tachyonic sector exists* (atomic Tachyonic; a prove row, W4/W14). The Standard Model is complete and contains no tachyons; whether a tachyonic sector lies beyond it is a question for colliders not yet built — "
        f"blocked by measurement, so it unlocks the **Very Large Particle Collider**ⁿ [{INSTR}; a next-generation collider, as the proposed Future Circular Collider would be; on completion it settles the condition]. "
        f"Mirrored by Beyond the Catalogue (QM-E28). | W1/W14 — the test moved here from QP06 Standard Model Completion, an Atomic-era row; priced as a decider. |")
    j = [n for n, l in enumerate(L) if l.startswith('| QM-E27 |')][0]
    L.insert(j + 1, f"| QM-E28 | **Beyond the Catalogue (Beyond the Codex)** | STANDARD | Space | QM-E27 (Plenum Gravitation) + QM-E17 (Complete Catalogue) | "
        f"Hosts *the catalogue contains a superluminal form* (elemental Tachyonic; a prove row, W4/W14) — blocked by measurement, so it unlocks the **Very Large Boundary Furnace**ⁿ [{INSTR} — the Very Large Particle Collider's stats; on completion it settles the condition]. "
        f"*Substance:* a furnace that drives forms past the last stable harmony in search of one that outruns light (Model I); *Process:* \"Beyond the Codex\" — an engine turning patterns at the very limit of the cycle (Model II). The mirror of Beyond the Standard Model (QP15). | "
        f"W1/W14 — the test moved here from QM-E17 Complete Catalogue, an Atomic-era row; priced as a decider. |")
    s = '\n'.join(L)
    # the old hosts become plain prerequisites (W1)
    rep('Hosts *a tachyonic sector exists* (atomic Tachyonic; merged into its build, W14).', "No longer hosts an FTL condition (W1: no answer before the Space era); still in Tachyonic's build. The search for a tachyonic sector beyond it is QP15 Beyond the Standard Model.")
    rep('it hosts *the catalogue contains a superluminal form* (elemental Tachyonic; merged into its build, W14).', "it no longer hosts an FTL condition (W1); still in Tachyonic's build. The search beyond it is QM-E28 Beyond the Catalogue.")
    # §4
    rep('a tachyonic sector exists (merged) | The medium carries a superluminal mode; closed circuits of the medium are stable; the catalogue contains a superluminal form (merged) |',
        'a tachyonic sector exists | The medium carries a superluminal mode; closed circuits of the medium are stable; the catalogue contains a superluminal form |')
    rep('a tachyonic sector — QP06 Standard Model Completion, or QM-E17 Complete Catalogue in elemental worlds;', 'a tachyonic sector or superluminal form — QP15 Beyond the Standard Model, or QM-E28 Beyond the Catalogue in elemental worlds;')
    rep('| RC06 Dark Energy Understanding (dark energy is a tachyonic field; the medium carries a superluminal mode) | the same Survey Telescope | DESI; Euclid |',
        '| RC06 Dark Energy Understanding (dark energy is a tachyonic field; the medium carries a superluminal mode) | the same Survey Telescope | DESI; Euclid |\n'
        '| QP15 Beyond the Standard Model (a tachyonic sector exists); elemental QM-E28 Beyond the Catalogue (a superluminal form) | Very Large Particle Collider — a next-generation collider; elemental: the Very Large Boundary Furnace (+6 Science, 2 Scientist slots each) | the proposed Future Circular Collider |')
    rep('| Tachyonic | QP06 / QM-E17 (merged); QP08 / QM-E27;', '| Tachyonic | QP06 / QM-E17; QP08 / QM-E27;')
    rep('TH20 Boundary Ring / Cycle-Limit Ring in elemental ones | RC06; RC07 |', 'TH20 Boundary Ring / Cycle-Limit Ring in elemental ones | RC06; RC07; QP15 / QM-E28 |')
    rep('a tachyonic sector in the Standard Model (QP06), and dark energy as a tachyonic field (RC06) | a superluminal form in the complete catalogue (QM-E17),',
        'a tachyonic sector beyond the Standard Model (QP15), and dark energy as a tachyonic field (RC06) | a superluminal form beyond the catalogue (QM-E28),')
    # changelog and statistics
    rep('- **The Space era\'s price per discovery ×0.8** (§2).',
        "- **The tachyonic-sector test moves to the Space era**, found by a traced game: it sat on QP06 Standard Model Completion and QM-E17 Complete Catalogue, Atomic-era rows, against W1. "
        "New rows **QP15 Beyond the Standard Model** and **QM-E28 Beyond the Catalogue** (Space, STANDARD, priced as deciders) host it as measurement tests; each unlocks a national wonder, the **Very Large Particle Collider** / **Very Large Boundary Furnace** (+6 Science, 2 Scientist slots), whose completion settles it. QP06 and QM-E17 return to plain prerequisites.\n"
        "- **The Space era's price per discovery ×0.8** (§2).")
    for lab, delta in (('Total Breakthroughs', 2), ('STANDARD Breakthroughs', 2)):
        m = re.search(rf'^\| {lab} \| ~(\d+) \|$', s, re.M); assert m; s = s.replace(m.group(0), f'| {lab} | ~{int(m.group(1)) + delta} |')
    open(P, 'w', encoding='utf-8').write(s)
print("tachyonic-sector move applied to the tree and its work-in-progress copy")
