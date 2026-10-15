# Row survey: merges, rows that don't earn their place, demotions to UNCOMMON

*Draft for Tamsin, 15 October 2026. Nothing here is applied: it's a list to choose from. Her request: "draft merge candidates, survey for technologies that don't earn their place, and ones that can be demoted to UNCOMMON".*

## Why, and how much

At parity (v3.123) the late game runs faster than one discovery a turn. From the turn a good economy's development enters the Modern era to the race's finish, the familiar world's expert makes about 132 discoveries in 105 turns, and the novice 138 in 111: about 1.25 a turn, rivals' knowledge included. The average economy makes about one a turn (135 in 136). A game holds about as many discoveries as it has turns whatever the prices, and the late prices are pinned by the science victory's length, so the only way down is fewer late discoveries. One a turn for the good economies needs about 27 fewer a game from the Modern era on, about a fifth.

**The data:** `design/simulator/power/results/row_survey_v3123.tsv`, written by `row_survey.py` from v3.123's confirmation (2,700 games, all 15 victory conditions). For every row, it gives:
- tier, era, focus and world;
- what the row grants;
- its dependents, and the victory goals it must precede;
- how often each player discovers it by the finish, how often by diffusion, and when.

The estimates below count a merged row's partner, a cut row, or 53% of a demoted row (UNCOMMON occurs 40% of the time against STANDARD's 85%) as discoveries removed from the stretch. They are first-order: they leave out the Insight a change frees, and the late prices' re-solving for parity afterwards (below).

**The rules followed**, from the thinning pass (v3.99–v3.105) and Tamsin's earlier decisions:
- Merge before cutting, and fold a row into a natural host: the same theme and era, adjacent in the tree. Nothing moves across eras, and every base-game object keeps a home on a CORE or STANDARD row. CORE rows keep CORE-only prerequisites.
- Every breakthrough carries a tangible benefit. Tamsin, 24 September: "a breakthrough that gives you nothing except unlocking further breakthroughs that you can't even see feels disappointing". Frontier rows that give an event or knowledge are fine, and so are focus unlocks.
- Leave alone:
  - Competing Solutions (Tamsin: "happy to leave separate as competing technologies");
  - the World Truth mirrors, except merged in step;
  - the frontier questions and FTL tests;
  - the airship chain, kept in v3.103 for the Airship Disaster;
  - the W18 Space-era pools (settled in the FTL work);
  - UNCOMMON, RARE and UNIQUE rows, which make games differ.

## First, a measurement: Competing Solutions' lock-outs

The simulator doesn't model Competing Solutions' lock-outs (§1.2 says so). In a real game an alternative that arrives after its primary is never developed, but the simulator counts it. From the Modern era on, that is 5.3 discoveries a game for the familiar world's expert, 4.6 for the novice, and 3.5–4.3 in the Process world. The main ones (expert, familiar world) are:

| Alternative locked out | Share of games |
|---|---|
| Industrial Canal Network | 1.00 |
| Bio-Fuel Plant | 0.89 |
| Direct-Current Stations | 0.86 |
| Thorium Reactor | 0.80 |
| Bio-Organic Synthesis | 0.61 |
| Biomass Plant | 0.53 |
| Perceptron Machines | 0.37 |

Real games therefore run about 5 discoveries a game slower than measured, and the target falls from about 27 to about 22. Modelling the lock-outs in the harness would make every later measurement truer; it would also move victory times a little, so it needs its own parity check.

## Merges

Recommended:

1. **General Relativity into Special Relativity, as "Relativity"** (Modern, CORE). General Relativity grants nothing of its own: its Unlocks cell reads "; prerequisite for all FTL theories". It is discovered in every game, right after Special Relativity, on the same prerequisite (Non-Euclidean Geometry, MA08). Its seven dependents follow the merged row: Quantum Gravity, Plenum Gravitation, Gravitational Waves, Black Hole Thermodynamics, Dark Matter, Dark Energy and Closed Timelike Curves. It is world-neutral in both kinds of world. **About −0.8 to −1.0 a game.**
2. **Quantum Electrodynamics into Quantum Field Theory** (Atomic, CORE), and in step, **Aetheric Electrodynamics into Unified Field Theory (Elemental)**. Quantum Field Theory grants nothing of its own ("Read as HIGH_ENERGY_PHYSICS; prerequisite for the FTL paths"), and QED was the first quantum field theory. The merged row takes Quantum Field Theory's name, QED's +10% Insight to Electronics, and the prerequisites Quantum Mechanics, Electromagnetism and Topology. The Ion Drive and Metamaterials follow it. In elemental worlds, Aetheric Electrodynamics (STANDARD) folds into the CORE Unified Field Theory, which then always carries its grants. **About −1.0 a game in every world.** It raises one question first; see *Found in passing*.
3. **Uranium Discovery into Radioactivity** (atomic worlds; Modern, CORE). Radioactivity's only grant is +1 Gold from Uranium tiles, and Uranium Discovery only reveals Uranium. The elemental mirror, Boundary Survey, already does both in one row ("the mirror of Radioactivity and Uranium Discovery together"), so this brings the two worlds level. The merged row needs the Periodic Table, Spectroscopy and Deep Shaft Mining, all CORE, Deep Shaft Mining from the Ancient era. **About −1.0 a game (atomic worlds).**

