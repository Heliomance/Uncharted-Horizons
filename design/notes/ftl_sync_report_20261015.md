# The FTL methods' relative length, and how to bring them into sync

*Report for Tamsin, 15 October 2026, on v3.125. Her request: "Re-analyse the FTL methods for relative length, and prepare a report on recommendations for bringing them into sync with each other." Nothing here is applied to the design document; the measurements use the simulator's switches (`ROWX`, `SETCELL`) on a private copy of the tree.*

## In brief

- **At v3.125 the methods are far apart.** For the expert, Wormhole, Tunnelling and Plenum finish 7–13 turns behind their world's field, while Warp and Tachyonic finish 4–8 turns ahead. Averaged over the three worlds and three benchmark players, the slowest or fastest method sits **10 turns** from the field, and methods win 25–78% of races against it, where 50% is neutral (§9 of the decisions digest).
- **The cause is structural, not price.** Every method reaches the unified theory at about the same turn (250–252 for the expert), and nearly every race is then held up by engineering, not by the tests. What differs is how many Space-era rows each build needs *one after another* once the Space era opens. Each such row takes 12–20 turns: it shares its focus's Insight with that field's other Space-era rows, which number 6–11 in every signature field since W18.
- **Recommendation: three prerequisite changes and five price changes, with the Space price ×1.1.** They more than halve the spread: averaged over worlds and players, the method furthest from its field goes from 10.1 to **4.3 turns** (RMS 6.3 → 2.8), and win shares from 25–78% to 36–71% (measured on 5,400 games a setting). Parity with base Civ V's science victory holds: **302 / 306 / 380** (expert / novice / average) against 305 / 305 / 380. The details, and which settled values they reopen, are below.

## Why the methods differ

The race, taken apart for the expert at v3.125 (all three worlds, 60 games each; `ftl_balance.py`, `results/v3125_confirmation.txt`):

| Method | Unified theory | Certain | Build complete | Build is the last thing | What the build waits on last |
|---|---|---|---|---|---|
| Warp | 251–252 | 273–277 | 277–283 | 62–65% (35% both) | Exotic Matter Engineering, or Superconducting Energy Storage |
| Wormhole | 251 | 273–278 | 297–300 | 100% | Transformation Media |
| Hyperspace | 250–251 | 271–276 | 288–292 | 78–97% | Higher-Dimensional Geometry |
| Tunnelling | 250 | 268 | 292 | 90% | Macroscopic Quantum Control |
| Tachyonic | 250–252 | 270–276 | 276–283 | 85–90% | Superconducting Storage Rings, or the Boundary Ring |
| Plenum | 251–252 | 276–278 | 298 | 87–93% | Current Rigging |

Certainty comes 10–25 turns before the build is complete, so the tests are not what holds methods back; the engineering is. The chains, with each row's median discovery turn (expert, v3.125):

| Method | The build's chain after the theory |
|---|---|
| Tachyonic | Superconducting Storage Rings 276 (its prerequisites met by about 222), or the Boundary Ring 281 — **one** Space-era row, not waiting on the theory |
| Warp | Exotic Matter Synthesis 266 → Exotic Matter Engineering 277–280; Superconducting Energy Storage 269–273 alongside — **two** |
| Hyperspace | Optimisation Theory 271 → Higher-Dimensional Geometry 288 — **two**, not waiting on the theory |
| Tunnelling | Planetary Data Networks 265 → Quantum Computing 282 → Macroscopic Quantum Control 292 — **three** |
| Wormhole | Exotic Matter Synthesis 266 → Exotic Matter Engineering 280 → Transformation Media 297 — **three** |
| Plenum | Celestial Current Survey 268 → Current Sail 286 → Current Rigging 298 — **three** |

A Space-era row takes 12–20 turns even at ×1, because the funded focus divides its Insight among all its ideas under study, and since W18 each signature field has 6–11 Space-era rows (Computing 11, Materials Science 9, Mathematics 9, Aeronautics 6–8). The race is therefore set by **serial depth**: one row deep finishes about turn 276–283, two deep 277–292, three deep 292–300. Prices move a row's length much less than its place in the chain: in the first candidate below, the Current Sail at ×1 instead of ×2.5 did not move Plenum at all.

