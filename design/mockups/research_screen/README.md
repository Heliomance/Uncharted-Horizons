# Research screen mockup (15 October 2026)

A proposal for Uncharted Horizons' research screen, styled on Unciv's own research screen and shown in a simulated late
game. The canvas is at https://claude.ai/artifact/S57dnCQWKAh4HqAfB1Hums (private to Tamsin until shared).

## The artboards

| Artboard | What it shows |
|---|---|
| 1 · Turn 226 (`Main.dc.html`) | The screen as it opens: Quantum Physics funded, 250 breakthroughs, Superconductivity (moment passed) selected. Interactive. |
| 2 · Grand Endeavour, turn 231 (`Endeavour.dc.html`) | An Endeavour on Superconductivity occupying the funding slot. |
| 3 · Switching away (`Switch_away.dc.html`) | The confirmation when funding a focus while an Endeavour runs. |
| 4 · One focus (`Focus_view.dc.html`) | Energy Systems chosen: its breakthroughs as cards, with conjectures and effects. |
| 5 · Phone (`Phone.dc.html`) | The same screen at Unciv's Small size, landscape, 44-px rows and buttons. |
| 6 · Status key (`Status_key.dc.html`) | Every status, tag and focus-list state. |
| 7 · Whole board (`Whole_board.dc.html`) | Turn 226 unscrolled: every owned and revealed breakthrough. |

Every artboard except the key is the one component in `Main.dc.html` with a different `view` (and `phone`) prop.

## Design in brief

- **Funding** is a single choice, as a radio button per focus in the left list (Unciv's current-research blue marks the
  funded one). The funding header shows Insight a turn, the funded share (80% after Specialization of Labor) and the
  spread. A Grand Endeavour takes the funded slot; a queue (right-click a focus) says what is funded next.
- **The board** lists every owned and revealed breakthrough by status, newest work first: Being studied, Awaiting the
  idea (revealed, not yet occurred), Not yet reachable, Moment passed (revealed, its window closed: only an Endeavour is
  certain), then the owned history in era bands with Unciv's era-header colours. Statuses differ by fill lightness,
  border pattern (solid, dashed, dotted), shape and glyph, never by hue alone. Filters and collapsible sections keep 250
  rows legible.
- **The bottom bar** is Unciv's Close | description | action. It explains why each breakthrough is or is not progressing
  and what can be done: fund its focus, Experiment, Synthesis, or a Grand Endeavour (offered only for ideas that have not
  occurred).
- **Hidden information** stays hidden: no odds, hidden meters, window lengths, tiers on revealed rows, per-focus spread,
  unknown breakthroughs, World Truths or FTL results.

## Choices the mockup makes on open questions (for Tamsin)

From `build_spec.md` §11, with the review's changes:
- Endeavours only for revealed ideas that have not occurred (the ENDUNOCC package), never to reorder research.
- Status 4 reads "Its moment passed — only an Endeavour is certain", true even though diffusion can still bring it.
- Rows under study show no progress at all (the meter is hidden); tiers appear only as Rare and Unique on owned rows.
- No per-focus Insight figures (they would reveal hidden occurrence); only the funded share and the total spread.
- Experiment acts on ideas awaiting their moment, Synthesis on ideas whose moment passed, with no size of effect shown.
- The queue moves on when the funded focus has no revealed work under study.
- "Not yet reachable" and "Path not taken" are statuses; Dead end, Superseded, Rival, Rare, Unique, FTL and New are tags.
- The era shown is the era entered by count; "ahead of its time" appears only in Endeavour prices.
- Breakthrough IDs are never shown. Only foci the civilisation has entered are listed.

## The data

`make_state.py` takes one simulated expert game (the familiar world, today's rules) at turns 226 and 231 and applies
the player's visibility rules (an idea occurring does not reveal it). `build_data.py` adds what the engine does not
model: Competing Solutions lock-outs and rivals, superseded and dead-ended theories, theory-revealed rows, foci entered
by their "Available from" conditions. `texts.json` holds the player-facing text of every breakthrough, written and
checked by agents against the design document and the hidden-information rules. `requirements.json` is the full
requirement set the screen was built against; `review.json` the five-lens review and its findings.

## Rebuilding

```
python3 build_data.py      # mockup_data.json from the two snapshots
python3 assemble.py        # canvas/project/*.dc.html from src/ and the data
python3 preview.py canvas/project/Main.dc.html out.png --props '{"view":"t231-endeavour"}'   # a local render
python3 dump_texts.py      # bar_texts.txt: every sentence the description bar can show
```
Then publish `canvas/project/` to the canvas URL above (`canvas/font_url.txt` names the uploaded DejaVu Sans subset).
