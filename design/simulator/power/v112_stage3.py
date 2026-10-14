"""v3.112, stage 3: the individual decisions, on wip/tt_v112_wip.md. Every replacement is asserted to match exactly once."""
import re
P = '/home/user/Uncharted-Horizons/design/simulator/outputs/wip/tt_v112_wip.md'
L = open(P, encoding='utf-8').read().split('\n')
def row(rid):
    h = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; assert len(h) == 1, (rid, len(h)); return h[0]
def cells(rid): return L[row(rid)].split(' | ')
def put(rid, c): L[row(rid)] = ' | '.join(c)
def sub(rid, old, new, col=5):
    c = cells(rid); n = c[col].count(old); assert n == 1, (rid, n, old[:60]); c[col] = c[col].replace(old, new); put(rid, c)
def rsub(rid, pat, new, col=5):
    c = cells(rid); c[col], n = re.subn(pat, new, c[col]); assert n == 1, (rid, n, pat[:60]); put(rid, c)
def setcol(rid, col, val): c = cells(rid); c[col] = val; put(rid, c)
def note(rid, text):
    c = cells(rid); old = c[6].strip().rstrip('|').strip(); c[6] = (text + ' ' + old).strip() + ' |'; put(rid, c)

INSTR = 'national wonder — every civilisation may build its own; cost set at spec, about 3–6 turns of construction'
# --- the condition hosts, in W14's terms (W10: facts, never advice) ---
sub('QP04', 'Fires the tachyonic report (Method E) where it applies.', 'The great instrument of atomic physics: Quantum Gravity Theory (QP08) is built on its data (W17). It settles no FTL condition of its own (W1).')
sub('QP06', 'Fires the FTL report on superluminal solutions, positive or negative.', 'Hosts *a tachyonic sector exists* (atomic Tachyonic; merged into its build, W14).')
sub('QP09', 'Prerequisite for Hyperspace FTL (Method C).', 'Hosts *extra dimensions exist* (Warp and Hyperspace; a prove row, W4).')
sub('QP09', 'Mutually exclusive with QP10 — if one validates, the other dead-ends — and fires the report.', 'Mutually exclusive with QP10 — if one validates, the other dead-ends.')
sub('QP10', 'The final research of Quantum Tunnelling FTL costs ×0.67 (a cost multiplier, §1.2 — the old "+50% Insight").', 'Hosts *spacetime is discrete* (Tunnelling; a prove row, W4).')
sub('QP10', 'Mutually exclusive with QP09, and fires the report.', 'Mutually exclusive with QP09 — discreteness excludes extra dimensions.')
sub('QP11', 'Fires the report: success points to Warp and Wormhole, failure rules both out.', 'Hosts *exotic matter holds* (merged into the Warp and Wormhole builds, W14): a failure rules both out.')
sub('QP13', 'the final research of Quantum Tunnelling FTL costs ×0.5 (a cost multiplier)', 'the **Determinist Institute** reveals every breakthrough as soon as the civilisation becomes eligible for it — once its prerequisites are discovered it is Revealed, and so can be pursued as a Grand Endeavour: what was luck becomes calculation (fork engine work)')
rsub('GN10', r'\) and \. An alternative route to Quantum Computing \(CP10\); the final research of Quantum Tunnelling FTL costs ×0\.67 \(a multiplier\)\.',
     ') — an alternative route to Quantum Computing (CP10) and Quantum Communication (QP14), and the host of *macro-scale coherence* where FQ6 (Biological Depth) makes the biological route real (elsewhere it dead-ends with nothing to report).')
sub('QP14', ' — unhackable).', ' — unhackable). Hosts *tunnelling carries information faster than light — the Hartman effect* (Tunnelling; merged into its build, W14).') if cells('QP14')[5].count(' — unhackable).') == 1 else None
if 'Hartman' not in cells('QP14')[5]:
    c = cells('QP14'); c[5] = c[5].rstrip() + ' Hosts *tunnelling carries information faster than light — the Hartman effect* (Tunnelling; merged into its build, W14).'; put('QP14', c)
sub('RC07', 'With Black Hole Thermodynamics (RC04), fires the report that decides Wormhole FTL (§4, *The Evidence Map*).',
    'Hosts *closed timelike curves are stable* (Wormhole and atomic Tachyonic; elemental: *closed circuits of the medium are stable*, for Wormhole and Tachyonic) — theoretical at root, so the breakthrough is the answer (W14).')
