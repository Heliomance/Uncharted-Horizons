# The FTL race: what changed, when, and why the balance didn't hold

*Written for Tamsin on 16 October 2026, at v3.126. Sources: the changelog, the decisions digest, the direction document, the claude.ai transcripts, the Claude Code session of 14–16 October and the simulator's records (listed at the end). Checked against them by an independent reader before it was committed. When the FTL puzzle or its costs change again, add a row to the timeline and the cost table.*

## Reading the numbers, and some terms

- **Victory** is the median turn for the expert / novice / average player.
- **Spread** is how many turns from its world's field the method furthest from that field finishes, averaged over the three worlds and the three players. Perfectly level methods give 0. Noise alone gives about 1–2.5, nearer 4 when games vary more, as at v3.122.
  - Up to v3.125 the spread is measured at the race's finish, which doesn't depend on how victory is counted.
  - The analyses of 15–16 October measure it at victory. On that measure v3.125 is 9.7 (10.1 on the sync report's 5,400 games).
  - Every spread here was computed on 16 October from the saved results (`ftl_drift_20261016.txt`). At the time, balance was judged by each method's median and by its chance of winning races against its world's field, with 40–60% counting as balanced.
- **Round two** is the method balance agreed on 14 October, the last time the methods were level.
- **W16** is the rule against bad luck on the FTL route (2 October), dropped in v3.120.
- **Development** is a civilisation's cumulative Insight, which sets the era it is priced from. A breakthrough from a later era costs ×4 for each era it is ahead: the **ahead-of-time premium** (§1.2).
- How victory was counted, the target and the simulated players all changed along the way (*What the measurements assumed*, below). Compare a victory time only with others from the same period.

## In short

1. **The puzzle's shape has hardly changed since 14 October; the rules, prices and players around it have.**
   - Round two left the six methods level: spread 2.6.
   - The later changes were made for other reasons: corrections to the simulator, the safety net, base Civ V's game length, parity.
   - Most of them made Space-era rows take longer to occur or to study, and the cost did not fall evenly. At v3.122, against v3.120, the expert's race took:

     | Methods | How much longer |
     |---|---|
     | Warp and Tachyonic | 12–17 turns |
     | Wormhole, Plenum, Tunnelling and Hyperspace | 27–35 turns |

   - The likeliest reason is the wait for each row's idea to occur, which adds up along a chain of rows found one after another. Wormhole, Plenum and Tunnelling end in the longest such chains. This is inferred, since no run records when each idea occurred.
2. **The spread over time** (at the race's finish unless marked):
   - 2.6 at round two;
   - 3.3 at the final confirmation, after the pools, the rebalance and the theory gate (the pools alone measured 4.1, on 20 games a method);
   - 3.5–4.4 through the corrections and versions of 14–15 October;
   - 4.8 at v3.120, when W16 was dropped and the methods fell into today's pattern at about half today's size;
   - 13.2 at v3.122, easing to 11.7, 11.0 and 10.1 by v3.125;
   - 17.8 at victory (against v3.125's 9.7) with players who see only the screens.
3. **The 14 October balance was measured under conditions that have since gone:**
   - **W16 as the simulator had it:** a Space-era idea the player was pursuing occurred at once. The rule written into the design, that a funded focus keeps a Space-era idea's window open, measures as no rule at all.
   - **The old era timing:** development reached the Space era only after the races, and a Space-era idea's window lasted 14 turns (28 since v3.122).
   - **Rivals from a pool made before round one.** At the final confirmation their diffusion finished half to three-quarters of the weaker players' Hyperspace, Plenum and Tunnelling builds. At round two it finished a third at most.
   - **A fault in the Endeavour split:** while an Endeavour ran, a player had 180% of its income, 21–30% more Insight over a game.

   To find out how much of the drift each one explains, each was put back on a scratch copy of v3.125, one at a time. These were diagnostics, not proposals: the design and the simulator's defaults are unchanged. The fault was never put back.

   | Put back, as a test | Spread | What it shows |
   |---|---|---|
   | W16 as the simulator had it | **2.9** | The waits in sequence are most of the drift. But this W16 was never the design's rule, and it makes victory 6–10 turns too short. |
   | the 14-turn window | 6.7 | About a third of the drift is the window's length (see *Why the window's length matters*). |
   | the old pool | 8.0 | Part of round two's balance came from rivals made under older, faster rules, who reached the deep chains' rows sooner than rivals playing by the current rules could. |

   Of the three, only the window's length is a design choice. The old pool and the simulator's W16 were flaws in the old measurements; the rebuilt rivals, which play by the same rules as the player, are the better approximation of a real game, and they stay.

4. **The prices moved for their own reasons, and neither caused the spread nor cured it.** A price moves every method about alike: v3.125 with the Space era back at ×0.8 still measures 9.7. The Space era's price went:
   - to ×0.8 (14 October), with the prototype from 9× to 5×, to reach a victory target that turned out to rest on a misreading;
   - to ×2 (v3.122), for base Civ V's game lengths as then understood (320 / 400): 3–12 turns over that target, and 22–32 over the science-victory reference adopted next;
   - to ×1 (v3.123), for parity with base Civ V's science victory (305 / 380);
   - to ×1.05 (v3.124), to re-centre parity after merges and lock-outs shortened the race.
5. **Three ways to level the methods have been measured; none is adopted.** They were measured with different players, so their figures don't compare directly:

   | Way | Players | Spread | Victory |
   |---|---|---|---|
   | Shorten the deep chains (the sync report) | the old players | 10.1 → 5.0 | 303 / 307 / 380 |
   | The funded-focus rule, with the FTL rows ×1.4 | players who see only the screens | 17.8 → 4.7 | 301 / 305 / 380 |
   | The 14-turn Space-era window | the old players | 9.7 → 6.7 | 301 / 302 / 376 |

   The funded-focus rule makes FTL ideas occur once their prerequisites are met and their focus is funded. Its cost: the non-FTL Space-era breakthroughs held at launch fall from 22–24 a game to 13.5–15.

## Timeline

Times are UTC. Spreads are those computed on 16 October (see above).

| When (2026) | Version | What changed | Why | Measured |
|---|---|---|---|---|
| 13–14 Feb | first draft | One FTL method works in each game, and working out which is the science victory's puzzle. Every FTL prerequisite CORE or STANDARD. | Tamsin's brief | — |
| 10 Jul | v3.3–v3.17 | Grand Endeavours, with the FTL launch as the final one (2.5–3×). The FTL method a World Truth. The Plenum Drive for elemental worlds; Tunnelling atomic-only. | Tamsin wanted "a sixth option that only works in non atomic" worlds | — |
| 23–24 Sep | v3.55, v3.77 | The science victory becomes an FTL ship: the Apollo Program, three Boosters, the Cockpit and the SS FTL Drive (1,500 Production; exotic components +15% to the Drive only). | Tamsin: "honestly the FTL victory is the intended path" | — |
| 1 Oct | v3.108 | Eras redrawn to an even pace. The Space era gets 29 turns, provisional until an FTL re-audit, asked for earlier the same evening. | base Civ V's game length at each skill level | games of 262 / 320 / 396 turns for a strong, a good and a casual player |
| 2 Oct, morning | v3.110–v3.111 | The re-audit: elemental worlds get Plenum Gravitation and routes of their own, and every method can be ruled out (the evidence map). | four rows Warp and Wormhole need were atomic-only; elemental worlds finished 15–35 turns early and had no negative signals | builds complete on turns 278–301; Tachyonic about 20 turns before Wormhole |
| 2 Oct, from 11:28 | direction document | The redesign, W1–W19: <br>• evidence only from the Space era <br>• hypotheses on an FTL screen <br>• a prototype that can be a Hail Mary <br>• build separate from prove <br>• power <br>• W16 against bad luck <br>• a wider Space era (W18) | Tamsin: "Surely all of the indicators for which method is viable should be Space era" | FTL took about 45 turns of a 29-turn Space era; a 9× prototype (about 12 turns) recommended |
| 10–13 Oct | direction document | W18 sized and designed: a signature field per method, pools of about 10 rows at 2.5×, capstones 4×. <br>• Three conditions per method. <br>• Levers a, b, c. <br>• Instruments. <br>• Endeavours at 2×, the 10% glimpse and diffusion. <br>• The benchmark players. | 10–18% of games never reached certainty; many lone civilisations could never build their method | certainty in 96–97% of games, from 82–90% |
| 13 Oct, 18:48 | | Wormhole gets an engineering row (Throat Stabilisation, now Transformation Media) at 2.5×. | Wormhole fastest: nothing left to build after certainty in 80–88% of games | Wormhole from 35–36 to 39–43 turns into the Space era |
| 13 Oct, 22:14 | "current" | The benchmark players' first full measurement. | | 296 / 303 / 378; spread 4.6 |
| 13 Oct, 23:33 | round one | <br>• Wormhole's row at 4×. <br>• Warp without the Smart Grid, its storage at 1×. <br>• Aerospace Industry at 1×. <br>• Atomic Tachyonic without Antimatter Production. | Warp and Plenum slow, Wormhole fast | 294 / 301 / 376; spread 3.6 (run in 9 cells; the "current" results for the other six); Warp overshot |
| 14 Oct, 08:31 | round two | <br>• Warp's storage back to 2.5×. <br>• Higher-Dimensional Geometry and Planetary Data Networks at 1×. <br>• The Boundary Ring at 4×. | atomic Hyperspace and Tunnelling slow, elemental Tachyonic fast | 294 / 302 / 377; **spread 2.6** |
| 14 Oct, 09:28 | | The W18 pools priced (2.5×, capstones 4×). | Tamsin (09:26): "add in the wider pools" | 297 / 307 / 382; a first tilt (20 games a method): the expert's Warp quick, Wormhole and Tunnelling slow |
| 14 Oct, 10:38 | | The ship counted: the Drive (4 turns, 5 average) and a turn to launch. | Tamsin (09:42): "construction of the SS engine and final assembly of the probe need to be accounted for" | 302 / 311 / 387, 7–27 turns past the target |
| 14 Oct, 10:39 | the rebalance | The prototype from 9× to 5×; the Space era ×0.8. | back to the target of the time (about 295; 360–375) | 293 / 305 / 380 |
| 14 Oct, 11:23 | | The theory gate: each unified theory needs its ontology's great instrument, both CORE. The attention boost dropped. | elemental worlds' first answer took 10–11 turns | the novice's theory phase from 27 to 18 turns; victory unchanged |
| 14 Oct, 11:43 | final confirmation | (all the above, 2,700 games) | | 294 / 305 / 380; spread 3.3 |
| 14 Oct, 11:44 | | Quantum Computing at 2×. | atomic Tunnelling 3–4 turns slow for every player | in every run since; its effect never measured on its own |
| 14 Oct, 13:03–14:03 | v3.112 | Written into the tree. The Power Grid CORE. The tachyonic-sector test moved to new Space-era rows with instruments. | a lost Power Grid idea blocked the theory; the test was Atomic-era, against W1 | expert spot check: Tachyonic 2–4 turns slower; no before-and-after comparison for all three players |
| 14 Oct, 19:05–20:58 | simulator | <br>• Glimpse by tier, and every tier studied alike (both Tamsin's decisions). <br>• The Endeavour fault fixed. | the fault gave a player 180% of its income during Endeavours | 301 / 308 / 382; spread 3.5 |
| 15 Oct, 10:48 | v3.115 | Optimisation Theory, on Hyperspace's build, needs the Programmable Computer. v3.113–v3.119 change no other FTL row. | sixteen missing enablers | spread 4.4 |
| 15 Oct, 12:28 | v3.120 | <br>• Rediscovery on demand. <br>• Grand Endeavours only on revealed ideas that have not occurred. <br>• W16 dropped. | every game with contacts now finished; W16 only bought speed | 297–298 / 301–302 / 374–375; spread 4.8 |
| 15 Oct, 17:54 | v3.122 | <br>• Development at base Civ V's era timing. <br>• Space-era idea windows doubled. <br>• Modern and Atomic ×1.25, Space ×2. <br>• Rivals rebuilt. <br>• The expert retuned. <br>• The prototype priced from the income. | the game ended before development reached the Space era; base Civ V's game lengths | 323 / 328 / 407; **spread 13.2** |
| 15 Oct, 18:29 | `victory.py` | The Drive built from Production. | Tamsin (18:22): "we've not been accounting for the production cost of the SS parts in our benchmarks so far" | v3.122: 327 / 332 / 412 |
| 15 Oct, 20:30 | v3.123 | Late prices back to ×1; the Ancient era ×1.5. | parity with base Civ V's science victory, 305 / 380 | 304 / 307 / 380; spread 11.7 |
| 15 Oct, 21:45 | v3.124 | <br>• Relativity merged; it now proposes Warp, Wormhole and Tachyonic together. <br>• Other merges. <br>• Competing Solutions modelled. <br>• Space ×1.05. | fewer late breakthroughs | 305 / 307 / 379; spread 11.0 |
| 15 Oct, 22:51 | v3.125 | Ring Fortress merged into Reinforced Concrete. | | 304 / 307 / 381; spread 10.1 |
| 15–16 Oct | sync report | Proposed: three prerequisite changes, three dearer last rows, Space ×1.1. | Tamsin asked for the methods in sync | 303 / 307 / 380; spread at victory 10.1 → 5.0 on 5,400 games; not adopted |
| 16 Oct | analyses | Found: the weaker players' Endeavour rule never ran, and why the methods drifted. Measured: the funded-focus rule, and players who see only the screens. | Tamsin's questions | visible players: 310 / 312 / 386, spread 17.8; with the rule and the FTL rows ×1.4: 301 / 305 / 380 and 4.7; not adopted |

## What the costs have been

| Cost | How it has moved | Why |
|---|---|---|
| **The Space era's price per discovery** | ×1, 1,399 Insight (v3.108) → **×0.8**, 1,119 (the rebalance, 14 Oct; in v3.112) → **×2**, 2,798 (v3.122) → **×1** (v3.123) → **×1.05**, 1,469 (v3.124; today) | ×0.8: with the pools and the ship counted, victory had moved 7–27 turns past the target, and the race took 45–50 turns of a Space era sized at 29. ×2: base Civ V's game lengths, then taken as 320 / 400 (it came out 3–12 turns over them). ×1: against base Civ V's science victory, adopted next, v3.122 ran 22–32 turns over. ×1.05: v3.124's merges and lock-outs had shortened the race. |
| **The Modern and Atomic prices** | ×1 → ×1.25 (v3.122) → ×1 (v3.123) | as above |
| **The prototype** | 3× in the first runs (2 Oct; 2–4 turns) → **9×** (2 Oct; about 12 turns then, counted as 9, or 11 for the average player) → **5×** (the rebalance, 14 Oct), counted as 5 turns (6). Priced from the income since v3.122: about 8 turns (10) at ×2, 4 (5) at ×1 and 5 (6) today. | 9×: so that confirming is the normal path and a wrong gamble costs something. Experiment timers had been rejected because with them a wrong gamble cost nothing. Tamsin: "confirming would be the normal approach". 5×: part of the rebalance. Its length in turns follows the Space price. |
| **The SS FTL Drive** | 1,500 Production (v3.55, v3.77). Left out of victory until 14 Oct, then counted as 4 turns (5 average), one fewer for Warp, Wormhole and Plenum, plus a turn to launch. Built from Production since 15 Oct, 18:29: about 8 turns (10) at v3.122's prices, 10 (12) since v3.123. | Tamsin, 14 Oct: the Drive and the final assembly "need to be accounted for"; 15 Oct: "we've not been accounting for the production cost of the SS parts in our benchmarks so far". |
| **The signature pools (W18)** | entry and pool rows 2.5× the era's price, capstones 4× (sized 10 Oct; priced in the simulator 14 Oct) | At 1× the phase would buy 15–18 rows of a field, far too many. At 2.5× a civilisation finds 6–8 of about 10. |
| **Rows that host a test** | Deciders at 1× in W18's design. The three build rows that also host a condition (Macroscopic Quantum Control, Exotic Matter Engineering, Current Rigging) at 1× too (lever a, 13 Oct). | Conditions on 2.5× build rows meant that confirming required doing their engineering first. |
| **Each method's own rows** | <br>• **Wormhole**: Transformation Media 2.5× (13 Oct) → 4× (round one). <br>• **Warp**: Superconducting Energy Storage loses its Smart Grid prerequisite; at 1× in round one only. <br>• **Plenum**: Aerospace Industry 1× (round one). <br>• **Hyperspace**: Higher-Dimensional Geometry 1× (round two). <br>• **Tunnelling**: Planetary Data Networks 1× (round two); Quantum Computing 2× (after the final confirmation). <br>• **Elemental Tachyonic**: the Boundary Ring 4× (round two). <br>• **Atomic Tachyonic**: Antimatter Production leaves its build, and the Storage Rings need a power plant instead (round one). | to level the methods' chances (round by round, below) |
| **Grand Endeavours** | 2.5–3× (10 Jul) → 2× (13 Oct) | Tamsin: "roughly-on-par-with to slightly-worse-than the average time to victory without them, but better than the worst case" |
| **Instruments** | 3–6 turns to build (simulated as 5, 6 for the average player; 13–14 Oct) | At 9 turns an instrument delayed certainty in 62% of games. |
| *Proposed, not adopted* | The sync report: Superconducting Energy Storage ×4, the Storage Rings ×5, the Boundary Ring ×6, Space ×1.1. With the funded-focus rule: the FTL rows ×1.4, or the Space era ×1.5. | to level the methods at parity |

## Why the 14 October balance didn't hold

### The chains

Every Space-era row on an FTL build is STANDARD, except the unified theories and Quantum Entanglement Mastery, which are CORE.

- A STANDARD row's idea has to occur before the row can be studied, and the wait begins only when its prerequisites are met.
- A row whose prerequisites are met long before it is needed has usually occurred by then.
- Rows in a chain wait one after another.

The right-hand column is the expert's race at v3.122 against v3.120.

| Method | Space-era rows at the end of its build, in the order they must be found | Race at v3.122 |
|---|---|---|
| Wormhole | (unified theory) → Exotic Matter Synthesis → Exotic Matter Engineering → Transformation Media | +29 to +32.5 turns |
| Plenum | (unified theory) → Celestial Current Survey → Current Sail → Current Rigging | +28.5 to +34.5 |
| Tunnelling | Planetary Data Networks → Quantum Computing → Macroscopic Quantum Control | +32.5 |
| Hyperspace | Optimisation Theory → Higher-Dimensional Geometry | +27.5 to +30 |
| Warp | (unified theory) → Exotic Matter Synthesis → Exotic Matter Engineering; Superconducting Energy Storage alongside, its prerequisites met long before | +15.5 to +16 |
| Tachyonic | the Storage Rings (atomic), or the Re-Tempering Reactor → the Boundary Ring (elemental); Orbital Assembly alongside | +12 to +17 |

- The chain lengths: three rows for Wormhole, Plenum and Tunnelling; two for Warp, Hyperspace and elemental Tachyonic; one for atomic Tachyonic.
- The count explains most of the pattern, but not Hyperspace, which lost as much as the three-row chains.

### How long each step took

These are the expert's median turns from the row before it in the chain to the step's discovery. For these rows, the row before is in almost every game the last prerequisite to arrive. Round two ran 20 games a method; the rest, 60 a cell.

| Step | Round two (W16 on) | v3.120 (W16 dropped) | v3.122 (window doubled; Space ×2) | v3.125 | v3.125 with W16 put back |
|---|---|---|---|---|---|
| Transformation Media (Wormhole) | 5–6 | 9–11 | 19–20 | 16–21 | 4–6 |
| Current Sail (Plenum) | 10–12 | 14–15 | 27–30 | 16–19 | 7–8 |
| Current Rigging (Plenum) | 2 | 6 | 10–12 | 8–10 | 3 |
| Quantum Computing (Tunnelling) | 6–7 | 14 | 20 | 17 | 5 |
| Macroscopic Quantum Control (Tunnelling) | 2 | 6 | 18–19 | 10 | 3 |
| Higher-Dimensional Geometry (Hyperspace) | 1–2 | 7–9 | 19–22 | 13–17 | 2 |

- At round two every method's build finished within a 7-turn band (turns 280–287 for the expert).
- v3.122 also priced the Space era at ×2, so part of its lengthening is study, not waiting.

### Why the window's length matters

- **A shorter window doesn't make ideas go stale more often.** The chance each turn is set from the window's length, so that 85% of STANDARD ideas occur within their window and 15% don't, whatever its length (§1.2). What the length changes is how soon they occur:

  | A Space-era STANDARD idea's window | Chance a turn | Mean wait, if it occurs | Mean wait, counting a stale idea's rediscovery |
  |---|---|---|---|
  | 14 turns (until v3.122) | 12.7% | 4–5 turns | 6–8 turns |
  | 28 turns (since v3.122) | 6.6% | 9–10 turns | 13–14 turns |

- **A stale idea costs more under a long window.** It is lost only when its window closes, and rediscovery on demand (10% a turn for each thing waiting on it) starts only then.
- **Only rows whose windows open shortly before they are needed wait at all**, and those are the steps in a chain. A row that opens long before it is needed has occurred or gone stale by then, whatever the window's length, and a stale one comes back by rediscovery in either case.
- **So a shorter window helps the deep chains most.** It saves them a few turns a step, and saves Warp's and Tachyonic's early-opening rows almost nothing, so the methods draw together.
- **The window doubled in v3.122 as a side effect.** Windows are half an era, and the redraw made the Space era 56 turns instead of 28. Its effect on the FTL race wasn't looked at when it was made.

### Putting the old conditions back, one at a time

Diagnostic runs on scratch copies of v3.125, to find out what each change since round two explains. None is a proposal, and nothing was changed in the design or the simulator's defaults. Each ran on all 15 victory conditions with the players as they were (2,700 games, none unfinished); the spread is measured at victory.

| Put back on v3.125 | Spread | Victory (305 / 305 / 380) |
|---|---|---|
| nothing | 9.7 | 304 / 307 / 381 |
| W16 as the simulator had it, with rivals made under it | **2.9** | 295 / 299 / 372 |
| W16 as written in §4 until v3.120 (a funded focus keeps its Space-era window open) | 9.7 | 304 / 307 / 380 |
| the 14-turn Space-era window | 6.7 | 301 / 302 / 376 |
| the old era timing (the era model for every era) | 6.6 | 307 / 308 / 384 |
| the old rival pool | 8.0 | 306 / 310 / 385 |
| the old expert, without the premium cap | 10.7 → 7.7 for the expert alone | |
| Endeavours on ideas under study | 10.9 | 304 / 311 / 387 |
| the Space era at ×0.8 | 9.7 | 300 / 303 / 374 |

- W16 alone puts the methods back in line, but it makes the science victory 6–10 turns shorter than base Civ V's.
- The 14-turn window does about a third of it, inside the limit. The old era timing does about as much as its window.
- The rivals and the expert's cap are smaller parts. The Space price and Endeavours on ideas under study change nothing.
- The Endeavour fault was never put back.
- Of these, only the window's length is a design choice. The old pool, the simulator's W16 and the old expert were features of the old measurements, not levers.

### What the measurements assumed

**The target.**

- 13–14 October: about 295 for a good economy and 360–375 for an average one.
  - They came from a note in the era model that "the fork's eras run about a tenth shorter" than base Civ V's 320 turns.
  - That note predates v3.108, which had set the fork's game length to base Civ V's at every skill level, and W7 itself cited 320. Claude misread the note as current on 13 October.
  - No source was found for 360–375.
  - The 5× prototype and the ×0.8 Space price were set to reach these targets.
- 15 October: about 320 / 400, base Civ V's whole-game length by the era model. v3.122 came out 3–12 turns over it.
- Since v3.123: **305 / 380**, base Civ V's science victory raced on the same income (`base_race.py`), within 5 turns either way.

**How victory was counted.**

- Until 14 October, 10:38: the race's finish (certainty and the build) plus the prototype, counted as 9 turns (11 for the average player).
  - Before 20:56 on 13 October, times ran from the player's first Space-era discovery rather than from the start of the game.
- From 14 October, 10:38: plus the Drive (4 turns, 5 average, one fewer for Warp, Wormhole and Plenum) and a turn to launch. The prototype was counted as 5 turns (6) from 10:39.
- Since v3.122 (15 October, 17:54), `victory.py` prices the prototype at 5× the Space price, with any premium, from the income at the finish. Since 18:29 it also builds the Drive from Production.
- Counted this way, the final confirmation's games give 300 / 311 / 386, which would put the novice and the average player outside today's limit.

**The players.**

- The expert was retuned at v3.122: it never targets a row above ×2 premium, and it Endeavours only the last thing its race waits on. Its unified theory moved from about turn 230 to 250.
- The novice's and the average player's Endeavour rule never ran as scripted; they used the naive rule throughout (found 16 October).
- Every player decided partly on information the screens don't show, such as whether an unrevealed idea had occurred (found 16 October).
- Until 14 October the runs did not fix Python's hash seed, which changes some of the weaker players' choices.

**The rivals.**

- Until v3.122 every run replayed one pool of rivals made on 13 October at 15:55–15:59, before round one.
  - Its rivals never held Transformation Media.
  - At the final confirmation its diffusion completed 47–75% of the weaker players' Hyperspace, Plenum and Tunnelling builds; at round two, a third at most.
- Since v3.122, rivals are rebuilt for each setting, ten games a method, so their sampling alone can move a method by a few turns.

**The simulator's rules.**

- W16 as simulated made a Space-era STANDARD idea occur at once if the player was pursuing it. For the novice, that meant every such idea in its funded field.
- In Claude's reading, this resembles W16's first version more than the rule written in §4:
  - On 2 October the first version had rows on a proposed hypothesis's path "roll as CORE does" (the direction document's words).
  - Tamsin replaced it the same day with the funded-focus window that §4 carried until v3.120.
- The difference was recorded on 14 October (`discovery_workshop_report.md`). Its pooled cost was measured: 6 turns for the expert, 1 for the novice, 2 for the average player. Its cost to each method was not.
- Every measurement until 14 October, 20:29 also had the Endeavour fault.

## Round by round

### Before October: one hidden method per world

- **13 February.** Tamsin's brief: "Only one method of ftl should actually be available in any game, and part of the challenge of a tech victory will be working out which method is actually going to work, based on what you've learned of the laws of physics …"
  - The next day the routes were checked for balance, and every FTL prerequisite became CORE or STANDARD (Guarantee Rule 2).
- **10 July.**
  - Grand Endeavours arrived, with the FTL launch as the final one, at 2.5–3×.
  - The FTL method became a World Truth (FQ1).
  - v3.17 made Tunnelling atomic-only and added the Plenum Drive for elemental worlds. The four methods found in both kinds of world are reached through the same capability primitives in each.
  - None of this was simulated.
- **23–24 September.**
  - v3.55 made the science victory an FTL ship. Tamsin: "honestly the FTL victory is the intended path".
  - v3.77 set the ship at 4,500 Production, as in base Civ V, with the SS FTL Drive at 1,500 and exotic components giving +15% to the Drive only.
- No FTL race was measured before 2 October.

### 1–2 October: the era redraw and the re-audit (v3.108, v3.110, v3.111)

- **What triggered the re-audit (1 October, about 20:40).** Four rows that Warp and Wormhole need had only atomic prerequisites. Tamsin: "we need to do a dedicated re-audit and fix pass on the FTL methods".
- **v3.108 (1 October, about 21:10).**
  - Tamsin: "tune it for the same game length as the base game at each skill level".
  - The eras were redrawn to an even pace, for games of 262 / 320 / 396 turns (a strong, a good and a casual player).
  - The Space era came out at 29 turns. Tamsin left it provisional until the re-audit.
- **The audit (2 October, 30 runs a method).**
  - Atomic builds completed on turns 282 (Tachyonic) to 301 (Wormhole).
  - Elemental worlds finished 15–35 turns early, because their FTL rows hung off Unified Field Theory, two steps short of Quantum Gravity.
  - Elemental worlds also had no negative signals.
- **v3.110** added Plenum Gravitation and elemental routes.
- **v3.111** added the evidence map: every method can now be ruled out in both kinds of world.
  - Wormhole is decided by Black Hole Thermodynamics and Closed Timelike Curves.
  - Plenum's sail moved to Nanotechnology.
- **Result.**
  - Each elemental method finished within a few turns of its atomic mirror.
  - Tachyonic still completed its prerequisites about 20 turns before Wormhole.
  - Evidence came early: elemental Tachyonic's first signal arrived on turns 235–242.

### 2–13 October: the redesign (the direction document)

**Why it happened.** Tamsin, 2 October: "how is it that the Tachyonic question is decided so early? I picked the FTL methods ... because it's a question that real-world physics hasn't yet solved ... Surely all of the indicators for which method is viable should be Space era". Thinking the puzzle through as a player also showed that the hints didn't lead to decisions, and that there was little real choice about when to commit. The planned v3.112 was held back and the direction document opened.

**The decisions** (W1–W19, mostly 2 October):

- **W1.** Evidence comes only from Space-era experiments.
- **W2.** A prototype Grand Endeavour, which can be committed before certainty (the Hail Mary). It runs its full length, costs more than any experiment that could disprove its method, and refunds nothing.
- **W3.** No report misleads.
- **W4.** What builds a method is separate from what proves it.
- **W6, W10, W11.** Hypotheses sit on an FTL screen that shows facts, not advice.
- **W9.** Power: one advanced fission plant's worth, for Warp, Hyperspace and Tachyonic only. It is flavour, not a balance lever.
- **W14.** Three conditions per method (13 October). With two, an atomic Wormhole world had only two valid truths, which would give it away.
- **W15.** Shapes vary but totals are balanced. The prototype has one flat cost, and confirming is the normal path.
- **W16, bad luck.**
  - Tamsin, 2 October: no science civilisation should be "blocked by hitting the 15%-ish chance that you don't discover one of the techs on the critical path", without making the path CORE.
  - The first rule: every row on a proposed hypothesis's path behaves like a CORE row for a civilisation funding it, with no occurrence window, so even a long-closed window re-opens.
  - Replaced the same afternoon by Tamsin's rule: a Space-era row's window stays open while its focus is funded.
- **W17.** Tamsin: "make the theory easier on average than the practise". The target was 10–15 turns from the unified theory to certainty; the length target was later dropped.
- **W18** (Tamsin, 2 October; sized 10 October; designed by 13 October). A wider Space era, steered through a signature field for each method:
  - Energy Systems (Warp), Materials Science (Wormhole), Mathematics (Hyperspace), Computing (Tunnelling), Nuclear Physics or Thermodynamics (Tachyonic), Aeronautics (Plenum).
  - Pools of about 10 rows at 2.5×, capstones at 4×, deciders at 1×.

**The prototype's size.**

- The first runs (2 October) used 3×, which took 2–4 turns.
- Experiment timers with a 6× prototype were rejected the same afternoon, since with them a wrong gamble cost nothing. Tamsin: "confirming would be the normal approach".
- A 9× prototype, about 12 turns, was recommended, so that waiting to confirm is the better bet unless a rival is close.

**The first measurements.**

- FTL took about 45 turns of the Space era, against its provisional 29.
- Without W16, 22–75% of games could not build a given method; with it, none were locked out.
- On 13 October about 40% of lone civilisations still could never build their method. That led to:
  - diffusion;
  - the 10% glimpse;
  - Endeavours at 2× (Tamsin: "roughly-on-par-with to slightly-worse-than the average time to victory without them, but better than the worst case").

**13 October.** Only 82–90% of games reached certainty. The fixes:

- **Levers a, b and c.** The three build rows that host a condition at 1×; Nanotechnology made CORE; elemental exotic matter reachable through Nanotechnology too. Certainty then came in 96–97% of games.
- **Instruments** (Tamsin's idea). A measurement test unlocks a national wonder whose completion answers it, pencilled at 3–6 turns to build.
- **Dark Energy Understanding** beside Dark Matter Identification, not behind it.

### 13–14 October: the balance rounds

**The standard.**

- Tamsin, 13 October, 19:09: "The methods don't need to be exactly the same, they just need to be close enough that none of them have a greater than random variance advantage or disadvantage compared to other victory methods. So long as the goal being warp doesn't make it massively harder to beat a diplomatic or cultural player, I'm okay."
- At 22:10: "we need to keep the balance in mind for every skill level".
- It was measured as each method's chance of beating its world's field (40–60% counts as balanced) and its turns from the field.

**Wormhole's engineering row** (18:48). Tamsin, 18:47: "I think Wormhole should have an engineering row outside its tests".

- Wormhole had been fastest: in 80–88% of games nothing was left to build after certainty.
- Warp had been slowest, still building 8 turns after certainty.
- The new row was Throat Stabilisation (now Transformation Media), at 2.5×.

**The benchmark players** (evening):

- the expert, who knows the prerequisites and heads straight for the unified theory;
- the novice, who follows the screens;
- the average player: the novice on four-fifths of the economy.

The "current" design measured 296 / 303 / 378, spread 4.6. For the weaker players Wormhole won 67–85% of races, and Warp as few as 16% (atomic world).

**Round one** (23:33; run in 9 of the 15 cells):

- Changes:
  - Wormhole's row at 4×.
  - Warp without the Smart Grid, its storage at 1×.
  - Aerospace Industry at 1×, since Plenum was slow for every player.
  - Atomic Tachyonic without Antimatter Production.
- Result: 294 / 301 / 376, spread 3.6.
- Warp overshot (67–82% for the expert), and atomic Hyperspace and Tunnelling showed up slow.

**Round two** (adopted 14 October, 08:31):

- Changes:
  - Warp's storage back to 2.5×, since the two Warp trims together overshot.
  - Higher-Dimensional Geometry at 1×: the row Hyperspace still builds after certainty.
  - Planetary Data Networks at 1×: Tunnelling's expensive entry.
  - The Boundary Ring at 4×: elemental Tachyonic was too fast for the weaker players.
- Result: 294 / 302 / 377, with 5 / 3 / 2 of 15 cells outside 40–60%.
- **Spread 2.6, where noise alone gives 1.2.**

**The pools** (run at 09:28; Tamsin, 09:26: "add in the wider pools").

- They added 3–5 turns: 297 / 307 / 382.
- They first tilted the methods the way they lean today: in a 20-game check the expert's Warp was 5 turns quick, and Wormhole and Tunnelling 3–4 slow.
- They were kept for incidental discoveries.

**The ship** (counted from 10:38). Tamsin, 09:42: "construction of the SS engine and final assembly of the probe need to be accounted for".

- Until then, victories had ended at the prototype.
- With the Drive and a launch turn: 302 / 311 / 387, 7–27 turns past the target.

**The rebalance** (10:39; Tamsin: "yes, do that"):

- The prototype from 9× to 5×, and the Space era ×0.8: one uniform cut, so as not to disturb the balance.
- Result: 293 / 305 / 380.
- The two cuts were never measured apart.

**The theory gate** (adopted 11:23):

- Each unified theory needs its ontology's great instrument (the Particle Accelerator, the Boundary Furnace), and both became CORE.
- Why: elemental worlds had reached their theory before their Furnace existed, so their first answer took 10–11 turns.
- The theory phase shortened (the novice's from 27 to 18 turns); victory was unchanged.
- The attention boost was dropped, since it was worth only 1–2 turns.

**The final confirmation** (11:24–11:43, 2,700 games):

- 294 / 305 / 380.
- Method medians 288–297, 302–309 and 376–383; spread 3.3.
- The pools' tilt was there in miniature.
- Diffusion from the old rivals completed 47–75% of the weaker players' Hyperspace, Plenum and Tunnelling builds.
- Atomic Tunnelling was 3–4 turns slow for every player, so Quantum Computing went to 2× (11:44; Tamsin: "Make the tunnelling nudge, but don't bother re-simulating everything as it's a small change").
  - It has been in every run since, but its effect was never measured on its own.

### 14 October, afternoon: v3.112 written in

- **13:03.** The redesign was written into the tree (544 rows).
  - The Power Grid was made CORE. As a STANDARD row, its lost idea had left the elemental unified theory unreachable in 8 of 60 Substance Plenum games.
- **13:47–14:03.** A traced game ruled Tachyonic out on turn 240 through an Atomic-era row, against W1.
  - When W14 added third conditions, the tachyonic-sector condition had been put on Standard Model Completion and Complete Catalogue.
  - It moved to new Space-era rows, Beyond the Standard Model and Beyond the Catalogue (1×), whose instruments answer it.
  - Expert spot check: Tachyonic 2–4 turns slower (atomic 292 → 294, Substance 294 → 298).
  - Every later confirmation includes the moved test, but no before-and-after comparison was made for all three players.

### 14 October, evening: three corrections

Two were Tamsin's decisions about the discovery model, written into the design in v3.120; one was a simulator fault. All three changed the numbers round two had been measured with.

- **Glimpse by tier** (Tamsin, 19:05).
  - STANDARD ideas are glimpsed at 10% a turn, UNCOMMON at 3%, RARE and UNIQUE never. Before, every tier was glimpsed at 10%.
  - Checked in the familiar world only: pooled victory moved by a turn at most (292 / 307 / 382 → 292 / 306 / 381).
- **The Endeavour fault** (20:29).
  - While an Endeavour ran, the other foci had shared the whole income on top of the Endeavour's 80%: 180% of income in all, which came to 21–30% more Insight over a game.
  - Every measurement until then had it, round two and the final confirmation included.
  - Fixed: 294 / 305 / 380 → 299 / 308 / 382.
  - One method broke loose: the average player's Process-world Hyperspace, at 402. It had leant on the extra Insight during long Endeavours.
- **Every tier studied alike once its idea has occurred** (Tamsin, 20:40: "I don't think there's any benefit to rarer breakthroughs being slower to get once they've occurred, then").
  - Effect: 301 / 308 / 382; the Hyperspace outlier was gone; spread 3.5.

### 15 October: the safety net, and W16 dropped (v3.115–v3.121)

- **v3.115.** Sixteen missing enablers. One is on Hyperspace's build: Optimisation Theory now needs the Programmable Computer. Spread 4.4. v3.113–v3.119 changed no other FTL row.
- **v3.120 (12:28; Tamsin, 12:15: "Adopt the package ... Drop w16").** Three changes:
  - rediscovery on demand: a lost STANDARD idea comes back at 10% a turn for each thing waiting on it, FTL prototypes and open questions included;
  - Grand Endeavours only on revealed ideas that have not occurred, in the design and for the simulated players;
  - W16 dropped.
- **Why W16 went.**
  - With rediscovery every game with contacts finished (isolated, all but 2 of 900), so W16 no longer protected anything. It only bought speed.
  - Its written form measured as no rule at all.
- **Effect.** 297–298 / 301–302 / 374–375, none unfinished. The spread rose to 4.8: Tunnelling and Plenum slow, Warp and Tachyonic quick. That is today's pattern at about half today's size.
- **What was missed.** W16's cost was judged on the pooled figure: about 8 turns for the expert. Per method, in the familiar world, it cost the expert:
  - Warp +3.5 turns;
  - Wormhole +11;
  - Hyperspace +7.5;
  - Tachyonic +7;
  - Tunnelling +10.

  At the old era timing this reordered the methods more than it widened the spread, and nobody looked per method. This was Claude's error.
- **v3.121 (13:42).** The design allows Endeavours on ideas under study again, for needs the game situation creates. The simulated players keep v3.120's rule. No row or measurement changed.

### 15 October, 17:54: base Civ V's game lengths (v3.122)

**What changed** (five things at once):

1. Development's last three era boundaries moved to base Civ V's timing. The Atomic era now starts around turn 228 and the Space era around turn 264 on a good economy, instead of about 285.
2. Idea windows follow the new era lengths. A Space-era STANDARD idea's window is 28 turns instead of 14, so it occurs at 6.6% a turn instead of 12.7%.
3. Prices went up: ×1.25 in the Modern and Atomic eras, and ×2 in the Space era, in place of ×0.8.
4. Rivals are rebuilt under each setting, replacing the pool made before round one.
5. The expert was retuned, and `victory.py` prices the prototype from the income at the finish.

At 18:29 the Drive was built from Production too. Tamsin, 18:22: "we've not been accounting for the production cost of the SS parts in our benchmarks so far".

**Why.**

- Development had reached the Space era only after the races, 24–29 turns after civilisations entered it by count. The ahead-of-time premium was taking 36–47% of the Insight spent on Space-era rows.
- Tamsin, 16:14: "I feel like the development thresholds aren't set right if the game is reliably ending before the space era even begins".
- 16:42: "we need to get back in line with civ V game lengths, because that's what cultural and diplomatic victories are balanced against".
- 17:26: "let's go with x1.25/x1.25/x2 for now, and retune the expert".

**Effect.**

- 323 / 328 / 407; with the Drive built from Production, 327 / 332 / 412. That is 3–12 turns over the target of the time.
- The spread jumped to **13.2**: Warp and Tachyonic won 62–78% of races against their field; Wormhole, Tunnelling and Plenum 22–44%.
- The drift was seen in this confirmation and parked as a task (*Rebalance the FTL methods*). Its cause was found only on 16 October.

**Why the spread jumped** (found on 16 October):

- The prices were not the main cause: every price back at ×1 still gives 12.3.
- The doubled window and the earlier Space era exposed the wait on every step in sequence. The ×2 price lengthened their study too.
- The rebuilt rivals no longer finished the deep chains for the weaker players by diffusion.
- The retuned expert reached the unified theory about 20 turns later.

### 15 October: parity with base Civ V's science victory (v3.123–v3.125)

- **v3.123 (20:30).**
  - Changes:
    - the Modern, Atomic and Space prices back to ×1, so the Space era is dearer than v3.112's ×0.8;
    - the Ancient era ×1.5 with its span, and the Primitive span ×1.3, to smooth the opening;
    - v3.122's era timing kept.
  - Why: Tamsin, 19:03: "keeping parity with the length of the base's science victory is an absolute we cannot compromise on".
    - The reference became `base_race.py`: base Civ V's tree raced to a launched spaceship on the simulator's own income, 305 on a good economy and 380 on an average one.
    - v3.122 had run 22–32 turns over it.
  - Effect: 304 / 307 / 380, with the prototype about 4 turns (5 average) and the Drive about 10 (12). Spread 11.7.
- **v3.124 (21:45).** Fewer late breakthroughs:
  - General Relativity merged into Special Relativity as Relativity, which still opens the FTL screen and now proposes Warp, Wormhole and Tachyonic together;
  - Quantum Electrodynamics merged into Quantum Field Theory, which is on every atomic method's theory path;
  - two cuts and five demotions;
  - the simulator began to model Competing Solutions' lock-outs.

  The merges and lock-outs shortened the science victory, so the Space era went to ×1.05: 305 / 307 / 379, spread 11.0.
- **v3.125 (22:51).** Ring Fortress merged into Reinforced Concrete: 304 / 307 / 381, spread **10.1**.
  - For the expert, Wormhole, Tunnelling and Plenum finished 7–13 turns behind their world's field.
  - Warp and Tachyonic finished 4–8 turns ahead.

### 15–16 October: the analyses (nothing adopted yet)

- **The sync report** (`ftl_sync_report_20261015.md`).
  - Recommended:
    - shorten each three-step chain by one step (Transformation Media, with exotic matter validated; Current Rigging; Quantum Computing);
    - price the fast methods' last rows higher: Superconducting Energy Storage ×4, the Storage Rings ×5, the Boundary Ring ×6;
    - raise the Space era to ×1.1.
  - Measured at victory: spread 10.1 → **5.0**, at 303 / 307 / 380 (5,400 games a setting). The prerequisite changes alone give 5.7.
  - It was measured with the players as they then were.
- **The weaker players' Endeavour rule** (16 October, 00:19).
  - The novice's and the average player's "request" rule had never run, at round two or since; they always used the naive rule.
  - Run as written (`ENDREQ=1`): spread 9.7 → 8.4, at 304 / 306 / 378.
  - The default is unchanged; the question is parked.
- **Why the methods drifted** (16 October; `results/ftl_drift_20261016.txt`): the step times and the one-at-a-time measurements above.
- **The funded-focus rule** (16 October; Tamsin's question). FTL-related ideas occur as soon as their prerequisites are met and their focus is funded (`FTLOCC=1`).
  - With the players as they were: spread 2.6, but 296 / 297 / 369.
  - With the Space era ×1.5 as well: 3.7 at 302 / 303 / 378.
- **Players who see only the screens** (16 October).
  - Tamsin: a player "has no way to know whether it's occurred or not". The expert may know the fixed foundations; the novice only what's on the screen.
  - The benchmark players had been choosing fields on information no screen shows.
  - With visible-information players, v3.125 measures **310 / 312 / 386**, which puts the novice and the average player outside the limit, and a spread of **17.8**.
  - Plenum suffers most: nothing visible sends anyone to Aerospace Industry or Reusable Launch Vehicle until the FTL screen points there.
- **The funded-focus rule with those players:**

  | Setting | Spread | Victory (305 / 305 / 380) |
  |---|---|---|
  | the rule alone | 6.2 | 297 / 299 / 373 |
  | with the FTL rows ×1.4 | **4.7** | 301 / 305 / 380 |
  | with the Space era ×1.5 instead | 7.9 | 303 / 307 / 383 |

  - The price is the Space era's other content: the non-FTL Space-era breakthroughs held at launch fall from 22–24 a game to 13.5–15.
  - The reason: today a player studies a signature field's other ideas while the field's FTL idea waits to occur, and the rule removes that wait.

## Where it stands

**Decisions for Tamsin:**

1. **Which players to balance against.**
   - v3.125's balance and parity rest partly on players who choose fields on information no screen shows.
   - With players who see only the screens (the expert also knowing the fixed foundations), v3.125 is outside the limit for the novice and the average player.
   - Adopting them re-bases every figure.
2. **How to level the methods**, at parity, measured on the chosen players. The options:
   - **Treat the depth.** The sync report's three prerequisite changes, three dearer rows and Space ×1.1, measured so far only with the old players.
   - **Remove the waits in sequence.**
     - The funded-focus rule with the FTL rows ×1.4, measured with visible-information players. It leaves Plenum (+2 to +6) and Tunnelling (+3 to +4) slowest, because Aerospace Industry, Reusable Launch Vehicle and Planetary Data Networks are on their routes but not named on the FTL screen.
     - A shorter Space-era window. It would mean sizing the Space era's windows at less than half the era (§1.2). The 14-turn window measured 301 / 302 / 376 and 6.7, inside the limit, but only with the old players.
     - A W16-like rule. As simulated it is 6–10 turns too short; nothing milder has been measured.
3. **The weaker players.** Whether their Endeavour rule runs as scripted (`ENDREQ=1`), and whether their ties are broken in a fixed order, which would end the hash seed's effect.

**Never measured:**

- the Quantum Computing nudge on its own;
- the tachyonic-sector move before and after, for all three players;
- the 5× prototype and the ×0.8 Space price apart.

**Suggested:** report the methods' spread (`ftl_sync.py`) with every change that touches the late game, before it is adopted. The drift began at v3.120 unnoticed, because W16's removal was judged on its pooled cost alone.

## The lever letters

These are the switches in the records of the rounds. Since v3.112 the document carries the adopted ones (all but x, t and z), and `LEVERS=abcrwgpnyhukqvVm` is the simulator's default; prices come from `prices.py`.

| Letter | What it does | When |
|---|---|---|
| a | the build rows that host a condition (Macroscopic Quantum Control, Exotic Matter Engineering, Current Rigging) at 1× | 13 Oct |
| b | Nanotechnology CORE | 13 Oct |
| c | elemental Exotic Matter also reachable through Nanotechnology | 13 Oct |
| r | Dark Energy Understanding beside Dark Matter Identification, not behind it | 13 Oct |
| w | Wormhole's engineering row (Transformation Media), priced at `WROWX` (4 from round one) | 13 Oct |
| g | Superconducting Energy Storage without the Smart Grid | round one |
| x | Superconducting Energy Storage at 1× | round one only |
| p | Aerospace Industry at 1× | round one |
| n | the Storage Rings need a power plant instead of Antimatter Production | round one |
| y | Antimatter Production out of atomic Tachyonic's build | round one |
| h | Higher-Dimensional Geometry at 1× | round two |
| u | Planetary Data Networks at 1× | round two |
| k | the Boundary Ring at 4× | round two |
| q | the W18 pools: 2.5×, capstones 4× | 14 Oct |
| v | each unified theory needs its ontology's great instrument | 14 Oct |
| V | both great instruments CORE | 14 Oct |
| m | Quantum Computing at 2× | 14 Oct |
| t | the attention boost (dropped 14 Oct) | 13 Oct |
| z | assumed non-FTL pools (measurement only) | 14 Oct |

## Sources

**The design:**

- `design/tech_tree.md`: the changelog, v3.108–v3.126; §2's era table; §4.
- `design/notes/ftl_decisions_digest.md`.
- `design/notes/deferred_tasks.md`: *Rebalance the FTL methods*, *Development's Space threshold and the victory target*, *The simulated players decided what to fund on hidden information*, and *The novice's and the average player's Endeavours never followed their own rule*.
- `design/notes/ftl_sync_report_20261015.md`.
- `design/notes/discovery_workshop_report.md`: W16 as simulated against W16 as written; rediscovery.

**Outside the repository:**

- The direction document, *Direction Document: The FTL Endgame Puzzle* (claude.ai, private; revision 335): the rationale and measurement history for W1–W19.
- The claude.ai transcripts (13 February to 14 October; see `CLAUDE.md`).
- The Claude Code session of 14–16 October, the source of Tamsin's words from 14 October, 19:05, on.

**The simulator's records** (`design/simulator/power/results/`):

- 13–14 October: `method_balance.txt`, `balance_rounds.txt`, `balance_package.txt`, `pools_effect.txt`, `victory_total.txt`, `rebalance_check.txt`, `theory_instrument_gate.txt`, `instrument_build_times.txt`, `balance_final.txt`.
- 15 October: `v3122_confirmation.txt`, `parity_20261015.txt`, `base_vs_fork_20261015.txt`, `v3123_confirmation.txt`, `v3124_confirmation.txt`, `v3125_confirmation.txt`, `ftl_sync_20261015.txt`.
- 16 October: `endreq_20261016.txt`, `ftl_drift_20261016.txt` (every checkpoint's spread, the step times, and the one-at-a-time measurements), `ftl_occ_rule_20261016.txt`, `visible_players_20261016.txt`.

**The switches:** `design/simulator/docs/WORKSPACE.md`.