Worth considering:

4. **Dark Matter Identification and Dark Energy Understanding as one "Dark Sector Survey"** (Space). They have identical prerequisites and no dependents. The same instrument, the Survey Telescope, already answers both questions. One row can host both conditions, as Exotic Matter Engineering hosts two. This is an FTL change: the FTL screen loses one beat of evidence, so it needs Tamsin's decision under the FTL work. **About −0.8 to −0.95 a game.**
5. **Radar into Radio, as "Radio and Radar"** (Modern). Both come from the Vacuum Tube and Wireless Transmission; radar is radio detection and ranging. The cost is a heavy row: four canonical units (Anti-Aircraft Gun, Fighter, Bomber, Paratrooper), the Radar Station, the Broadcast Tower, three world wonders, the National Intelligence Agency and the City-State influence. That's about two base techs' worth. Stealth Technology would follow the merged row. **About −1.0 a game.**
6. **The four Modern power plants into two rows.** The Coal and Oil Power Plants would become one row, "Thermal Power Stations", which keeps both plants. The Biomass and Bio-Fuel Plants would become its alternative. The two Competing Solution pairs become one pair (fossil against grown fuel). Every plant object stays, so v3.96's "plants for every fuel" holds, but with fewer breakthroughs. The merged alternative needs both alternatives' prerequisites. **About −2.0 a game in the simulator; about −1.3 in real games**, since lock-outs already remove some of the alternatives.
7. **Ring Fortress into Reinforced Concrete** (Modern). The Military Base and the Bunker ("detached forts in concrete and steel") move to the row that brings the concrete. Star Fort stops being needed for the Bunker. The alternative is demotion (below). **About −1.0 a game.**

Not recommended:
- **Standard Model Completion into the Particle Accelerator.** It's in Tachyonic's build, and Tachyonic already wins 62–78% of races.
- **DNA Structure into Genetic Engineering.** They are twenty years apart, and either direction moves a Great Scientist or +25% growth by a large stretch of the game.

## Rows that don't earn their place

- **General Relativity and Quantum Field Theory**, which grant nothing (merges 1 and 2).
- **Sealed Environments** (Modern, STANDARD). It's a gateway with one minor bonus, +25% Production towards Submarines, and every game discovers it.
  - **Proposal: cut it.** Its prerequisites (Reinforced Concrete, Oxygen Theory, Glassmaking) move onto its two dependents, the Submarine and Life Support Systems, and the +25% moves onto the Submarine row.
  - Folding it into the Submarine instead would put Life Support, and so the Generation Ship, behind the naval line.
  - **About −1.0 a game.**
- **Atmospheric Science** (Modern, STANDARD). It grants +1 Gold from Harbors, for storm warnings to shipping, and it is the prerequisite of two Space rows that almost no game reaches.
  - **Proposal: cut it.** Its effect moves to Wireless Transmission: weather reports reached ships by wireless. Extremophile Engineering and Planetary Engineering Theory drop it from their prerequisites, or take Weather Prediction instead.
  - **About −1.0 a game.**
- **Aetheric Vacuum** (elemental worlds; Space). It grants nothing and fires no report, where its atomic mirror, Casimir Effect Amplification, reports on vacuum energy. It's on Wormhole's build, so **give it Casimir's report** rather than cut it. This is world parity, not pace.
- **Kept, though thin:**
  - **Anaesthesia** (+5 HP when healing): there is no clean host, since Germ Theory dead-ends outside germ worlds and Prosthetics is UNCOMMON.
  - **Helium Extraction:** designed as the Airship Disaster's end (but see below).

## Demotions to UNCOMMON

Each candidate is STANDARD, off every victory path, outside the Competing Solutions, and hosts no base-game object. Each is also a path historically less travelled.