sub('QM-E06', 'Fires the report that decides Warp and Wormhole FTL (§4, *The Evidence Map*).', 'Hosts *exotic matter holds* (merged into the Warp and Wormhole builds, W14): a failure rules both out.')
sub('QM-E08', "With the Unified Field (QM-E04) it reads out matter's superluminal mode and fires the elemental tachyonic report (Method E).",
    'The great instrument of elemental physics: Plenum Gravitation (QM-E27) is built on its data (W17). It settles no FTL condition of its own (W1).')
sub('QM-E12', 'The elemental prerequisite for Hyperspace FTL (Method C), and fires the report that decides it (§4, *The Evidence Map*).',
    'Hosts *higher strata or a higher-order cycle exist* (Warp and Hyperspace in elemental worlds; a prove row, W4).')
sub('QM-E13', 'The elemental prerequisite for Wormhole FTL (Method B).', 'The elemental prerequisite for Wormhole FTL and for Transformation Media (MS17).')
sub('QM-E17', "with the Boundary Furnace (QM-E08) it is the second reading of matter's superluminal mode and fires the tachyonic report (Method E).",
    'it hosts *the catalogue contains a superluminal form* (elemental Tachyonic; merged into its build, W14).')
rsub('QM-E19', r'\*\*prerequisite for the Plenum Drive \(Method F\)\*\* and the source of its decisive report,',
     '**prerequisite for the Plenum Drive**, and host of *the currents run faster than light* (merged into its build, W14) — its report:')
rsub('MS08', r'\*Exists only where the FTL method is Warp or Wormhole \(FQ1 \(FTL Method\)\)\.\*',
     '*Exists only where exotic matter is validated (QP11 / QM-E06).* Hosts *the bubble is stable* (Warp) and *the throat is stable* (Wormhole), both merged into those builds (W14).')
# --- the measurement tests and their instruments (decided before writing into the tree) ---
setcol('CP21', 5, f'⟨[+10]% [Science] [in all cities]⟩. Hosts *macro-scale coherence* (Tunnelling; merged into its build, W14), blocked by measurement: unlocks the **Orbital Quantum Laboratory**ⁿ [{INSTR}; massive superpositions in free fall, as ESA\'s MAQRO proposal would test; on completion it settles the condition]. Entanglement is already mastered (QP07); what is unknown is whether coherence survives for massive objects.')
note('CP21', "W18 — Pool; Tunnelling engineering (atomic worlds); hosts a condition, so priced as a decider.")
setcol('RC11', 5, f'Hosts *gravitational leakage shows the extra dimensions are open* (Hyperspace; elemental: *leakage into the strata*), which can hold only where they exist — blocked by measurement: unlocks the **Space Interferometer**ⁿ [{INSTR}; a gravitational-wave detector in orbit, as LISA is planned for the 2030s; on completion it settles the condition]. GW170817 already ruled out leakage at about 40 megaparsecs; larger scales need many more distant standard sirens.')
note('RC11', 'W1/W14 — the evidence row added by the redesign; priced as a decider.')
c = cells('RC05'); c[5] = c[5].rstrip() + (f' Hosts *dark matter is a hidden sector* (Hyperspace, W14): a sector interacting only through gravity, identified by lensing maps from space — blocked by measurement, so it unlocks the shared **Survey Telescope**ⁿ [{INSTR}; lensing maps and the expansion history, as Euclid measures both; on completion it answers each of the two questions — this one and RC06\'s — whose breakthrough the civilisation holds].'); put('RC05', c)
rsub('RC06', r'fires the report\.', 'hosts *dark energy is a tachyonic field* (atomic Tachyonic; elemental: *the medium carries a superluminal mode*, for Tachyonic and Plenum) — blocked by measurement: it also unlocks the shared Survey Telescope (RC05), whose completion answers it. Researched alongside RC05, not behind it: dark energy waits on the expansion history, not on dark matter.')
# --- Transformation Media (replaces Throat Stabilisation), checked against Unciv's source ---
setcol('MS17', 5, '⟨[+50]% Strength for cities <vs [Siege] units> <when defending>⟩; ⟨Population loss from nuclear attacks [-50]% [in all cities]⟩; ⟨Damage to garrison from nuclear attacks [-50]% [in all cities]⟩ — cities route shock waves around their structures. '
    'Designing a space by its shape: choose the geometry, then build the medium that produces it — as Morris and Thorne designed traversable wormholes, and as transformation optics steers light (Pendry, Schurig and Smith; Leonhardt, 2006); analogue wormholes have been built in metamaterials (a magnetic one, 2015), and seismic metamaterials tested at full scale (2014). '
    'On the wormhole path it is the discipline of shaping exotic matter into a designed throat, tried first on analogue throats. Substance: graded substance that makes waves travel as if the Aether were folded; Process: a pattern grown to channel the flow\'s course. '
    'Nuclear reductions multiply with a Bomb Shelter\'s and Hardened Shelters\' (NP13); a nuke\'s damage to city health is not reducible.')
