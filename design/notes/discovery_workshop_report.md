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

## Files

`power_tools/harness2.py` — the harness (models, routings, options, accounting); `harness2_results.json`, `efficiency_tests.json`, `catchup_tests.json`, `premium_sweep.json`, `candidate_summary.json` — the results above; `eramodel.py` — the calibrated era model.
