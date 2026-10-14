# Discovery-model workshop — overnight report

The design document is unchanged: everything here comes from the comparison harness (`power_tools/harness2.py`) and is for workshopping, not yet a proposal to replace the threshold mechanics. The harness runs the familiar world's 503 rows on the calibrated era model (base Civ V's science victory around turn 320), with the document's routing — 80% of Insight to the active focus, 50% before Specialisation of Labour, the rest spread — and a simple but sensible player.

## Headline findings

1. **The Insight losses were the routing's, and one rule removes them.** Spreading the 20% only to foci that have something live cuts the Insight a civilisation loses from about 30% to 1–4%. Most of the loss had been spread going to foci whose discoverable ideas had not yet occurred.
2. **What remains between a model and its calibrated prices is mostly design, not waste:** the prematurity premium (3–9% of attention, intended), pure rate's diminishing returns (about 20%, removable with a linear chance), and the time an idea takes to occur. Breakthroughs become discoverable early — the median just after its era begins, 41% before it — and a non-CORE then waits a median 11 turns for its idea.
3. **The tier rates were right all along.** Among breakthroughs that actually became discoverable, lifetime rates match their targets: STANDARD 85%, UNCOMMON 40%, RARE 9%, UNIQUE 6%. The low headline rates came from rows that never become discoverable, mostly because a rare prerequisite never occurred.
4. **Catch-up is fixed without disturbing the tiers:** an idea *behind* history occurs quickly (its window divided by 1 + 4 × eras behind). A landlocked civilisation gets its Caravel 6 turns after reaching the coast, and 76% of its old Seafaring foundations within 10.
5. **Under a rate model, accelerators are bounded:** the strongest tested moves a breakthrough by under half an era. A **head start** — the meter part-filled when the breakthrough becomes discoverable — is the clearest meaning, and fits the progress model naturally.
6. **A premium of ×4 per era is the right steepness:** it is where arrivals an era or more early disappear, while specialists still earn a real head start (Calculus about 0.45 era early for a Mathematics specialist).
7. **The threshold design keeps its virtues but inherits two structural problems**: its focus thresholds need cutting to about 9% under the document's routing (its running totals assume fields are funded in proportion to their content, which this routing never does), and its one-per-focus cap slows catch-up.

## The candidate configuration

If the rate direction is pursued, this is the configuration the evidence points to:

- **Parallel progress with momentum.** A focus's Insight fills meters for its live breakthroughs, attention favouring lines already under way — so arrivals stagger rather than all maturing together. Progress persists; discovering one thing never sets another back, it frees attention.
- **Price** = the era's price × 4 for every era the breakthrough lies ahead of the civilisation's development, measured by its total Insight on the calibrated curve. A breakthrough behind the civilisation keeps its own era's price, so catching up is fast, as in base Civ V.
- **Tiers as luck in a bounded window.** A non-CORE competes only once its idea has *occurred*: a chance each turn while its moment lasts, sized to the tier's lifetime target. STANDARD windows are half an era; UNCOMMON, RARE and UNIQUE ideas also need history near their era, so their moment truly passes; an idea behind history occurs within a few turns.
- **Routing:** the 20% spread goes only to foci with something live; Insight a focus cannot use spills at once to foci that can.
- **Accelerators as head starts**, stated in the rows as "a head start of half its study" or similar, not as cost factors.
- **Era prices** then need one calibration factor for the model — about ×0.83 on the current figures.

## Thread 1 — where the Insight goes

At the calibrated era prices, before the spread fix:

| Model / routing | Lost to empty foci | Lost to caps or overflow | Recovered | Becomes attention | Premium share of attention | Rate saturation |
|---|---|---|---|---|---|---|
| Pure rate / none | 5% | 13% | 0% | 81% | 3% | 20% |
| Pure rate / spill | 20% | 8% | 11% | 83% | 5% | 18% |
| Pure rate / bank | 9% | 34% | 30% | 83% | 3% | 21% |
| Momentum / none | 8% | 18% | 0% | 73% | 3% | — |
| Momentum / spill | 27% | 12% | 14% | 74% | 7% | — |
| One line / none | 7% | 20% | 0% | 72% | 6% | — |
| One line / spill | 23% | 15% | 15% | 77% | 9% | — |

The calibration factors each model needed are explained by these terms: efficiency ≈ attention share × (1 − premium dilution) × (1 − saturation) — pure rate with no transfer, for instance, 0.81 × 0.97 × 0.80 ≈ 0.63, against its calibrated ×0.58.

With the spread going only to foci with something live:

| Model / routing | Calibration factor | Net Insight lost |
|---|---|---|
| Pure rate / spill (old spread) | ×0.70 | 33% |
| Pure rate / spill | ×0.73 | 1% |
| Pure rate / spill-then-bank, linear chance | ×0.81 | 1% |
| Momentum / spill (old spread) | ×0.75 | 30% |
| Momentum / spill | ×0.77 | 3% |
| One line / spill | ×0.64 | 3% |

Spill-then-bank (spill first, then bank what a just-emptied focus could not place) adds nothing once the spread is fixed: there is almost nothing left to bank. Banking as you described it matters in the threshold model's native form, where it behaves like the base game's overflow; in the rate models it is subsumed by spill-over.

## Thread 2 — catch-up and tier calibration

Momentum with spill-over and the live-foci spread:

| Variant | Calibration factor | Rates among discoverable (CORE/STD/UNC/RARE/UNIQUE) | Caravel after the coast | Old Seafaring foundations within 10 turns |
|---|---|---|---|---|
| As before | ×0.77 | 1.0 / 0.85 / 0.40 / 0.09 / 0.06 | 10 turns | 55% |
| STANDARD windows half an era | ×0.78 | 1.0 / 0.87 / 0.39 / 0.11 / 0.03 | 11 | 63% |
| Compression behind history | ×0.81 | 1.0 / 0.81 / 0.37 / 0.06 / 0.04 | 7 | 73% |
| **Both** | **×0.83** | **1.0 / 0.86 / 0.32 / 0.07 / 0.05** | **6** | **76%** |
| Both, every window half an era | ×0.82 | 1.0 / 0.84 / 0.44 / 0.13 / 0.06 | 7 | 77% |

What still limits catch-up is prerequisite depth — one link of a chain per turn, since a breakthrough found this turn makes its dependents discoverable only the next — and the 15% of old STANDARDs whose idea never occurs, by design. Knowledge Diffusion, which the harness does not model, would add to it.

## Thread 3 — what an accelerator should promise

Paired runs (the same random seed with and without the accelerator); median turns earlier / eras earlier:

