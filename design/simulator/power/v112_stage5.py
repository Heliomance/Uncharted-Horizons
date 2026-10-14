"""v3.112, stage 5 (text): the Space era's price, §1.5's note, the changelog entry, the summary statistics."""
import re
P = '/home/user/Uncharted-Horizons/design/simulator/outputs/wip/tt_v112_wip.md'
L = open(P, encoding='utf-8').read().split('\n')
def one(pred):
    h = [n for n, l in enumerate(L) if pred(l)]; assert len(h) == 1, len(h); return h[0]
# --- §2: the Space era's price per discovery, ×0.8 ---
i = one(lambda l: l.startswith('| **Space** | 51,842 |')); assert '| 1,399 |' in L[i]
L[i] = L[i].replace('| 1,399 |', '| 1,119 (×0.8, v3.112) |')
i = one(lambda l: l.startswith("The Space era's span is provisional"))
L[i] = ("The Space era's span is provisional. The FTL endgame (§4) widened the era with the signature fields' pools and, at the span's price, stretched it from the provisional 29 turns "
        "to 45–50; v3.112 therefore sets its price per discovery 20% below the span's (1,399 → 1,119), which scales every Space-era row alike — tests, builds, instruments' breakthroughs and pools. "
        "Measured on the full design, a good economy then wins near turn 295 and an average one near 380 (see the v3.112 changelog). Era *entry* (above) is separate from these spans and was measured before they were redrawn.")
# --- §1.5: the agreed Endeavour price, pending the discovery model's rewrite ---
i = one(lambda l: l.startswith('- **Cost premium.** Total Insight cost is roughly 2.5–3×'))
L[i] = L[i].replace('- **Cost premium.** Total Insight cost is roughly 2.5–3×',
                    '- **Cost premium.** *(Agreed in v3.112: 2×, as insurance rather than a shortcut; this section is rewritten with the discovery model, a deferred task.)* Total Insight cost is roughly 2.5–3×', 1)
i = one(lambda l: l.startswith('**Grand Endeavours (Section 1.5):**')); L[i] = L[i].replace('at a 2.5–3× Insight prem', 'at a 2× (v3.112; 2.5–3× before) Insight prem', 1)
# --- §8: summary statistics, recounted from the rows ---
rowpat = re.compile(r'^\| ([A-Z]{1,3}\d+[A-Z]?(?:-W)?|ME-B|NP-F\d+|QM-E\d+|MI05B|MI06B|[A-Z]{2}-[A-Z]\d+) \| ')
tiers = {}
for l in L:
    if rowpat.match(l):
        t = l.split(' | ')[2].split()[0].strip('*'); tiers[t] = tiers.get(t, 0) + 1
total = sum(tiers.values())
for lab, key in (('Total Breakthroughs', None), ('CORE Breakthroughs', 'CORE'), ('STANDARD Breakthroughs', 'STANDARD'), ('UNCOMMON Breakthroughs', 'UNCOMMON'), ('RARE Breakthroughs', 'RARE'), ('UNIQUE Breakthroughs', 'UNIQUE')):
    i = one(lambda l, lab=lab: l.startswith(f'| {lab} |')); L[i] = f'| {lab} | ~{total if key is None else tiers.get(key, 0)} |'
# --- the changelog entry ---
i = one(lambda l: l.startswith('### v3.111 — '))
entry = '''### v3.112 — The FTL Endgame Redesign Written In
- **§4 rewritten** from the direction document's W1–W19. A hypothesis for each candidate method, proposed by a CORE theory row and listed on the FTL screen from RC01 Special Relativity; the unified theory (QP08 / QM-E27) closes the list. **Three conditions per method**, each a Space-era result with a named host, a positive raising a method's standing and any failure ruling it out; **every report is true**; the screen shows facts, never odds or advice, and every hint points to where progress is possible now. **Generation rules**: the viable method uniformly, the other conditions at even odds, and a guarantee checked as a battery.
- **Instruments answer the measurement questions.** CP21 Macroscopic Quantum Control unlocks the Orbital Quantum Laboratory, the new **RC11 Gravitational Leakage Survey** the Space Interferometer, and RC05 Dark Matter Identification or RC06 Dark Energy Understanding the shared Survey Telescope — national wonders whose completion settles the question. RC05 and RC06 now sit alongside each other (RC02 + RK05 + the unified theory). Theoretical tests answer with their breakthrough. A test's evidence travels with it by diffusion, trade or theft; a measurement still needs the receiver's own instrument.
- **The theory phase opens promptly**: each unified theory needs its ontology's great instrument (QP08 needs QP04 Particle Accelerator; QM-E27 needs QM-E08 Boundary Furnace, and MA13 Topology so every proposal arrives first), and both instruments become **CORE**; QM-E08 needs EL07 Power Grid, as QP04 does. Neither instrument settles a condition any more.
- **The prototype** (a Grand Endeavour, one per method, on the FTL screen) costs **5×** the Space era's price, runs its full length and reports; the SS FTL Drive needs only the viable method's successful prototype. Committing before certainty is the **Hail Mary**. Completing the prototype and the Drive is announced to every civilisation; committing stays private.
- **The Space era widened** (W18): signature pools for Computing (CP16–CP22), Energy Systems (ES17–ES22), Materials Science (MS10–MS17), Mathematics (MA15–MA23), Nuclear Physics (NP12–NP17), Thermodynamics (TH15–TH22) and Aeronautics (AE14–AE20), each carrying its method's engineering; entry and pool rows at 2.5×, capstones at 4×, condition hosts and deciders at 1×. QM-E07 Aether Tension Engine moves to Energy Systems, QM-E23 Current Sail to Aeronautics (now STANDARD). Space Engineering settled: the Dyson Swarm becomes **SE09 Advanced Solar Power** and its Orbital Solar Array, and MS09 Dyson Sphere Materials is retired. Rocketry settled, with one new row, **RK17 Reconnaissance Satellites** (the Spy Satellite).
- **Balance**, measured on three benchmark players (expert, novice, average) at 60 games a cell: round two's changes — MS17 for Wormhole at 4×, ES18 without ES22, AE14 1×, atomic Tachyonic without NP11 (NP15 needs EL11 and a power plant), TH20 4×, MA19 1×, CP16 1× — and CP10 Quantum Computing at 2×. MS17 is **Transformation Media**: Shockproof Walls (siege resistance in their city) and Bomb Shelters made 50% more effective. Victory medians: expert about turn 294, novice 305, average player 380; methods within a few turns of each other.
- **Reliability**: MS02 Nanotechnology / Fine Structuring is CORE, and QM-E06 accepts MS02.
- **Removed**: the three clauses speeding Tunnelling's "final research", a step from the older design; QP13 Hidden Variable Discovery's Determinist Institute instead reveals every breakthrough as soon as the civilisation becomes eligible for it.
- **The Space era's price per discovery ×0.8** (§2).
- **Deferred**: the discovery model's write-up in §1.2 and §1.5 (Grand Endeavours at 2×, proximity revelation at 10%); the non-FTL Space-era fields; the fork engine work (the orbital unique, buildings that settle a condition, `Nuke.kt`'s context, the Determinist reveal, the announcements). New buildings' and units' costs and statistics are marked "set at spec".
'''.rstrip('\n').split('\n')
L[i:i] = entry + ['']
open(P, 'w', encoding='utf-8').write('\n'.join(L))
print('stage 5 text written; tiers:', tiers, 'total', total)
