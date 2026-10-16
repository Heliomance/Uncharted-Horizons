# The FTL methods' relative length, and how to bring them into sync

*Report for Tamsin, 15 October 2026, on v3.125. Her request: "Re-analyse the FTL methods for relative length, and prepare a report on recommendations for bringing them into sync with each other." Nothing here is applied to the design document: every measurement patches a private copy of the tree with the simulator's switches (`SETCELL`, `ROWX`). Two independent checks of an earlier draft against the data and the document found errors; they are corrected here, and the share of the improvement due to each change was measured separately (S, F2c, R below).

## Correction (16 October): why the methods drifted apart

Tamsin asked why the same shapes that were balanced at round two are not balanced now (`design/simulator/power/results/ftl_drift_20261016.txt`). This report put each chain step's 8–21 turns down to the funded focus's Insight being shared among its Space-era rows. **Most of it is the wait for the step's idea to occur.** Every Space-era build row is STANDARD, so it must occur before it can be studied, and the wait starts only when its prerequisites are met: in a chain the waits add up, while a row that opens early occurs during its slack.

- At round two the simulator's W16 made a Space-era idea the player was pursuing occur at once (stronger than the rule the document wrote, which measures as no rule at all), so a step cost only its study, 1–12 turns. v3.120 dropped W16; v3.122 then doubled the Space-era idea window (28 turns instead of 14, so about 13 turns' wait instead of 7) and removed what had hidden the depth (development reaching the Space era only after the races; rivals from an old, fast pool whose diffusion finished the weaker players' deep chains).
- Measured on v3.125, one change put back at a time (2,700 games each, none unfinished): W16 as simulated, with rivals made under it, takes the spread from 9.7 to **2.9** turns, but also shortens the science victory to 295 / 299 / 372, outside the 5-turn limit. The 14-turn Space-era window alone gives 6.7 (301 / 302 / 376); the old rival pool 8.0; the old expert 10.7 → 7.7 for the expert; the Space price at ×0.8 and Endeavours on ideas under study nothing.

The recommendation below shortens the deep chains, so it treats the same cause from the other side, and its measurements stand. A rule that removes the serial waits themselves is the more direct alternative; it is not yet measured at parity.

## In brief

- **At v3.125 the methods are far apart.** For the expert, Wormhole, Tunnelling and Plenum finish 7–13 turns behind their world's field and Warp and Tachyonic 4–8 turns ahead. Averaged over the three worlds and three benchmark players, the method furthest from its field sits **10 turns** away, and methods win 25–78% of races against the field, where 50% is neutral (the standard in §9 of the decisions digest).
- **Why.** Every method reaches the unified theory at about the same turn, and engineering, not the tests, holds up 62–100% of races. Wormhole, Tunnelling and Plenum each need three Space-era rows one after another, and each step takes 8–21 turns once its prerequisites are met. Warp's and Tachyonic's last rows are available well before the Space era, wait for it, and are done soon after it opens.
- **Recommendation:** shorten each three-step chain by one step (three prerequisite changes), price the two fast methods' last rows higher (three multipliers), and raise the Space price to ×1.1 to keep the expert well inside parity. Measured on 5,400 games a setting, with rivals rebuilt under it: the method furthest from its field goes from 10.1 to **5.0 turns** (RMS 6.3 → 3.2); methods more than 5 turns from their field go from 18 of the 45 combinations of world, method and player to **2**; win shares go from 25–78% to 32–71%; and victory is **303 / 307 / 380** (expert / novice / average) against base Civ V's 305 / 305 / 380, with no game unfinished. The prerequisite changes do most of it on their own (10.1 → 5.7).

## Why the methods differ

The race taken apart for the expert at v3.125 (all three worlds, 60 games each; `ftl_balance.py`, `results/v3125_confirmation.txt`):

| Method | Unified theory | Certain | Build complete | Build is the last thing | What the build waits on last |
|---|---|---|---|---|---|
| Warp | 250–252 | 273–277 | 277–283 | 62–65% (both at once 28–35%) | Exotic Matter Engineering (62–68%) or Superconducting Energy Storage |
| Wormhole | 251 | 273–278 | 297–300 | 100% | Transformation Media |
| Hyperspace | 250–251 | 271–276 | 288–292 | 78–97% | Higher-Dimensional Geometry |
| Tunnelling | 250 | 268 | 292 | 90% | Macroscopic Quantum Control |
| Tachyonic | 250–251 | 270–276 | 276–283 | 85–90% | Superconducting Storage Rings or the Boundary Ring (73–85%), else Orbital Assembly |
| Plenum | 251–252 | 276–278 | 298 | 87–93% | Current Rigging |

Certainty comes before the build is complete: by only 4–9 turns for Warp and Tachyonic, and by 13–27 turns for the other four. So the engineering, not the tests, sets most races.

The engineering chains, with each row's median discovery turn and, in brackets, the median turns from its prerequisites being met to its discovery (expert, v3.125; `ftl_balance.py --chains`, recorded in `results/ftl_sync_20261015.txt`):

| Method | The build's chain (the three worlds' range) |
|---|---|
| Wormhole | Exotic Matter Synthesis or (Elemental) 264–268 (12–16) → Exotic Matter Engineering 279–282 (10–14) → Transformation Media ×4 297–300 (16–21): three steps after the theory |
| Plenum | Celestial Current Survey 268 (15–16) → Current Sail ×2.5 286–290 (16–19) → Current Rigging 298 (8–10): three steps after the theory |
| Tunnelling | Planetary Data Networks 265 (11) → Quantum Computing ×2 282 (17) → Macroscopic Quantum Control 292 (10): three steps, not waiting on the theory |
| Warp | Exotic Matter Synthesis 266–268 → Exotic Matter Engineering 277–281 (9–12); alongside, Superconducting Energy Storage ×2.5 269–273, available from about turn 222 but waiting 48–49 turns |
| Hyperspace | Optimisation Theory ×2.5 271–274, available from about 240 but waiting 31–33 turns → Higher-Dimensional Geometry 288–292 (13–17) |
| Tachyonic | atomic: Superconducting Storage Rings ×2.5 276, available from about 240 but waiting 36 turns; elemental: Re-Tempering Reactor 252 → the Boundary Ring ×4 281–282 (26–28) |

