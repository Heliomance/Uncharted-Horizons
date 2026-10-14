"""v3.112, stage 2: the seven signature fields' effects (W18 tables in the direction document), on wip/tt_v112_wip.md.
Effects are transcribed as agreed; uniques in ⟨⟩. Costs and statistics the design did not set are marked 'set at spec'.
'keep' rows retain their v3.111 effect and only gain their W18 role in the Notes column."""
P = '/home/user/Uncharted-Horizons/design/simulator/outputs/wip/tt_v112_wip.md'
L = open(P, encoding='utf-8').read().split('\n')
def row(rid):
    h = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; assert len(h) == 1, (rid, len(h)); return h[0]
def cells(rid): return L[row(rid)].split(' | ')
def put(rid, c): L[row(rid)] = ' | '.join(c)
def set_eff(rid, eff, role):
    c = cells(rid); c[5] = eff
    note = c[6].strip().rstrip('|').strip()
    c[6] = (f'W18 — {role}. ' + note).strip() + ' |'; put(rid, c)
def keep(rid, role):
    c = cells(rid); note = c[6].strip().rstrip('|').strip()
    c[6] = (f'W18 — {role}. ' + note).strip() + ' |'; put(rid, c)
def add_after(anchor, rid, name, tier, era, pre, eff, note):
    assert not any(l.startswith(f'| {rid} |') for l in L), rid
    L.insert(row(anchor) + 1, f'| {rid} | **{name}** | {tier} | {era} | {pre} | {eff} | {note} |')

# --- Computing: intelligence and AI, managing a mind ---
set_eff('CP16', '⟨[+10]% [Science] [in all cities] <in cities with a [AI Lab]>⟩. The planet\'s data joined into one network.', "Entry: opens Computing's Space-era pool; on Tunnelling's build through CP10 (atomic worlds)")
set_eff('CP17', '⟨<every [5] turns> Triggers a [Advisory Council] event⟩: the player chooses a research push (Insight for the funded focus), an industry plan (⟨[+X]% [Production] <for [N] turns>⟩) or an intelligence sweep (map reveals, spy promotions); X and N set at spec.', "Pool; the playstyle's reliable core")
set_eff('CP18', '⟨[5] units cost no maintenance⟩ — fleets that run themselves.', 'Pool; first step of capstone A')
set_eff('CP19', '⟨New spies start with [1] level(s)⟩, ⟨[+25]% spy effectiveness <when espionage is enabled>⟩; fallback ⟨[+1] Sight <for [Military] units> <when espionage is disabled>⟩.', 'Pool')
set_eff('CP20', '⟨[+10]% [Production] <in cities with a [AI Lab]>⟩ — every plant simulated before it is changed.', 'Pool')
keep('CP15', 'Pool'); keep('CP10', 'Pool; Tunnelling engineering (atomic worlds)')
set_eff('CP22', '⟨[+15]% [Production] [in all cities]⟩, ⟨[+10]% [Gold] [in all cities]⟩.', 'Capstone A (the reliable one)')
c = cells('CP09'); assert 'the alignment dilemmas via `Events.json`' in c[5]
c[5] = c[5].replace('the alignment dilemmas via `Events.json`', "the council's proposals (CP17) grow stronger, and alignment requests appear via `Events.json`: granting autonomy brings bigger returns but occasional overreach events with real costs; restricting it is safer. Each answer adjusts a hidden trust stockpile"); put('CP09', c)
keep('CP09', 'First step of capstone B; deepens the council')
c = cells('CP12'); assert c[5].startswith('**The Awakening**')
c[5] = ('**The Awakening** — an `Events.json` chain coloured by the autonomy history (CP09): partnership (⟨Free Great Person⟩ every few turns and better proposals, '
        'with occasional demands that cost to refuse) or containment (much lower enemy spy effectiveness and more happiness; the proposals stop). '
        'No new civilisation is spawned — Unciv has no mechanism for that.'); put('CP12', c)