| Row | Price ×0.5 | Premium shifted ½ era | Idea twice as fast | Half-filled meter (head start) |
|---|---|---|---|---|
| Calculus (CORE), balanced | +13 / +0.35 | +12 / +0.32 | 0 | +16 / +0.45 |
| Calculus, Mathematics specialist | +4 / +0.12 | +4 / +0.12 | 0 | +5 / +0.15 |
| Crank and Connecting Rod (CORE, on time) | +3 / +0.08 | ≈0 by construction | 0 | +7 / +0.20 |
| Plate Armour (CORE, on time) | +4 / +0.10 | ≈0 | 0 | +6 / +0.16 |
| Bio-Organic Synthesis (STANDARD) | +2 / +0.04 | ≈0 | 0 | +3 / +0.07 |
| Caravel (STANDARD) | +9 / +0.16 | ≈0 | 0 | +10 / +0.18 |

(The premium-shift column for the on-time rows is zero by construction — it acts only while a breakthrough is ahead of history; its first run had a bug that made it a plain ×0.5 price cut, now corrected and re-tested on Calculus.)

- **Nothing here is era-breaking.** The largest effect is under half an era — against 0.4–1.0 era for the threshold model's "whole threshold × 0.5" reading. An accelerator acts only once a breakthrough is discoverable, and only on the wait its price causes.
- **A head start is the most readable meaning** — "what you already know gets you partway" — and the most consistent: it saves a fixed share of the study whenever the breakthrough opens, early or on time. It suits the progress model directly. (The pure-rate model has no meter; there a price cut is the equivalent.)
- **A faster idea does nothing measurable** in this configuration: with compression and half-era windows, these STANDARDs' ideas already arrive within a few turns.
- **So an accelerator does not have a fixed size in eras**, and should not be written as one. "Arrives a quarter-era sooner" is not something a rate model can promise uniformly; "starts half-studied" is.

## The premium's steepness

Momentum with every fix above:

| Premium per era | Calibration factor | Outside own era | ≥1 era early | Earliest | Calculus: balanced / specialist |
|---|---|---|---|---|---|
| ×2 | ×0.85 | 30% | 0.08% | 1.73 eras early | +0.02 / −0.68 |
| **×4** | **×0.83** | **27%** | **0%** | **0.74 era early** | **−0.15 / −0.45** |
| ×8 | ×0.77 | 26% | 0% | 0.62 era early | +0.03 / −0.33 |

## The candidate against the threshold design

| Era | Cadence, threshold / candidate | Turns with 3+ discoveries | Longest dry spell |
|---|---|---|---|
| Primitive | 1.49 / 0.77 | 19% / 4% | 2.3 / 3.2 |
| Ancient | 1.69 / 2.08 | 25% / 37% | 1.6 / 1.7 |
| Classical | 1.01 / 0.92 | 6% / 6% | 2.6 / 3.3 |
| Medieval | 0.83 / 0.91 | 5% / 6% | 3.9 / 4.8 |
| Early Modern | 0.70 / 0.87 | 3% / 5% | 4.6 / 3.8 |
| Modern | 1.04 / 1.55 | 8% / 17% | 3.4 / 1.8 |
| Atomic | 0.96 / 1.24 | 6% / 13% | 3.2 / 2.4 |
| Space | 0.71 / 0.38 | 3% / 3% | 5.2 / 22 (the end of the tree) |

| | Threshold (slack fixed) | Candidate |
|---|---|---|
| Arrivals outside their own era | 37% | 27% |
| Arrivals ≥1 era early | 0% | 0% |
| Calculus, specialist | 0.34 era early | 0.45 era early |
| Landlocked: Caravel / old foundations in 10 turns | 13 turns / 56% | 6 turns / 76% |
| Order decided | at world creation | when each discovery is made |
| Needs its prices or thresholds cut to | ~9% | ~83% |

Two things to weigh: the candidate starts more gently in the Primitive era (0.77 discoveries a turn, against the threshold design's 1.49 — the document wants an opening faster than base Civ V's, which a tech every few turns still is, but the flurry comes in the Ancient era instead); and it has more clumps from the Modern era on (a sixth of turns, against a twelfth), because spill-over lands bursts of spare Insight at once.

The threshold model's slack, incidentally, had a flaw now fixed in the harness: "half an era" was measured in the breakthrough's own era's Insight, and since eras grow several-fold, for a Space-era row that reached back deep into the Modern era — which let rows arrive nearly three eras early. Measured in eras, nothing arrives even one era early.

## What the harness does not model

Knowledge Diffusion; rival civilisations (so UNIQUEs' first-come rule is absent); Competing Solutions' lock-outs; World Truths other than the familiar world; environmental prerequisites (terrain conditions are ignored); the environment-weighted spread; Grand Endeavours; and feedback from discoveries to income (Insight follows the calibrated curve regardless of what is found). Its player is simple: it activates the focus with the most weight waiting, weighting overdue breakthroughs, every turn. The era model's absolute turns rest on the 320-turn anchor and assumptions noted in §7 (cities per era, 1.5 Production per citizen, the ramp's shape, the per-city factor); comparisons between the models are sturdier than any single figure.

## Decisions for you

1. **Direction.** Is the candidate — parallel progress with momentum, prematurity priced, tiers as luck in a bounded window — the model to carry forward, or should the threshold design be kept with its focus thresholds rebuilt for the routing?
2. **The spread rule.** Sending the 20% only to foci with something live is what removes the losses in every model. Is that acceptable as the routing rule — it changes the document's "every qualifying focus is always rolling"?
3. **Accelerators as head starts.** If so, the five existing multipliers and Mycological Knowledge's three would be restated that way (and in the threshold model they would need re-measuring either way).
4. **The Modern-era clumps under spill-over.** A sixth of turns with three or more discoveries. Acceptable, or worth damping — for instance by spilling only a share of the spare Insight each turn?
5. **The gentler Primitive start.** Acceptable given the Ancient flurry, or should Primitive ideas occur faster?

Mycological Knowledge's rewiring (Antibiotics, Nitrogen Fixation, Biogas and Vaccination off its hard gate), its Mushroom Cellar, and the Biogas Plant fix are still pending; they are independent of the model question and can go in whichever way it is settled, with the accelerator wording following your answer to 3.

## Settled since

**Era entry** (v3.97): a small count of breakthroughs from the era or later — 5, 3, 3, 5, 7, 6, 4 from the Ancient to the Space era — replacing the first draft's 8–20, which left entry up to an era behind development. Base Civ V's one-technology rule was measured and set aside: here a Mathematics specialist would enter the Early Modern to Atomic eras 0.8–1.1 eras early. Marked provisional in §2 and recorded as a playtesting lever, since the counts depend on the discovery model's pace.

## Where it stands (14 October 2026)