1. **Desalination** (Atomic). Desalination at scale belongs to arid coastal states (the Gulf, Israel, Australia), not to everyone. **About −0.45 to −0.5 a game.**
2. **Hydroponics** (Modern). Soilless farming stayed a niche: Pan Am's Wake Island garden, military outposts, greenhouses. Vertical Farming (UNCOMMON) depends on it, so it becomes rare in practice. **About −0.5.**
3. **Flying Boat** (Modern). The maritime patrol aircraft of the naval powers. **About −0.45 to −0.5.**
4. **Nuclear Thermal Rocket** (Space). Built and ground-tested by two powers (NERVA, RD-0410) and never flown. It is one of the propulsion rows that speed the SS Boosters (+10% each, up to three); the Boosters never hold the launch up. **About −0.35 to −0.5.**
5. *Alternative to merge 7:* **Ring Fortress**, with the Military Base moved to Reinforced Concrete. Ring fortresses were a continental powers' answer (Liège, Verdun). **About −0.5.**
6. *Optional:* **Helium Extraction.** Helium was in fact a near-monopoly. The United States restricted its export, which is why the Hindenburg flew on hydrogen. As UNCOMMON, many civilisations would keep the Airship Disaster's risk, which changes the airship design, so it's Tamsin's call. **About −0.5.**

## What it adds up to

Discoveries removed from the stretch from the Modern era to the finish, first-order:

| Item | familiar, expert | familiar, novice | familiar, average | Process, expert | Process, novice |
|---|---|---|---|---|---|
| Merge 1, Relativity | 0.83 | 1.00 | 1.00 | 0.74 | 1.00 |
| Merge 2, Quantum Field Theory (both worlds) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Merge 3, Radioactivity (atomic) | 1.00 | 1.00 | 1.00 | — | — |
| Merge 4, Dark Sector Survey | 0.80 | 0.83 | 0.84 | 0.88 | 0.95 |
| Merge 5, Radio and Radar | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 |
| Merge 6, power plants (simulated) | 1.97 | 2.00 | 2.00 | 1.98 | 1.99 |
| Merge 7, Ring Fortress | 1.00 | 1.00 | 1.00 | 0.98 | 0.98 |
| Cut: Sealed Environments | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 |
| Cut: Atmospheric Science | 1.00 | 0.98 | 0.99 | 0.97 | 0.99 |
| UNCOMMON: Desalination | 0.45 | 0.50 | 0.50 | 0.44 | 0.51 |
| UNCOMMON: Hydroponics | 0.53 | 0.53 | 0.53 | 0.52 | 0.52 |
| UNCOMMON: Flying Boat | 0.43 | 0.52 | 0.51 | 0.53 | 0.53 |
| UNCOMMON: Nuclear Thermal Rocket | 0.37 | 0.35 | 0.30 | 0.52 | 0.53 |
| *Optional:* UNCOMMON: Helium Extraction | 0.53 | 0.53 | 0.53 | 0.53 | 0.53 |
| **Baseline: discoveries / turns** | **132 / 105** | **138 / 111** | **135 / 136** | **139 / 109** | **144 / 112** |

**Totals.**
- **Everything above except the optional item: about 11.4 fewer discoveries a game** for the familiar world's expert, about 9% of the stretch.
- **With the lock-out correction** (less about 0.7 of merge 6, which overlaps it): **about 16 fewer.**
- That takes the good economies from about 1.25 to about 1.1 discoveries a turn from the Modern era on, and the average economy from about one to about 0.9.

**After the merges, the late prices must be re-solved for parity.**
- Merges 1–3 remove rows every race passes through, and the cuts and demotions free Insight, so the science victory gets a little shorter.
- Raising the late prices to restore it slows every late discovery a little more: perhaps another 3–4 a game. That needs measuring.

**One a turn for the good economies would need about 6–10 more off.** The protected categories hold most of what's left: base-game object hosts, Competing Solutions, frontier and FTL rows, and the W18 pools (about 6 discoveries a game for the expert, entry rows included). Options:
- A second tier of skeleton merges: Wave-Particle Duality into the Atomic Model, with the elemental mirror Limiting Fineness into Fundamental Matter Theory (about −1).
- W18's pools sized to the pace.
- Accepting about 1.1 a turn late on.

## Found in passing

- **The two electrodynamics rows have drifted apart.** On 23 September, Quantum Electrodynamics and its elemental mirror Aetheric Electrodynamics both granted +2 Production from Factories. Quantum Electrodynamics has since lost it, probably in the power pass (I couldn't find when), but the mirror kept it and still says it has "the same grants". So elemental worlds get +2 Production per Factory that atomic worlds don't. Settle which is intended before merge 2.
- **W18 plans more Space-era content.** The agreed themes for the non-FTL Space-era fields (Warfare, Optics, Philosophy and the Arts and others) would add late rows. They are meant to be rarely reached, but the late pace argues for keeping them small.

## Next

Tamsin picks. Then, as v3.124:
- apply the chosen changes to the document, with each effect copied verbatim and every dependent re-pointed;
- run the battery and the wiki check;
- re-solve the late prices for parity on all 15 victory conditions (rivals rebuilt);
- report the late pace.

Modelling the lock-outs in the simulator first would let that measurement show real games' pace.