keep('CP12', 'Capstone B (rare)')
# --- Energy Systems: industrial power — connect, store, build big ---
set_eff('ES22', '⟨[+10]% [Production] [in all cities] <in cities connected to the capital>⟩ — connection to the capital gates the bonus.', 'Entry: opens the pool')
set_eff('ES17', '**Storage Array**ⁿ [building; cost set at spec; needs a power plant in the city; +2 Production; ⟨[+10]% [Production] [in this city]⟩].', 'Pool')
set_eff('ES18', '⟨[+25]% Production when constructing [Wonder] wonders⟩ — energy released in an instant: a warp bubble\'s need, and on the ground the heavy plant of megaprojects.', 'Pool; Warp engineering (both ontologies)')
set_eff('ES19', '⟨[+15]% Production when constructing [All] buildings⟩.', 'Pool')
keep('ES14', 'Pool; power for Warp (atomic worlds)'); keep('ES08', 'Pool; power for Warp (atomic worlds)'); keep('ES11', 'Pool')
set_eff('ES20', '⟨[-50]% maintenance cost for [Power Plant] buildings⟩.', 'First step of capstone A')
set_eff('ES21', '⟨[+15]% [Production] [in all cities]⟩.', 'Capstone A (the reliable one)')
keep('ES12', 'Capstone B, rare (atomic worlds)'); keep('QM-E07', 'Capstone B, rare (elemental worlds) — moved here from Quintessic Physics')
# --- Materials Science: resilience — cities that hold, forces that endure ---
set_eff('MS10', '⟨[+15]% Strength for cities⟩ (taking over Dyson Sphere Materials\' city strength).', 'Entry: opens the pool')
set_eff('MS11', '**Field Repair Unit**ⁿ [unit; statistics set at spec; ⟨All adjacent units heal [15] HP when healing⟩].', 'Pool')
set_eff('MS12', 'New military land units gain ⟨Withdraws before melee combat⟩; unlocks one dedicated stealth reconnaissance unit (statistics set at spec) with ⟨Invisible to non-adjacent units⟩.', 'Pool')
set_eff('MS13', 'New military units gain an Adaptive Armour promotion: ⟨[+15]% Strength <when defending>⟩.', 'Pool; first step of capstone A')
set_eff('MS16', '⟨[+15]% Strength <for [Water] units> <when defending>⟩.', 'Pool')
keep('MS08', "Pool; Wormhole's and Warp's engineering, wherever exotic matter is validated; hosts two conditions (W14), so priced as a decider")
set_eff('MS15', '**Modular Combat Vehicle**ⁿ [unit; statistics set at spec; ⟨Can transform to⟩ a support configuration and back — assault one turn, air defence and repair the next].', 'Capstone A (the reliable one)')
keep('MS07', 'Capstone B, rare')
# --- Mathematics: efficiency and secrecy — running lean, keeping secrets ---
set_eff('MA15', "⟨[-15]% maintenance cost for [All] buildings [in all cities]⟩, on top of MA13's −10%.", 'Entry: opens the pool')
set_eff('MA16', '⟨[-25]% maintenance costs⟩ (unit upkeep; to confirm against Unciv).', 'Pool')
set_eff('MA17', '⟨[-33]% Gold cost of upgrading⟩ — retrofits planned from the start.', 'Pool')
set_eff('MA18', '⟨[+1] Movement <for [Civilian] units>⟩.', 'Pool')
set_eff('MA22', '⟨[Gold] cost of purchasing items in cities [-15]%⟩.', 'Pool')
set_eff('MA23', '⟨[+5]% [Gold] [in all cities]⟩ (secure finance); ⟨[-25]% enemy spy effectiveness [in all cities] <when espionage is enabled>⟩.', 'Pool')
set_eff('MA19', '⟨[+10]% [Science] [in all cities]⟩.', 'Pool; Hyperspace engineering (both ontologies; the geometry of the strata in elemental worlds)')
set_eff('MA20', '⟨[-10]% Science cost of researching new Technologies⟩.', 'First step of capstone A')
set_eff('MA21', '⟨[-15]% Science cost of researching new Technologies⟩, ⟨[+10]% [Science] [in all cities]⟩.', 'Capstone A')
# --- Nuclear Physics (atomic worlds only): deterrence and big science ---
set_eff('NP12', '⟨[+15]% Great Person generation [in all cities]⟩ — accelerator laboratories as a home for big science.', 'Entry: opens the pool')
set_eff('NP13', '⟨Population loss from nuclear attacks [-50]% [in all cities]⟩, ⟨Damage to garrison from nuclear attacks [-50]% [in all cities]⟩; fallback ⟨[+15]% Strength for cities <when nuclear weapons are disabled>⟩.', 'Pool')
keep('NP11', "Pool (left Tachyonic's build in balance round two)")
set_eff('NP15', '⟨[+15]% [Science] <in cities with a [Nuclear Physics Lab]>⟩ — antimatter is held in magnetic traps and storage rings, and the converter ring is one at ship scale.', 'Pool; Tachyonic engineering — the converter ring (atomic worlds)')
keep('NP-F03', 'Pool')
set_eff('NP16', '⟨[+20]% Strength <for [Siege] units>⟩ — beams strike; lasers (Optics) defend.', 'First step of capstone A')
set_eff('NP17', '**Particle Beam Cannon**ⁿ [unit, Siege; statistics set at spec; a long-range siege unit].', 'Capstone A')
keep('NP09', 'Capstone B, rare (where fusion works)'); keep('NP-F04', 'Capstone B, rare (the fission road)')
# --- Thermodynamics: mastery of heat — industry that wastes nothing ---
set_eff('TH15', '⟨[+1 Production] from all [Factory] buildings⟩.', 'Entry: opens the pool')
set_eff('TH16', '⟨[+1 Production] per [4] population [in all cities]⟩.', 'Pool')
set_eff('TH17', '⟨[+1 Production] from all [Power Plant] buildings⟩.', 'Pool')
set_eff('TH18', "⟨[+15]% Food is carried over after population increases⟩, stacking with TH02's.", 'Pool')
add_after('TH18', 'TH19', 'Permafrost Engineering', 'STANDARD', 'Space', 'TH15 + tundra tiles in territory — **cost ×2.5**',
          'A worker-built improvement that, ⟨<upon building>⟩ it, will ⟨Turn this tile into a [Plains] tile⟩ on tundra (to be tested in play). A civilisation without tundra never becomes eligible, so never wastes a discovery on it.',
          'W18 — Pool; the one cold-land row. |')