The workshop stopped when the FTL endgame redesign took over (from 2 October). Every measurement since has run on the candidate configuration above (`design/simulator/power/w7c_cfg.json`: momentum, spill-over, the spread only to foci with something live, ×4 premium per era, STANDARD windows half an era, compression ×4 behind history, calibration ×0.83): the era-entry counts (v3.97), the era redraw (v3.108) and the whole FTL balance (v3.112). So it is the model in practice, while §1.2 still describes the threshold design.

- **Agreed since, to write in with it** (FTL work, 13 October): Grand Endeavours at 2× the price; proximity revelation as a 10% chance, each turn an eligible idea fails to occur, that it is glimpsed (Revealed) instead, so a lost idea can still be pursued as an Endeavour; observational revelation only of what can be seen; and W16's rule that a Space-era idea's moment stays open while its focus is funded (the simulator runs a stronger form; see *Funded windows instead of W16*).
- **Done since:** Mycological Knowledge's rewiring, its Mushroom Cellar and the Biogas Plant fix (v3.98). Only its accelerator wording waits, on decision 3.
- **Stale in the document:** §1.2's example of a multiplier below 1 still cites Loop Quantum Gravity and Bio-Quantum Coherence speeding Tunnelling, removed in v3.112; QM-E23 Current Sail still makes "the final research of the Plenum Drive" cost ×0.5, a clause of the same older kind that v3.112 removed from Tunnelling.

**Missed ideas, re-measured** (`design/simulator/power/missed_ideas.py`; `results/missed_ideas_<world>.txt`). 100 games per setting and world, the workshop's balanced player without Endeavours, played to the end of the tree; figures for the eras before the Space era, where W16 does not reach. The three worlds agree within a row or two; atomic figures:

| Setting (old glimpse rule; see *Recalculated* for the agreed one) | STANDARD ideas lost for good | Rows they alone lock | Still locked if every glimpsed one were Endeavoured |
|---|---|---|---|
| Bare: no glimpse, no contacts (the 2 October sweep's setting) | 17.8 | 24.6 (p90 34, max 56) | 24.6 |
| Isolated, 10% glimpse | 17.8, 15.3 of them glimpsed | 24.6 | 3.9 (p90 10, max 33) |
| Connected: 10% glimpse, five rivals met in the Early Modern era | 4.2, 3.7 glimpsed | 3.8 (p90 9, max 13) | 0.4 (p90 1, max 8) |

- Knowledge diffusion brings back about 19 lost ideas a game for a connected civilisation, nearly all the early ones among them. The harness does not model theoretical revelation (*Reveals* lists), which would give more lost ideas a way back, so these figures are conservative.
- FA03 Selective Breeding is now lost in 18% of bare games (35% on 2 October), in line with STANDARD's 15%. The biggest single gateways: MA09 Statistics and MA06 Probability Theory (about 30 rows each when lost), FA03 (20), CP07 Artificial Intelligence (Narrow) (16–21), TH02 Refrigeration (15), CO11 Reinforced Concrete (12).
- **The glimpse reaches every tier** (settled by decision 7: no glimpses of RARE or UNIQUE ideas, fewer of UNCOMMON ones). 84% of lost STANDARD ideas are glimpsed, but so are 93% of UNCOMMON, 84% of RARE and 80% of UNIQUE ones (isolated, atomic; the harness ignores environmental prerequisites, so it overstates the UNIQUEs). That makes about 20 RARE and 37 UNIQUE breakthroughs a game visible and open to an Endeavour, against §1.4 ("RARE and UNIQUE breakthroughs are almost never revealed by theory: the surprises remain surprises") and §1.5's guards. FTL timings would not move if RARE and UNIQUE ideas could not be glimpsed: every row an FTL method requires is CORE or STANDARD.

**Open decisions** (the five above, with the two the FTL work raised). Proposals, pending Tamsin's decisions:

1. **Direction:** confirm the candidate. Everything since 1 October rests on it.
2. **The spread:** only to foci with something under study, weighted as measured (by what each has under study, favouring overdue work), with §1.3's environment modifiers multiplying that weight (not measured: the harness has no environment). §1.2's "every qualifying focus is always rolling" goes.
3. **Accelerators as head starts:** restate the five multipliers below 1 and Mycological Knowledge's three as head starts; remove QM-E23's Plenum clause.
4. **Modern-era clumps:** accept, and judge in play. Damping the spill-over would change pacing that every FTL timing was measured with.
5. **The Primitive start:** accept, and rewrite *Front-loaded CORE* to describe the Ancient flurry. CORE ideas occur at once, so the Primitive cadence is set by Insight, not by ideas occurring; only cheaper Primitive prices would quicken it.
6. **Missed ideas (new):** keep the bounded window, which gives the tiers their meaning; rely on the glimpse, Endeavours and diffusion to recover missed ideas; reword §1.2's promise that tiers never decide whether discovery is possible. Treat the big single gateways as tree content (the deferred entry's option 1), apart from the model.
7. **The glimpse by tier (new):** glimpse STANDARD and UNCOMMON ideas only, or RARE and UNIQUE ones far more rarely, so the surprises stay surprises.

**The glimpse for UNCOMMON ideas** (provisional 3% a turn; share of missed UNCOMMON ideas glimpsed, isolated): 10% a turn → 90%, 5% → 77%, 3% → 62%, 2% → 48%; STANDARD at 10% → about 85%. RARE and UNIQUE: never. The FTL check below shows the rule leaves victory turns unchanged.

**Decided (14 October 2026, Tamsin):** proposals 1–5 as written above. On 7, UNCOMMON ideas are glimpsed less often than STANDARD ones, and RARE and UNIQUE ideas are never glimpsed. 6 stays open: Tamsin proposes modelling the closing window as fading attention instead of a closing chance. *(Modelled below, then rejected by Tamsin on reflection, 14 October: the closing window stays.)* A breakthrough gets a smaller and smaller share of Insight as it recedes into the past; if it fills, it is still discovered, so missing the window means never filling. Also asked for: the workshop's figures recalculated now that the harness models rivals and diffusion, and a fuller account of the momentum calculation.

**The write-up must also translate** the threshold design's remaining terms. Thresholds, rolls and excess Insight become prices, meters and occurrence. The tier table's columns become each tier's chance of occurring in its moment and the moment's length. The UNIQUE penalty becomes a lower chance of occurring for each UNIQUE held; the harness's flat 6.5% stands in for it. Diffusion's "bonus to discovery rolls" needs a meaning (proposal: the idea occurs to you, or comes back if lost; the larger bonuses add a head start; only the automatic arrivals are measured). Necessity's roll bonus becomes Insight alone. The per-city modifier applies to the price. *Serendipitous accidents* are the spread itself. The RARE and UNIQUE Endeavour prices need revisiting. §2's prices per discovery should carry the ×0.83 calibration the model applies to them.

## Recalculated (14 October 2026): the current tree, rivals and diffusion