## What was measured

All 15 victory conditions (three worlds, five methods each), the three benchmark players, 60 games a cell (2,700 games a setting), none unfinished in any setting. The spread is each method's victory median against its world's field (all its methods' games), averaged over the three worlds and three players: the largest deviation, its root mean square, and the range of win shares.

| Setting | What changes (from v3.125) | Largest | RMS | Win shares | Victory (expert / novice / average) |
|---|---|---|---|---|---|
| v3.125 | — | 9.7 | 6.1 | 25–80% | 304 / 307 / 381 |
| F1: prices only | Transformation Media ×1.5, Current Sail ×1, Quantum Computing ×1; Superconducting Storage Rings ×5, the Boundary Ring ×6, Superconducting Energy Storage ×4 | 7.3 | 4.6 | 26–77% | 304 / 307 / 381 |
| F2: structure | F1's three dearer rows, and the three prerequisite changes below | 4.8 | 3.0 | 31–70% | 302 / 305 / 379 |
| F3 | F2, with the Current Sail ×1.5 and Optimisation Theory ×1.5 | 4.6 | 2.7 | 33–69% | 301 / 305 / 378 |
| F4 | F3 trimmed further (Energy Storage ×5, Transformation Media ×5, Current Sail and Optimisation Theory ×1), Space price ×1.1, its own rivals | 5.1 | 3.2 | 30–67% | 303 / 306 / 380 |
| v3.125, two seed sets | — | 10.1 | 6.3 | 25–78% | 304 / 307 / 381 |
| **F5: recommended** | F3 with the Space price ×1.1, its own rivals; **two seed sets, 5,400 games** | **4.3** | **2.8** | **36–71%** | **302 / 306 / 380** |

F1 to F4 used v3.125's rivals except F4; F5 rebuilds them under its own settings, as a confirmation must. A method's median from 60 games carries about ±1.5 turns of noise, so differences of a turn or two between F2, F3 and F4 are not meaningful; F5 doubles the games to reduce it.

Each method's victory against its world's field under F5, and at v3.125 (turns; two seed sets, 120 games a method; expert / novice / average):

| World | Warp | Wormhole | Hyperspace | Tachyonic | Tunnelling or Plenum |
|---|---|---|---|---|---|
| familiar, v3.125 | −5 / −4 / −4 | +12 / +10 / +8 | +1 / +5 / +3 | −5 / −5 / −6 | +7 / +4 / +4 |
| familiar, F5 | −2 / +3 / +4 | +3 / +1 / −1 | +1 / +3 / +1 | −3 / −4 / −1 | +0 / −2 / −2 |
| Process, v3.125 | −5 / −5 / −7 | +12 / +6 / +8 | +2 / +1 / +4 | −4 / −3 / −4 | +13 / +13 / +13 |
| Process, F5 | −2 / +2 / +1 | +2 / −2 / −3 | −0 / +1 / +4 | −2 / −4 / −3 | +4 / +3 / +4 |
| Substance, v3.125 | −5 / −2 / −2 | +8 / +1 / +3 | +4 / +1 / +1 | −8 / −8 / −7 | +7 / +5 / +7 |
| Substance, F5 | −0 / +2 / +3 | −0 / −3 / −8 | +2 / +3 / +5 | −2 / −4 / −5 | +4 / +2 / +3 |

Under F5 the expert's builds complete between turns 282 and 292 in every world (276–300 at v3.125), still bound by engineering in 73–98% of races, and certainty comes at 266–278 as before.

## Recommendations

**1. Shorten the three-deep chains by one step** (the structural change; it does most of the work):

- **Transformation Media** (Wormhole's engineering row): needs *exotic matter itself* — Exotic Matter Synthesis, or Exotic Matter (Elemental) — with Casimir Effect Amplification or the Aetheric Vacuum, instead of Exotic Matter Engineering. Shaping a throat's geometry is a design problem for the material, as transformation optics is; it need not wait for the matter to be fabricated in quantity. Wormhole's build still needs Exotic Matter Engineering, so the two are studied side by side.
- **Current Rigging** (Plenum's last row and the host of *the currents can be ridden*): needs the Celestial Current Survey and Aerospace Industry, instead of the Current Sail. The sail and the rigging become parallel parts of one craft; Plenum's build still needs both.
- **Quantum Computing** (Tunnelling): needs Quantum Entanglement Mastery and the Programmable Computer (or Bio-Quantum Coherence), no longer Planetary Data Networks. A quantum computer needs entanglement and computing, not a planetary network; Planetary Data Networks stays the entry to the Computing pool.

**2. Price the fast methods' last rows as capstones**, so that one-deep chains take about as long as two-deep ones:

- Superconducting Storage Rings (atomic Tachyonic) ×2.5 → **×5**.
- The Boundary Ring / Cycle-Limit Ring (elemental Tachyonic) ×4 → **×6**.
- Superconducting Energy Storage (Warp) ×2.5 → **×4**.

**3. Lighten two rows that now finish chains alongside others:** the Current Sail ×2.5 → **×1.5**, and Optimisation Theory (Hyperspace) ×2.5 → **×1.5**.

**4. The Space era's price ×1.05 → ×1.1** (1,469 → 1,539 per discovery), which restores parity: the changes speed up the slow methods more than they slow the fast ones, so without it the expert's science victory comes 4 turns early.

**What these reopen.** The decisions digest's settled values (§9, round two) include Transformation Media at ×4 (unchanged here), the Boundary Ring at ×4 (now ×6), Quantum Computing at ×2 after Planetary Data Networks (still ×2; the prerequisite goes), and Superconducting Storage Rings without Antimatter Production (unchanged). The condition-hosting build rows (Macroscopic Quantum Control, Exotic Matter Engineering, Current Rigging) stay at ×1 as the digest requires. Every method keeps a condition outside its build (W15). The FTL screen's build lists don't change; only what each build need waits on does.

## What remains

- **Residuals.** After the changes most methods are within 3 turns of their world's field, against about 1–2 turns of noise. Patterns that remain: Tachyonic is still 1–5 turns quick for every player; Plenum 2–4 slow (its last two rows share Aeronautics with that field's Space-era pool, so the lever would be the pool's size, not a price); and with Transformation Media studied alongside Exotic Matter Engineering, Wormhole is now a few turns quick for the weaker players, 8 for the average player in the Substance world, the one deviation beyond 5. A second round could price the Tachyonic rings a little higher and Transformation Media a little higher for weaker players' sake; F4 shows the limits of such trims (Transformation Media ×5 and Energy Storage ×5 overshot).
- **The simulator's limits.** The benchmark players fund one focus at a time and never weigh a build row above the other ideas in its focus, which is what makes depth matter so much. A human player who targets a build row within a field could shorten chains the simulated players can't; play will tell whether the depth effect is as strong. Production, wonders and military pressure are not modelled.
- **If adopted**, it goes into the document as v3.126 (the three prerequisite cells, the five multipliers, §2's Space price, §4's balance table), with the battery, the wiki check and a full confirmation with rebuilt rivals, as for every version.

## Data

- `design/simulator/power/ftl_balance.py` (each race taken apart), `ftl_sync.py` (the spread between methods), `results/ftl_sync_20261015.txt` (every setting above).
- Settings, for re-measuring: F5 is `SETCELL='MS17|4|(QP11 or QM-E06) + (QP12 or QM-E13);AE20|4|QM-E19 + AE14;CP10|4|((QP07 + CP01) or GN10)' ROWX=NP15:5,TH20:6,ES18:4,QM-E23:1.5,MA15:1.5 SPACEPRICE=1.1`, with rivals from `make_pool.sh <world> F5` under the same settings.