c = cells('TH20'); c[1] = '**Boundary Ring / Cycle-Limit Ring**'; put('TH20', c)
set_eff('TH20', "⟨[+15]% [Science] <in cities with a [Deep Matter Lab]>⟩ — the converter ring of elemental worlds, driven by bound-energy release: NP15's mirror.", 'Pool; elemental Tachyonic engineering (elemental worlds only)')
set_eff('TH21', '⟨[+10]% [Food] [in all cities]⟩.', 'First step of capstone A')
set_eff('TH22', '⟨[+15]% [Food] [in all cities]⟩ — a stabilised climate and reliable harvests (if the fork gains a disaster mechanic, reducing disasters is its natural effect).', 'Capstone A')
# --- Aeronautics: reach — force projected anywhere, fast ---
set_eff('AE14', '⟨[+25]% Production when constructing [Air] units [in all cities]⟩.', 'Entry: opens the pool; on Plenum\'s build (elemental worlds)')
set_eff('AE15', '⟨[+2] Range <for [Air] units>⟩.', 'Pool')
set_eff('AE16', 'New infantry gain an Airborne promotion: ⟨May Paradrop to [Land] tiles up to [12] tiles away <in [{Friendly} {Land}] tiles>⟩.', 'Pool; first step of capstone A')
set_eff('AE17', '⟨[+1] Movement <for [Infantry] units>⟩.', 'Pool')
set_eff('AE18', "**Sky Carrier**ⁿ [unit; a land-type aerostat like AE01's Observation Balloon; statistics set at spec; ⟨Ignores terrain cost⟩; ⟨Can carry [3] [Fighter] units⟩; carries the Airship Disaster risk ⟨<before discovering [Helium Extraction]>⟩; stands on the confidence ladder with AE02, AE13 and AE12].", 'Pool; on the airship chain')
set_eff('AE19', 'Two modes: combat drops reach ⟨up to [20] tiles away⟩, onto tiles you can currently see; and any land unit ⟨May Paradrop to [{your} {City center}] tiles up to [40] tiles away <in [City center] tiles>⟩ — redeployment between your own cities.', 'Capstone A')
keep('QM-E23', 'Pool; Plenum engineering (elemental worlds) — moved here from Rocketry; promoted to STANDARD; its Propulsion tag stays')
set_eff('AE20', '⟨[+10]% Strength <for [Air] units>⟩ — the rigging that drops a craft into one current and out of another, as a balloonist changes altitude to change wind. Hosts the "riding the currents" condition (W14).', 'Pool; Plenum engineering (elemental worlds only); hosts a condition, so priced as a decider')
open(P, 'w', encoding='utf-8').write('\n'.join(L))
left = [l.split(' | ')[0][2:] for l in L if '(effect: stage 2' in l]
print('stage 2 written; rows still awaiting a stage-2 effect:', left or 'none')