note('MS17', "W18/balance round two — Wormhole's engineering, outside its tests; the Space-era successor to MS03 Metamaterials, without needing it.")
# --- Space Engineering: SE09 becomes Advanced Solar Power; MS09 retired ---
c = cells('SE09'); c[1] = '**Advanced Solar Power**'; c[2] = 'UNCOMMON'
c[4] = 'SE02 (Orbital Assembly) + RK07 (Reusable Launch Vehicle) + ES07 (Solar Panel)'
c[5] = ("⟨[+1 Production] from all [Solar Plant] buildings⟩. **Orbital Solar Array**ⁿ [world wonder; 2000; ⟨[+25]% [Production] [in all cities]⟩] — space-based solar power at scale, "
        "of which ES11 Beamed Power's small stations are the forerunners (ES11 is not required: chaining one UNCOMMON row on another would make the era's biggest project rare in practice).")
put('SE09', c); note('SE09', 'W18 (Space Engineering, settled) — replaces the Dyson Swarm; no forcefields, replicators or star-scale works in the Space era.')
i = row('MS09'); del L[i]
# --- Rocketry: one new row ---
rk = [n for n, l in enumerate(L) if re.match(r'^\| RK\d+ \|', l)]
L.insert(max(rk) + 1, '| RK17 | **Reconnaissance Satellites** | STANDARD | Space | RK05 (Satellite Technology) + RK07 (Reusable Launch Vehicle) | '
         '**Spy Satellite**ⁿ [unit; its own unit type, Satellite, so no ordinary detector filter matches it; statistics set at spec — high movement and good sight; ⟨Ignores terrain cost⟩; '
         '⟨May travel on Water tiles without embarking⟩; ⟨Can pass through impassable tiles⟩; ⟨May enter foreign tiles without open borders⟩; ⟨Cannot attack⟩; ⟨Invisible to others⟩; '
         '⟨Limited to [2] per Civilization⟩; *orbital* (fork engine work: occupies no tile slot, cannot block, be captured or be attacked)]. An endgame scout that gives sight where nothing else can — '
         'and since paradrops land only on visible tiles, satellite first, then the drop. Optics\' orbital tracking (detectors with ⟨Can see invisible [Satellite] units⟩) belongs to Optics\' Space-era pool (deferred). | '
         'W18 (Rocketry, settled) — the one new row; ship-focus prices stay as they are. |')
# --- W6: every proposal arrives before the list is closed ---
c = cells('QM-E27'); assert 'MA13' not in c[4]; c[4] = c[4].replace('RC02 (General Relativity) +', 'RC02 (General Relativity) + MA13 (Topology) +'); assert 'MA13' in c[4]; put('QM-E27', c)
# --- the old method letters and the retired Evidence Map, everywhere in the rows ---
LET = {'A': 'Warp', 'B': 'Wormhole', 'C': 'Hyperspace', 'D': 'Tunnelling', 'E': 'Tachyonic', 'F': 'Plenum'}
n_let = n_map = 0
for k, l in enumerate(L):
    if re.match(r'^\| [A-Z]', l):
        l2, a = re.subn(r' \(Method ([A-F])\)', '', l); l2, b = re.subn(r'Method ([A-F])\b', lambda m: LET[m.group(1)], l2)
        l2, d = re.subn(r'§4, \*The Evidence Map\*', '§4, *Conditions and Their Tests*', l2); L[k] = l2; n_let += a + b; n_map += d
open(P, 'w', encoding='utf-8').write('\n'.join(L))
print(f'stage 3 written; method letters replaced {n_let}, Evidence Map references {n_map}')
print('MS09 references left:', [l.split(" | ")[0][2:] for l in L if 'MS09' in l and l.startswith('| ')])
print('placeholders left:', [l.split(" | ")[0][2:] for l in L if '(effect: stage' in l])