Measured with `design/simulator/power/workshop_measures.py`, which rebuilds the workshop's measures (its own scripts were lost) on the harness that models rivals and knowledge diffusion. The setup:
- the current tree (v3.112), atomic world, 60 games per figure;
- the agreed settings: prices as the FTL runs have them (`prices.py`), and the glimpse by tier (STANDARD 10% a turn, UNCOMMON 3% provisionally, RARE and UNIQUE never);
- the workshop's balanced player, played to the end of the tree.

*Isolated* means no contacts. *Connected* means five rivals replayed from the FTL benchmark pools, met in the Early Modern era, as in the FTL benchmarks. Results: `results/workshop_familiar_<isolated|connected>_agreed.json`.

| | 1 October | Isolated | Connected |
|---|---|---|---|
| Price calibration for mid-era arrivals (in use: ×0.83) | ×0.83 | ×0.78 | ×0.80 |
| Median lateness at the prices in use | 0.5 | 0.54 | 0.51 |
| Arrivals outside their own era | 27% | 30% | 37% |
| Arrivals a full era early; the earliest | 0%; 0.74 era early | 0.01%; 1.1 eras early | 0.01%; 1.2 eras early |
| Share of progress paying the premium; Insight unused | 3–9%; 3% | 12%; 0.5% | 16%; 0.2% |
| Lifetime rates among discoverable rows (CORE / STANDARD / UNCOMMON / RARE / UNIQUE) | 1 / 0.86 / 0.32 / 0.07 / 0.05 | 1 / 0.80 / 0.34 / 0.05 / 0.06 | 1 / 0.89 / 0.44 / 0.05 / 0.05 |
| Breakthroughs arriving by diffusion | — | — | 60 a game |
| Landlocked civilisation: Caravel after reaching the coast | 6 turns | 6 turns; never, in 18% of games | 6.5 turns; never, 0% |
| … old Seafaring foundations within 10 turns | 76% | 76% | 79% |