For the novice and the average player the shape is the same (the record has their chains).

Two things set the race. **Depth after the Space era opens:** each step of a chain takes 8–21 turns once available, about 8–17 at ×1 and 16–21 at ×2–×4. (Corrected 16 October: most of that is the wait for the step's idea to occur, not the funded focus's Insight being shared among its 6–11 Space-era rows; see the correction above.) Three-step chains therefore finish around turn 292–300. **Waiting for the Space era:** rows available before it (Superconducting Energy Storage, the Storage Rings, Optimisation Theory) wait 26–49 turns, because the expert does not pay their ahead-of-time premium early, so Warp's and Tachyonic's builds finish soon after the era opens, around 276–283, and Hyperspace's later because its second row only starts when Optimisation Theory is done. Prices matter too: in the first candidate, Transformation Media at ×1.5 brought Wormhole 3–6 turns earlier, and the Current Sail at ×1 brought the novice's and average player's Process Plenum 5–6 turns earlier, though not the expert's.

## What was measured

All 15 victory conditions (three worlds, five methods each) and the three benchmark players, 60 games a cell; none unfinished in any setting. The spread is each method's victory median against its world's field (all its methods' games), averaged over the three worlds and three players: the largest deviation, its root mean square, and the range of win shares. "Own rivals" means the rivals that knowledge diffusion replays were rebuilt under the setting, as a confirmation needs.

| Setting | What changes from v3.125 | Games | Largest | RMS | Win shares | Victory (expert / novice / average) |
|---|---|---|---|---|---|---|
| v3.125 | — | 5,400 | 10.1 | 6.3 | 25–78% | 304 / 307 / 381 |
| F1 | prices only: Transformation Media ×1.5, Current Sail ×1, Quantum Computing ×1; Storage Rings ×5, Boundary Ring ×6, Energy Storage ×4 | 2,700 | 7.3 | 4.6 | 26–77% | 304 / 307 / 381 |
| **S** | **the three prerequisite changes alone**, own rivals | 5,400 | **5.7** | **3.5** | 31–69% | 301 / 304 / 377 |
| **F2c** | **S with Storage Rings ×5, Boundary Ring ×6, Energy Storage ×4**, own rivals | 5,400 | **4.6** | **2.9** | 33–67% | 301 / 305 / 378 |
| **R: recommended** | **F2c with the Space price ×1.1**, own rivals | 5,400 | **5.0** | **3.2** | **32–71%** | **303 / 307 / 380** |
| F3 | F2c's settings with v3.125's rivals, plus the Current Sail and Optimisation Theory at ×1.5 | 2,700 | 4.6 | 2.7 | 33–69% | 301 / 305 / 378 |
| F4 | F3 trimmed (Energy Storage ×5, Transformation Media ×5, Current Sail and Optimisation Theory ×1), Space ×1.1, own rivals | 2,700 | 5.1 | 3.2 | 30–67% | 303 / 306 / 380 |
| F5 | F3 with the Space price ×1.1, own rivals | 5,400 | 4.3 | 2.8 | 36–71% | 302 / 306 / 380 |

A method's median from 60 games carries about ±1.5 turns of noise, so the 5,400-game settings are the ones to compare, and differences of half a turn in the averaged largest deviation (F2c's 4.6 against R's 5.0) are within it. Counting the combinations of world, method and player more than 5 turns from their field: 18 of 45 at v3.125, 8 under S, 4 under F2c, 2 under R. F3's and F5's two extra price changes (the Current Sail and Optimisation Theory at ×1.5) made no difference beyond that noise, so they are not recommended. F4 showed Superconducting Energy Storage at ×5 overshooting for the novice and the average player (Warp up to 7 turns slow), and Transformation Media at ×5 did nothing to the weaker players' quick Wormhole.

Each method's victory against its world's field at v3.125, under F2c and under R (turns; two seed sets, 120 games a method; expert / novice / average):

| World | Setting | Warp | Wormhole | Hyperspace | Tachyonic | Tunnelling or Plenum |
|---|---|---|---|---|---|---|
| familiar | v3.125 | −5 / −4 / −4 | +12 / +10 / +8 | +1 / +5 / +3 | −5 / −5 / −6 | +7 / +4 / +4 |
| | F2c | −1 / 0 / 0 | +6 / 0 / 0 | +2 / 0 / +4 | −2 / −1 / +1 | −1 / −2 / −3 |
| | R | −1 / +2 / +4 | +6 / +1 / −1 | +4 / +5 / +4 | −3 / −3 / −1 | 0 / −2 / −2 |
| Process | v3.125 | −5 / −5 / −7 | +12 / +6 / +8 | +2 / +1 / +4 | −4 / −3 / −4 | +13 / +13 / +13 |
| | F2c | −2 / −1 / −2 | +1 / −2 / −4 | +2 / +1 / +5 | −3 / −2 / −4 | +4 / +3 / +4 |
| | R | −3 / +2 / +1 | +1 / −2 / −3 | +1 / 0 / +2 | −3 / −4 / −3 | +5 / +4 / +5 |
| Substance | v3.125 | −5 / −2 / −2 | +8 / +1 / +3 | +4 / +1 / +1 | −8 / −8 / −7 | +7 / +5 / +7 |
| | F2c | −1 / +1 / +1 | 0 / −5 / −7 | +1 / +2 / +2 | −4 / −5 / −3 | +6 / +5 / +6 |
| | R | −1 / +2 / +3 | −1 / −3 / −8 | +3 / +1 / +5 | −3 / −4 / −5 | +4 / +3 / +3 |

Under R the expert's builds are complete between turns 282 and 293 in every world (276–300 at v3.125), still the last thing in 73–100% of races; certainty comes at 266–278 as before.

## Recommendations

**1. Shorten each three-step chain by one step** (S: 10.1 → 5.7 on its own):

- **Transformation Media** (Wormhole's engineering row) needs the exotic-matter breakthrough itself — Exotic Matter Synthesis or Exotic Matter (Elemental), **validated** — with Casimir Effect Amplification or the Aetheric Vacuum, instead of Exotic Matter Engineering: `(QP11, validated, or QM-E06, validated) + (QP12 or QM-E13)`. Shaping a throat's geometry is a design problem for the material, as transformation optics and the Morris–Thorne geometry-first approach treat it, and need not wait for the matter to be fabricated in quantity. "Validated" keeps the row, and its Shockproof Walls and better Bomb Shelters, to worlds where exotic matter holds, as now (the measurements ran without it: the simulator does not model a row's validation, and in those worlds Wormhole is impossible anyway). Wormhole's build still needs Exotic Matter Engineering, so the two are studied side by side.
- **Current Rigging** (Plenum's last row, host of *the currents can be ridden*) needs the Celestial Current Survey and Aerospace Industry, instead of the Current Sail. The sail and the rigging become parallel parts of one craft; Plenum's build still needs both.
- **Quantum Computing** (Tunnelling) needs Quantum Entanglement Mastery and the Programmable Computer, or Bio-Quantum Coherence, and no longer Planetary Data Networks: a quantum computer needs entanglement and computing, not a planetary network. Planetary Data Networks stays the entry to the Computing pool, but it leaves Tunnelling's build.

**2. Price the fast methods' last rows higher** (F2c: 5.7 → 4.6): Superconducting Storage Rings (atomic Tachyonic) ×2.5 → **×5** and the Boundary Ring (elemental Tachyonic) ×4 → **×6**, both above the ×4 capstone price; Superconducting Energy Storage (Warp) ×2.5 → **×4**, capstone price (for the expert it is Warp's last row only about a third of the time; for the weaker players most of the time).

**3. The Space era's price ×1.05 → ×1.1** (1,469 → 1,539 per discovery), to re-centre parity. Parity holds without it (F2c: 301 / 305 / 378), but the expert then sits 4 turns early, close to the 5-turn limit; with it, R gives 303 / 307 / 380 (−2 / +2 / 0), and the prototype costs 5% more. It does not change the spread between methods beyond the noise. This one is a judgement between the two players' margins, so it is Tamsin's call; Claude recommends it.

**What these reopen.**
- The decisions digest §9 (round two): the Boundary Ring at ×4 (now ×6), and "CP16 1×", a Tunnelling lever that loses its purpose once Planetary Data Networks leaves Tunnelling's build. Transformation Media ×4, Quantum Computing ×2 and the Storage Rings without Antimatter Production stay.
- The digest §8 (W18) prices, "all 2.5× unless marked": the Storage Rings ×2.5 → ×5 and Superconducting Energy Storage ×2.5 → ×4. Also §8's structure of parallel rows opened by an entry row, since Quantum Computing would no longer sit behind Computing's entry.
- §4's pricing rule ("engineering rows in the signature fields cost 2.5× and their capstones 4×"): two rows would cost more than a capstone.
- §4's build table and the digest's §5, which read "CP10 Quantum Computing (after CP16 Planetary Data Networks)", and Planetary Data Networks' own note.
- With recommendation 3, v3.124's Space price ×1.05.

Unchanged: the condition-hosting build rows (Macroscopic Quantum Control, Exotic Matter Engineering, Current Rigging) stay at ×1; every method keeps a condition outside its build (W15); the rows the FTL screen lists as each method's build needs stay the same; no CORE row gains a non-CORE prerequisite.

**If adopted**, the next version would change: the prerequisite cells of Transformation Media, Current Rigging and Quantum Computing, with their notes; Planetary Data Networks' note; the multipliers on the Storage Rings, the Boundary Ring and Superconducting Energy Storage; §4's build table and its Prices sentence; with recommendation 3, §2's Space price and §4's prototype turns; and the digest's §5, §8, §9 and §10. Then the battery, the wiki check and a full confirmation with rebuilt rivals, as for every version.

## What remains

- **Residuals.** Under R, the two combinations more than 5 turns from their field are the expert's Wormhole in the familiar world (+6) and the average player's Wormhole in the Substance world (−8). The patterns that remain:
  - **Plenum** stays 3–5 turns slow for every player (win shares 32–37%). With the rigging made parallel, the Current Sail (×2.5) is now its last need in 62–87% of races, the sail and the rigging each taking about 15 turns once available, diluted by Aeronautics' Space-era pool. Lowering the sail to ×1.5 measured nothing (F3), so the remaining lever would be that pool's size or the Celestial Current Survey's place.
  - **Tachyonic** stays 1–5 turns quick (win shares 51–63%), even at ×5 and ×6.
  - **Hyperspace** is 0–5 turns slow: Optimisation Theory still waits about 30 turns for the Space era, then Higher-Dimensional Geometry takes 11–18.
  - **Wormhole** splits by player: for the expert it is slow in the familiar world (+6), for the weaker players quick in the Substance world (−3 and −8), since Transformation Media is now studied alongside Exotic Matter Engineering.
  A second round could take these on, but each is now within a few turns of noise, and play may show a human player's targeting shortens chains more than the simulated players' does.
- **The simulator's limits.** The benchmark players fund one focus at a time and never weigh a build row above the other ideas in its focus, which is why chain depth matters so much; a human who sees the build needs on the FTL screen and targets them could shorten chains the simulated players can't. The expert also declines rows whose ahead-of-time premium is too steep, which is why Warp's and Tachyonic's last rows wait for the Space era. Production, wonders and military pressure are not modelled. Play will tell whether the depth effect is as strong as measured.

## Data

- `design/simulator/power/ftl_balance.py` (each race taken apart; `--chains` for the chain timings), `ftl_sync.py` (the spread between methods, with unfinished games counted), and `results/ftl_sync_20261015.txt` (every setting above, the chain timings, and each setting's exact switches). The settings' result files are not kept; the record holds their switches, to re-run with `compare_settings.sh` (seed sets: the defaults, and `SEED0=37000 TRUTHSEED=91`).
- R is `SETCELL='MS17|4|(QP11 or QM-E06) + (QP12 or QM-E13);AE20|4|QM-E19 + AE14;CP10|4|((QP07 + CP01) or GN10)' ROWX=NP15:5,TH20:6,ES18:4 SPACEPRICE=1.1`, exported, with rivals from `make_pool.sh <world> R` under the same settings.