(Reaching the coast as development enters the Modern era reproduces the workshop's 6 turns, the shortest the chain allows at one link a turn. *Old foundations* are the CORE and STANDARD Seafaring rows of earlier eras.)

**The pace by era** (discoveries a turn; turns with three or more; longest dry spell):

| Era | 1 October | Isolated | Connected |
|---|---|---|---|
| Primitive | 0.77; 4%; 3.2 | 0.79; 5%; 3.5 | 0.79; 5%; 3.5 |
| Ancient | 2.08; 37%; 1.7 | 0.94; 9%; 6.1 | 0.94; 9%; 6.1 |
| Classical | 0.92; 6%; 3.3 | 0.80; 6%; 4.2 | 0.80; 6%; 4.2 |
| Medieval | 0.91; 6%; 4.8 | 0.79; 5%; 5.0 | 0.84; 5%; 5.0 |
| Early Modern | 0.87; 5%; 3.8 | 0.74; 3%; 5.1 | 0.97; 8%; 4.9 |
| Modern | 1.55; 17%; 1.8 | 0.92; 5%; 3.4 | 1.08; 8%; 3.0 |
| Atomic | 1.24; 13%; 2.4 | 0.90; 6%; 3.8 | 1.21; 11%; 3.2 |
| Space | 0.38; 3%; 22 | 1.07; 9%; 3.1 | 1.10; 10%; 2.7 |

The era redraw (v3.108) did what it set out to: about 0.8 discoveries a turn in every era. So decisions 4 and 5, taken on the 1 October figures, addressed problems that have since gone. There is no Ancient flurry left to rewrite *Front-loaded CORE* around, and the Modern era's clumps are down from a sixth of turns to a twentieth. With contacts, diffusion adds a fifth to a third more discoveries from the Early Modern era on, and an eleventh of Atomic-era turns bring three or more.

**Accelerators** (median turns and eras earlier, paired by seed; head start ½ against price ×0.5):

| Breakthrough | 1 October, head start | Isolated | Connected |
|---|---|---|---|
| Calculus, balanced player | +16 / 0.45 | +12.5 / 0.32 against +10 / 0.25 | +12 / 0.29 against +9.5 / 0.23 |
| Calculus, Mathematics specialist | +5 / 0.15 | +4 / 0.11 against +4 / 0.11 | +4 / 0.11 against +4 / 0.11 |
| Crank and Connecting Rod | +7 / 0.20 | +7.5 / 0.21 against +3 / 0.09 | +7.5 / 0.21 against +3 / 0.09 |
| Plate Armour | +6 / 0.16 | +8 / 0.21 against +6.5 / 0.16 | +8 / 0.20 against +6 / 0.15 |
| Bio-Organic Synthesis | +3 / 0.07 | +2 / 0.03 against +1 / 0.02 | +1 / 0.02 against +1 / 0.02 |
| Caravel | +10 / 0.18 | +6 / 0.14 against +6 / 0.13 | +5.5 / 0.13 against +5.5 / 0.12 |

Still nothing era-breaking. **Why a head start beats a halved price:** both save exactly the same Insight, but the momentum rule gives a breakthrough attention in proportion to its progress (+0.1). A half-filled meter therefore draws about six times a fresh line's share from its first turn, and jumps the queue in its focus. A halved price starts from nothing. The two differ only where a breakthrough competes with its siblings; with momentum switched off (attention by tier alone) they come out identical: Crank and Connecting Rod +2.5 both ways, Plate Armour +5, Calculus +9.5, the Caravel +7. To make them equivalent, momentum could count only progress earned, not progress granted.

**The premium's steepness** (each at its own calibration):

| Premium per era | 1 October | Isolated | Connected |
|---|---|---|---|
| ×2 | ×0.85; 30% outside own era; 0.08% an era early; earliest −1.73; Calculus +0.02 / −0.68 | ×0.84; 32%; 0.08%; −1.37; +0.16 / −0.54 | ×0.84; 38%; 0.08%; −1.23; +0.08 / −0.53 |
| ×4 | ×0.83; 27%; 0%; −0.74; −0.15 / −0.45 | ×0.78; 30%; 0.01%; −1.0; +0.03 / −0.49 | ×0.80; 36%; 0.01%; −1.04; +0.04 / −0.43 |
| ×8 | ×0.77; 26%; 0%; −0.62; +0.03 / −0.33 | ×0.74; 28%; 0%; −0.89; +0.01 / −0.27 | ×0.78; 35%; 0%; −0.89; +0.03 / −0.30 |

(Calculus: median eras from the start of its own era, for the balanced player and the Mathematics specialist.) ×4 stays the right steepness.

**Era entry** (development on entering the era by §2's counts, minus the era; positive is late):

| | Ancient | Classical | Medieval | Early Modern | Modern | Atomic | Space |
|---|---|---|---|---|---|---|---|
| Isolated | +0.19 | +0.48 | +0.06 | +0.12 | +0.10 | +0.03 | −0.35 |
| Connected | +0.19 | +0.48 | +0.06 | +0.12 | +0.04 | −0.14 | −0.54 |

§2 says entry falls within about 0.15 era of development, the Classical era about a third of an era late. Now the Classical era enters half an era late and the Space era a third to a half early, sooner with contacts. The parked era-entry task suggested 2 for the Classical era; the Space era would want more than 4.

**Missed ideas under the agreed glimpse:** isolated, 17.6 STANDARD ideas lost before the Space era, locking 24 rows (p90 34, worst 55), or 3.8 if every glimpsed one were Endeavoured. Connected: 4.1, locking 4.3 (p90 10), or 0.3. Of the missed ideas, 85% of STANDARD and about 60% of UNCOMMON ones are glimpsed.

## Fading attention (Tamsin's proposal, 14 October 2026)

**The proposal.** Instead of an idea's moment closing, a breakthrough gets a smaller and smaller share of Insight as it recedes into the past. If it fills, it is still discovered; missing the window means never filling. Implemented as `harness_ftl_e.P.fade`, with a choice of clock and of the tiers that fade (removed from the simulator once rejected; the results below are kept).

**What the first forms showed** (atomic, isolated):
- **Every tier fading** makes the rarer tiers common: RARE 0.26–0.51 and UNIQUE 0.24–0.95 of those that open, against 0.05 and 0.06. Without a closing moment their ideas keep arriving, and an old breakthrough is cheap next to a later era's income, so even a small share fills it. Whatever the clock, the rarer tiers need their moments: their rarity is luck. The proposal belongs to STANDARD, the tier the closing window was hurting.
- **The clock matters.** Counted from when the question opened, rows that open early in their era start fading before it ends: 9.7 missed STANDARD ideas a game, locking 18 rows. Counted from the end of the row's own era (the literal "into the past"), rows whose prerequisites arrive late start out stale: Robotics, Genetic Engineering and Miniaturization are missed in 30–40% of games, and the landlocked Caravel takes 11.5 turns. **Counted from whichever comes later** solves both.

**The form that works:**
1. A STANDARD idea's moment never closes. Once its prerequisites are met, the idea occurs by chance each turn as now, however late.
2. Attention to an open STANDARD question fades once it is behind the times. From the later of the end of its own era and the turn it opened, its share halves with every era of development (half-life h = 1 era; half an era behaves much the same).
3. A field works in proportion to its freshest open question, against the freshest anywhere. The Insight it does not use spills to fields with fresher questions.
4. A stalled question can be glimpsed (10% a turn), and so Endeavoured.
5. UNCOMMON, RARE and UNIQUE ideas keep their moments, as now. CORE never fades, nor W16's funded Space-era rows.

**Measured** (60 games each, at the prices giving mid-era arrivals; results `results/workshop_familiar_<setting>_fade_later1.json`):

| | Window, isolated | Fading, isolated | Window, connected | Fading, connected |
|---|---|---|---|---|
| STANDARD found, of those that opened | 0.80 | 0.89 | 0.89 | 0.90 |
| UNCOMMON / RARE / UNIQUE | 0.34 / 0.05 / 0.06 | 0.34 / 0.06 / 0.06 | 0.44 / 0.05 / 0.05 | 0.43 / 0.04 / 0.05 |
| Missed STANDARD ideas a game | 17.6 | 2.9 | 4.1 | 2.3 |
| Rows they lock (p90; worst) | 24 (34; 55) | 2.7 (6; 9) | 4.3 (10; 15) | 1.9 (4; 6) |
| Of the missed, glimpsed | 85% | 94% | 85% | 92% |
| Caravel after reaching the coast; never | 6 turns; 18% | 7 turns; 0% | 6.5; 0% | 7; 0% |
| Prices for mid-era arrivals (in use: ×0.83) | ×0.78 | ×0.68 | ×0.80 | ×0.77 |

**The FTL check** (atomic world, five contacts, 60 games a method; victory median, with games that could not finish out of 300; `results/w7f_familiar_cmp*.json`):

| | Expert | Novice | Average |
|---|---|---|---|
| Old glimpse rule (every tier 10%) | 292 (3) | 307 (3) | 382 (2) |
| Glimpse by tier (decision 7) | 292 (2) | 306 (3) | 381 (6) |
| Fading attention, prices ×0.77 | 290 (0) | 305 (0) | 381 (0) |
| Fading attention, prices as now (×0.83) | 292 (0) | 306 (0) | 381 (0) |

Decision 7 leaves the victory turns where they were. Fading attention, at today's prices, leaves every median unchanged and makes every game finishable for every player.

**The closing window against fading attention:**
- *The window* is simple and legible: an idea's moment comes and goes, each tier's odds are exact by construction, one rule covers every tier, and an idea that never occurs absorbs no Insight. But missing is pure dice: funding a field does not help, which is why the Space era needed W16. A missed STANDARD idea locks its branch unless contacts or an Endeavour bring it back, hardest for isolated civilisations. And it breaks §1.2's promise that tiers decide difficulty, never possibility.
- *Fading attention* makes missing depend on what the civilisation attends to, and nothing is ever locked for good: a stalled question can fill later when nothing fresher competes, arrive by diffusion, or be Endeavoured. Missed STANDARD ideas almost disappear, even in isolation; rediscovering an old question could be a good moment in play; and the FTL balance holds at today's prices. Against it: it applies to STANDARD only, so there are two mechanisms. Insight sinks into stalled half-done questions and more STANDARD rows get found, so keeping the same pace needs research 4% (connected) to 13% (isolated) cheaper. And a stalled-but-recoverable state is harder to show on a research screen than "this moment passed".
- *Not yet modelled:* a tapering chance (the occurrence chance falling gradually instead of stopping), which softens the cliff but keeps ideas lost by dice; and funding a field reviving its stalled questions (`fade_funded=False`).

**Decided (14 October): rejected.** Tamsin prefers not to adopt it; the closing window stays. The fading code has been removed from the simulator (games without it are unchanged, checked byte for byte); its results files stay in `results/`. The open questions it raised were: adopt fading attention for STANDARD? Its half-life (1 era; half an era behaves much the same)? Keep today's prices, as the FTL check supports, or recalibrate for mid-era arrivals? Should funding a field revive its stalled questions?

## Recovery: rediscovery on demand (14 October 2026)

**Tamsin's brief.** STANDARD ideas may sometimes not happen: that is the variance between games, and why they are STANDARD, not CORE. The problem is when chance takes something vital, or locks a whole downstream chain. A glimpse of an idea that has not occurred is also illogical: if an idea is revealed as possible, it has occurred to someone.

**What the glimpse was carrying.** Without glimpses of ideas that have not occurred, FTL games that cannot finish (atomic, 300 a player) rise from 0 / 4 / 0 to 21 / 28 / 28 with contacts, and from 17 / 30 / 16 to 121 / 158 / 131 isolated (expert / novice / average).

**The mechanic, as modelled** (`harness_ftl_e.P.rediscover`, off by default; `REDISCOVER=0.1`):
1. A *lost* STANDARD idea (its window closed before it occurred) that is still discoverable counts, each turn, the things *ready but for it*:
   - each undiscovered breakthrough for which it is the only missing piece (every prerequisite group met by what is discovered or by this idea);
   - each FTL prototype of a hypothesis still standing, once the FTL screen has opened, whose build requirements are all met except those this idea would satisfy.
2. With *n* things waiting, the idea occurs that turn with chance 1 − 0.9ⁿ (10% for one, 19% for two, 27% for three). It then goes under study as normal, at its normal price.
3. A leaf has nothing that can wait on it, so a missed leaf stays missed: the intended variance. The rarer tiers keep their losses.

In history this is multiple discovery: ideas that many lines of work depend on keep turning up. Simplifications: only breakthroughs waiting directly count, not a whole chain behind them; every hypothesis still standing counts once the screen opens, since the simulator does not track proposals.

**Measured, no glimpses of ideas that have not occurred** (atomic, 60 games; every tier studied alike):

| | Missed STANDARD a game (of them, guarding nothing) | Rows locked behind them (p90; worst) | Ideas rediscovered |
|---|---|---|---|
| Isolated, no rediscovery | 17.2 (7.7) | 23.3 (38; 55) | 0 |
| Isolated, 5% a waiting item | 11.4 (8.3) | 3.0 (7; 10) | 11.8 |
| Isolated, 10% | 11.0 (8.9) | 1.4 (5; 7) | 12.5 |
| Isolated, 20% | 10.8 (8.2) | 2.0 (5; 8) | 12.2 |
| With contacts, no rediscovery | 4.0 (1.4) | 3.8 (7; 13) | 0 |
| With contacts, 10% | 2.6 (1.7) | 0.4 (2; 4) | 10.9 |

Rediscovery from waiting breakthroughs alone left FTL games failing on *vital leaves*, build requirements nothing else depends on: ES18 Superconducting Energy Storage (Warp) and RC04 Black Hole Thermodynamics (Wormhole). Counting the prototypes as waiting closed that gap:

| FTL games that could not finish (of 300; victory median) | Expert | Novice | Average |
|---|---|---|---|
| Contacts: glimpses (agreed rule) | 0 (298) | 4 (308) | 0 (382) |
| Contacts: rediscovery with prototypes, no glimpses | 0 (298) | 0 (308) | 0 (382) |
| Isolated: glimpses | 17 (311) | 30 (332) | 16 (412) |
| Isolated: no glimpses, no rediscovery | 121 (307) | 158 (326) | 131 (406) |
| Isolated: rediscovery with prototypes, no glimpses | 0 (312) | 0 (337) | 0 (419) |

The cost is pace for an isolated civilisation: it now researches the chains it used to lose, so its breakthroughs arrive later in their eras (median lateness 0.62, against 0.54). With contacts the pace barely moves (0.52 against 0.51).

**Revealing and Endeavours (Tamsin, 14 October):** if revealing an idea means it has occurred, everything visible is already under study and Grand Endeavours lose their main purpose, which in this model is to bypass occurrence. A reconciling reading, in §1.4's own terms ("Fusion has been a visible target since the 1950s"): *Revealed* means the goal is known to be possible (from theory, a rival's example, or scholars seeing what must be possible); *occurring* means someone has the insight that lets ordinary research progress; an Endeavour is the only route to a revealed goal without the insight. Then occurrence is the luck, rediscovery on demand the automatic safety net, and revealing with Endeavours the deliberate route, and a glimpse reveals the goal, not the solution. The simpler alternative: revealed means occurred, and Endeavours become a timing tool (2× to finish something already under study now) besides Competing Solutions and the FTL prototype. Note: the simulated expert can Endeavour any idea under study that it targets, revealed or not, standing in for theory revealing applications, so the measurements change little between the two readings.

**What Endeavours are worth (measured 14 October, with the Endeavour fault fixed; atomic, 300 games a player).** The simulated players start 8–11 Endeavours a game in the FTL endgame, 85–90% of them on ideas already under study, which is reordering. Against the same games without Endeavours, that costs 3.8 turns (expert), 7.8 (novice) and 9.3 (average) in games that finish either way. Endeavours only pay by rescuing games: without them, 19 / 23 / 22 of 300 cannot finish. The fault had hidden the cost by giving every Endeavour 80% extra Insight, which is why the FTL work found them nearly free. Tamsin's instinct holds: an Endeavour is never worth it just to change the order things arrive in.

**The package that follows** (Tamsin's gameplay brief: control at a price, and no revealed breakthrough left stuck with no explanation): rediscovery on demand (10% a waiting item, FTL prototypes included); Grand Endeavours only for revealed ideas that have not occurred (`ENDUNOCC=1`), never for reordering; glimpses as now.

| Victory median (unfinished of 300) | Expert | Novice | Average |
|---|---|---|---|
| Contacts, as now | 298 (0) | 308 (4) | 382 (0) |
| Contacts, no Endeavours | 293 (19) | 300 (23) | 373 (22) |
| Contacts, package | 296 (0) | 303 (0) | 377 (0) |
| Isolated, as now | 311 (17) | 332 (30) | 412 (16) |
| Isolated, package | 303 (0) | 325 (0) | 404 (0) |

**Does rediscovery make W16 unnecessary?** (Tamsin's question; atomic, 300 games a player, `W16=0` switches the rule off.) The FTL screen's open questions now also count as waiting on their test rows, the same principle as the prototypes; that cleared the isolated stress test's stalls on tests (QP09, QP10, RC11, QP15).

| Victory median (unfinished of 300), with contacts | Expert | Novice | Average |
|---|---|---|---|
| Today's rules | 298 (0) | 308 (4) | 382 (0) |
| Today's rules, no W16 | 303 (14) | 308 (9) | 383 (3) |
| Package, with W16 | 296 (0) | 303 (0) | 377 (0) |
| Package, no W16 | 302 (0) | 304 (0) | 379 (0) |

As a safety net W16 is no longer needed: with rediscovery every game finishes either way. It remains a speed rule. A funded Space-era idea occurs at once instead of at about 12% a turn, which is worth 6 turns to the expert, 1 to the novice and 2 to the average player. Isolated (a stress test only: Tamsin judges full isolation by the Space era practically impossible), the package without W16 is 311 / 334 / 410 with 0 / 0 / 2 unfinished.

**Funded windows instead of W16** (Tamsin's proposal, 14 October). For the whole game, a STANDARD idea's window does not close while its focus is the funded focus. A window that has already closed stays closed (`FUNDEDWIN=1` with `W16=0`; `workshop_measures.py <world> <setting> fundedwin=1`). Atomic, 300 games a player:

| Victory median (unfinished of 300), with contacts | Expert | Novice | Average |
|---|---|---|---|
| Today's rules | 298 (0) | 308 (4) | 382 (0) |
| Today's rules, no W16 | 303 (14) | 308 (9) | 383 (3) |
| Today's rules, funded windows instead of W16 | 302 (14) | 308 (7) | 383 (6) |
| Package, with W16 | 296 (0) | 303 (0) | 377 (0) |
| Package, no W16 | 302 (0) | 304 (0) | 379 (0) |
| Package, funded windows instead of W16 | 302 (0) | 304 (0) | 378 (0) |

The workshop's balanced player, 60 games (`results/workshop_familiar_<setting>_fundedwin.json` and `_redisc10_fundedwin.json`):

| | Missed STANDARD a game (of them, guarding nothing) | Rows locked behind them (p90; worst) |
|---|---|---|
| With contacts | 4.0 (1.4) | 3.8 (7; 13) |
| With contacts, funded windows | 3.9 (1.3) | 4.2 (8; 14) |
| With contacts, rediscovery 10% | 2.6 (1.7) | 0.4 (2; 4) |
| With contacts, rediscovery and funded windows | 2.9 (1.9) | 0.5 (2; 6) |
| Isolated | 17.2 (7.7) | 23.3 (38; 55) |
| Isolated, funded windows | 17.3 (7.7) | 24.1 (37; 44) |
| Isolated, rediscovery 10% | 11.0 (8.9) | 1.4 (5; 7) |
| Isolated, rediscovery and funded windows | 10.8 (8.7) | 1.9 (6; 9) |

Every difference is within the noise, and the pace (tier rates, lateness, era entry) does not move.

**Why so little.** Taken from the engine's accounts (`run.acct`; `ACCT=<path>` in `w7f.py`, and the `funded windows, a game` entry in the workshop's pace measure); the expert over 300 games, the balanced player over 60 with contacts:
- The window runs out on about 19 STANDARD ideas a game for the expert and 22 for the balanced player. With contacts, most of these come back later by diffusion.
- Only one focus of 34 is funded at a time, and no focus holds more than 14 of the 219 STANDARD rows. When a window runs out, its focus is the funded one for 0.6 ideas a game (expert) or 1.4 (balanced player).
- Funding cannot be aimed at the ideas at risk. An idea that has not occurred is unknown, so the player chooses its focus by the work already under study.
- The hold lasts only while the focus stays funded. The simulated players change focus every 4 turns (expert) or 2 (balanced player), and a held idea closes as soon as they move on. Of those held, 0.19 a game then occur for the expert and 0.37 for the balanced player; the rest close.
- A held idea still needs its roll, about 12% a turn in the Space era. W16 as simulated skips the roll.

**W16 as simulated is stronger than W16 as written.** §4 (*Building and Proving*) says a Space-era row's "occurrence window stays open for a civilisation funding its focus". Since the FTL work, the simulator has instead made a Space-era STANDARD row occur the moment it is discoverable, if it is among the player's research targets, whichever focus is funded. So every W16 figure in this report measures the stronger rule: the 6 turns of victory it is worth to the expert, and the 14 / 9 / 3 unfinished games without it. The written rule is the Space-era part of the rule tested above, which did nothing measurable for these players.

**Not modelled:** the simulated players never fund a focus to protect an idea that has not occurred. A human might, when the FTL screen names a goal; that is the case W16's "whoever commits to a field gets there" has in mind. Even then the idea arrives by dice, at about 12% a turn in the Space era. That is close to what rediscovery already gives an idea a prototype is waiting on (10% a turn for each waiting item).

**Open for Tamsin:** adopt rediscovery on demand, with FTL prototypes and open questions counted as waiting? Which W16, if any? There are three choices. The rule as written (a funded focus keeps its windows open) measured as no rule at all for the simulated players, and game-long it barely changes the missed ideas. The simulated rule (an idea the player pursues occurs at once) is a speed rule, worth 6 turns to the expert. Or no W16, with the expert re-tuned back towards ≈295. At what strength (10% a waiting item measured best; 5% and 20% are close)? Retire glimpses of ideas that have not occurred, keeping proximity revelation for ideas under study ("your scholars are onto something")?

## The candidate model, exactly (as the simulator runs it)

From `design/simulator/power/harness_ftl_e.py` (`run()`), with `w7c_cfg.json` and the agreed settings.

**Income is the simulator's abstraction.** In the game, Insight is the civilisation's science output (§1.2: 1:1 with base science), so it grows with buildings, improvements and specialists. The simulator replaces that with a calibrated curve for a good player's economy, the same whatever is discovered. So it cannot show discoveries feeding back into income, and it flatters a beeline that starves the economy (the FTL digest, §6, plans bot games to check this once the fork is playable).

**Development, income and price.**
- *Development* is the civilisation's cumulative Insight placed on §2's era spans: the era's index plus the fraction of its span accumulated (0 at the start of the Primitive era, 8 at the end of the Space era).
- *Income* is fixed within each era: the span ÷ the era's length for a good economy. That gives 5, 18, 48, 114, 330, 853, 1,412 and 1,790 a turn from the Primitive to the Space era, × 0.8 for the average player.
- *Price:* the era's price per discovery (§2) × 0.83 (the model's calibration) × 4 for each era the breakthrough lies ahead of development. "Ahead" is counted from the start of its era, so a breakthrough of the next era costs 4× at the start of the current era, 2× halfway through, and 1× once development reaches its era. Breakthroughs behind development keep their own era's price.
- Effective prices: 3.8, 11.9, 54, 120, 365, 790, 1,138 and 930 (the Space era's × 0.8 included).

**One turn, in order:**
1. **Income.** Income arrives and development advances.
2. **Discoverable rows.** Every undiscovered breakthrough whose prerequisites are all discovered becomes discoverable (each prerequisite group satisfied by at least one option). A discovery takes effect at the end of its turn, so a chain advances one link a turn.
3. **Diffusion.** Contact starts on the first turn the civilisation holds an Early Modern breakthrough. From then, for each discoverable breakthrough that at least half the contacted rivals hold:
   - CORE and STANDARD ones arrive free 10 turns later, once the Printing Press is known (5 turns, once the Internet is).
   - UNCOMMON ones arrive 5 turns later, once the Internet is known.
   - RARE and UNIQUE ones never diffuse. §1.2's roll bonuses before the Printing Press are not modelled.
4. **Occurrence and glimpses.** Every discoverable breakthrough whose idea has not occurred gets its chance (below). If the idea does not occur, a STANDARD one is glimpsed (Revealed) with 10% chance and an UNCOMMON one with 3%.
5. **The player's choice:** an active focus or a Grand Endeavour.
6. **The split.** The turn's Insight is split (below); breakthroughs whose meters fill are discovered at the end of the turn.

**What it means for an idea to occur.** A discoverable non-CORE breakthrough gets no Insight at all, however hard its focus is funded, until its idea *occurs*: the moment someone in the civilisation has the idea. From then it is *under study*, takes a share of its focus's Insight every turn until it is discovered, and is never lost. Occurring is hidden: it does not Reveal the breakthrough.
- CORE ideas occur the turn they become discoverable (and Reveal themselves, §1.4).
- Other ideas have a constant chance each turn through a window that opens when they become discoverable: half their era's length for STANDARD ideas, the whole era's length for the rest. The chance is sized so that the odds of occurring within the window are the tier's: STANDARD 85%, UNCOMMON 40%, RARE 10%, UNIQUE 6.5%.
- An idea whose window passes is lost for good. UNCOMMON, RARE and UNIQUE ideas are also lost once development is more than half an era past the end of their era, window or not.
- **Catch-up:** behind history the window shrinks. Once an idea's era has ended, its window is divided by 1 + 4 × the eras since it ended. The odds stay the same, packed into fewer turns: a Medieval STANDARD idea is 9.6% a turn over 18.7 turns on time, 26% a turn over 6.2 turns half an era late, and 40% a turn over 3.7 turns a full era late.
- **W16:** a Space-era STANDARD idea in a focus the player is pursuing occurs at once.
- A lost idea can still arrive by diffusion, or be completed by an Endeavour if it was Revealed.

| Era (turns) | STANDARD: window, chance a turn | UNCOMMON | RARE | UNIQUE (window: the era) |
|---|---|---|---|---|
| Primitive (29.8) | 14.9 turns, 12.0% | 1.70% | 0.35% | 0.23% |
| Ancient (31.3) | 15.7, 11.4% | 1.62% | 0.34% | 0.21% |
| Classical (31.8) | 15.9, 11.3% | 1.59% | 0.33% | 0.21% |
| Medieval (37.4) | 18.7, 9.6% | 1.36% | 0.28% | 0.18% |
| Early Modern (51.6) | 25.8, 7.1% | 0.99% | 0.20% | 0.13% |
| Modern (60.5) | 30.2, 6.1% | 0.84% | 0.17% | 0.11% |
| Atomic (48.6) | 24.3, 7.5% | 1.05% | 0.22% | 0.14% |
| Space (29.0) | 14.5, 12.3% | 1.75% | 0.36% | 0.23% |

Windows are counted in turns of the good economy's eras, so a slower economy gets the same turns and less Insight in them.

**How the Insight is split each turn.**
1. **The active focus** gets 80% of the turn's Insight (50% before Specialisation of Labour).
2. **The spread:** the other 20% (50%) goes to the other foci that have something under study, in proportion to each one's *waiting*. Waiting is the sum, over its breakthroughs under study, of tier odds × (1 + how far development is past the start of the breakthrough's era). So more open work, commoner work and older work all draw more of the spread. Foci with nothing under study get none.
3. **Within each focus:** each breakthrough under study has a hidden meter, drawn when it first comes under study. Its size is the breakthrough's price × a random factor (Gamma distribution: mean 1, middle half 0.63–1.28) × any cost multiplier.
   - The focus's Insight is shared in proportion to tier odds × (progress + 0.1), with progress as a fraction of the average cost: this is the momentum.
   - Insight becomes progress at the price in force when it is spent.
   - A breakthrough whose share would complete it takes only what it needs and is discovered; the remainder is shared again among the rest in the same turn.
4. **Spill-over:** Insight a focus could not use (nothing under study, or all of it completed) goes to the foci that still have open work and used all of theirs, in proportion to waiting. What they cannot use is lost: 0.1–0.5% of income.
5. **A Grand Endeavour** replaces the active focus. It receives the 80% (50%) share each turn until it holds 2× the breakthrough's price at the time of commitment, then completes.

**A fault found on 14 October.** While an Endeavour runs, the simulator gives the spread the *whole* income on top of the Endeavour's share, 180% in all. That contradicts the code's own comment ("the spread still rolls") and §1.5. Over a game this added 21–30% to the benchmark players' Insight (the expert spends about 39 turns under Endeavours, the novice 28, the average player 35). Corrected (`SPREADFIX=1`; atomic world, 60 games a method), the victory medians move from 292 / 306 / 381 to 296 / 308 / 383, with unfinished games falling from 2 / 3 / 6 to 0 / 2 / 5 of 300. The effect is small because most of the extra spread went to fields the FTL race does not need. Adopted by Tamsin on 14 October; it is now the simulator's default. Pooled over the three worlds, the corrected victory medians are 299 / 308 / 382 (see the digest and the parked re-check).

**Tier odds no longer weight attention** (decided by Tamsin, 14 October: rarer ideas pay for their rarity at occurrence, and gain nothing by being slower to finish). Once an idea has occurred, every tier is studied alike: within its focus, and in its focus's draw on the spread and spill-over (`tier_attention: false` in `w7c_cfg.json`, now the default). Measured: RARE rises from 5% to 7% of those that open; prices for mid-era arrivals ×0.77 instead of ×0.80; pooled victory medians 301 / 308 / 382 with 0 / 7 / 0 unfinished of 900; and the average player's Process-world Hyperspace outlier (402) disappears (383). The simulated player still uses the tier odds when choosing a focus.

**Not modelled:** environmental prerequisites; Competing Solutions' lock-outs; the UNIQUE first-come rule and stacking penalty (a flat 6.5% stands in); theoretical revelation (*Reveals* lists); necessity modifiers; the per-city cost modifier; §1.3's environment weighting of the spread; and feedback from discoveries to income.

**A worked example.** A focus receives 100 Insight a turn. It has three STANDARD breakthroughs priced at 200 with meters of exactly 1: A is 60% done, B 10%, C new.

| Turn | Weights (A / B / C) | Shares of 100 | After the turn |
|---|---|---|---|
| 1 | 0.595 / 0.17 / 0.085 | 70 / 20 / 10 | A 95%, B 20%, C 5% |
| 2 | 0.89 / 0.255 / 0.13 | 70 / 20 / 10, but A needs only 10 and is discovered; the 60 left over is shared between B and C (weights 0.34 / 0.17): 40 / 20 | A discovered; B 50%, C 20% |

So B, already under way, becomes the leading line; C keeps a small share and grows into the next one.

## Files

`design/simulator/power/harness2.py` — the harness (models, routings, options, accounting); `harness2_results.json`, `efficiency_tests.json`, `catchup_tests.json`, `premium_sweep.json`, `candidate_summary.json` — the results above; `eramodel.py` — the calibrated era model.
