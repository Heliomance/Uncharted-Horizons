# Simulator web mockups: build spec

Two prototypes for Tamsin (15 October 2026), sharing one data bundle and one research-screen renderer:

1. **Replay viewer** (`dist/replay.html`): takes a turn-by-turn log from the simulator (`TRACE=<file>` on `w7f.py`) and
   plays through it, showing what the research screen looked like each turn, with an engine view of the hidden state.
2. **Live game** (`dist/play.html`): the simulator's engine ported to JavaScript, so that a game can be played in the
   browser: choose what to fund each turn (or a Grand Endeavour), advance the turn and see what happens, with knowledge
   diffusion from rivals and everything else the simulator models, an FTL screen, and a victory at launch.

Her words: "don't worry too much about design so long as it's playable, this is just a prototype, but I want to be able to
play through the tech tree all the way to victory." Playability and fidelity to the simulator come first.

## Files (all under `design/mockups/sim_web/`)

| File | What it is |
|---|---|
| `build_bundle.py` → `bundle.json` | Everything the engine and screens need, from the simulator's own modules (see its docstring). Rebuild with `cd design/simulator/power && bash scratch_run.sh python3 ../../mockups/sim_web/build_bundle.py`. |
| `pyrandom.js` | Python's `random.Random`, bit for bit: MT19937 seeded as CPython seeds it from an int, `random()`, `getrandbits`, `_randbelow`, `choice`, `gammavariate` (all three branches), `choices` (weights). |
| `pysum.js` (or inside `engine.js`) | CPython 3.12+'s `sum()` of floats (Neumaier-compensated), so sums match Python's to the bit. |
| `engine.js` | The engine: `harness_ftl_e.run`'s turn loop, w7f.py's world setup (FTL hypotheses, truths, rivals, rediscovery goals, hints), the prototype, the Drive and victory. No DOM. Runs in Node (`module.exports`) and the browser (`window.UHEngine`). |
| `view.js` | Turns a **snapshot** (below) into the research screen's **view model**, applying the player's visibility rules; also the engine view. Shared by both apps. |
| `screen.js`, `ftl.js`, `style.css` | The research-screen renderer and the FTL-screen renderer (plain DOM, no framework), and their styles. |
| `replay.js`, `play.js` | The two apps' controllers. |
| `src/replay.html`, `src/play.html` | Page templates; `assemble.py` inlines CSS, JS, the font, the bundle and sample traces into `dist/replay.html` and `dist/play.html`, single self-contained files (the artifact sandbox blocks every fetch except files published with the page). |
| `traces/*.json` | Sample simulator logs for the replay viewer (made with `make_traces.sh`). |
| `test/` | Node and Playwright tests: the engine against the Python harness, and both pages played in Chromium. |

## The data bundle (`bundle.json`)

Read `build_bundle.py`. Keys: `version`, `eras` (EO), `foci` [{name, icon}] (names are `str.title()`, as `gen_data.FOCUS`
has them), `rows` {id: {name, focus, tier, era, pre, world, prereq, fx, flav, conj}} where `pre` is gen_data's
prerequisite structure: a list of AND-groups, each a list of OR-options, each option a list of row ids that must all be
held (`prereqs_met = all(any(all(p in have for p in opt) for opt in grp) for grp in pre)`); `worlds` {familiar, Process,
Substance: {ontology, ids (sorted), costmult (rows ≠ 1), compete {alternative: primary}, tiers (overrides), pool [{m, t:
[turn or null aligned to ids]}]}}; `model` (the harness's P and switches); `economy` {'1.0', '0.8': {inc: [...], d:
[...]}} indexed by turn (index 0 unused): the Insight income of that turn and development after it, exactly as the harness
accumulates them (they do not depend on decisions); `ftl` {atomic, elemental: {HOST, COND, CLOSE, BUILD, PROPOSER,
QUESTION, TRUTHS, VARS}, INSTR, INSTRUMENT, OPENS, INSTR_D}; `victory` {protox, p_space, scale, spaceprice, space,
drive {'1.0','0.8': {exotic, plain: [turns by turn]}}, exotic}.

## The engine (`engine.js`)

A faithful port of `design/simulator/power/harness_ftl_e.py`'s `run()` for the configuration in use (`model` Pmom,
`routing` spill, no T model, no URGENT/END_NOW/END_CREDIT/INSIGHT_CUT options), with `w7f.py`'s game setup around it.
Read both files; port line by line. Requirements:

- **Bit-for-bit with Python.** Same RNG streams and call order: `rng = Random(seed)`, `grng = Random(seed*7919+13)`,
  `rrng = Random(seed*104729+7)`; every `sum()` over floats as CPython's compensated sum; Python's `max`/`min` tie rules
  (first maximal in iteration order); dict insertion order where it matters (`pool`, `waiting`, `flow`, `takers`,
  `found`); ids sorted with Python's string order. Python `a ** b` is `Math.pow(a, b)`.
- **Game setup as w7f.py:** truths drawn with `Random(TRUTHSEED=31)`: `for s in range(N*5): m = methods[s % 5]; a =
  rng.choice(TRUTHS[m])`; rivals for game `s`: the pool's games of method `m` in file order, `j0 = (s // 5) * 5`, rivals
  `pm[(j0 + j) % len(pm)]` for j in 0..4, each turn value divided by ECON; `contact_era` Early Modern; the game's seed
  `SEED0 + s` (SEED0 = 17000); `GOALS_FN = ftl_goals` (rediscovery waits on FTL prototypes and open questions);
  `INSTR_D` 5 (good economy) or 6 (average); `CLOCK.turn` set each turn. Allow explicit `method`, `truth`, `rivals`.
- **Players.** `human`: before each turn the UI sets the funded focus, or requests an Endeavour (END_RULE `request`,
  END_MULT 2, allowed on any revealed idea whose prerequisites are discovered, occurred or not — the design allows both
  since v3.121), or runs the prototype; the chosen focus is the active focus even if it has nothing under study (its share
  then spills, as the harness's spill routing does). `generalist`: `TARGET_FN = None` (the active focus is the one with the
  most work waiting), no Endeavours — the reference player for the bit-for-bit test. Optional `advisor` auto-player for
  fast-forward (the generalist's choice, or better).
- **The FTL screen state** (`ftl()`): opens when RC01 is discovered; each hypothesis is proposed when its proposer (`PROPOSER`)
  is discovered and RC01 is held; the unified theory (`CLOSE`) closes the list; for each proposed hypothesis: its
  conditions (question text, host row names, state open / holds / fails / awaiting its instrument with turns left — use
  w7f.py's `knowledge`, `ready_turn`, the MS08 rule), its build needs (each group's options, met or not, and the hint:
  the focus of the cheapest workable next step — port `smart_targets`/`hint_row`/`hint_focus`), alive or ruled out;
  the running results list with turns; certainty (w7f's `status`).
- **The prototype** (§4): the player commits to a proposed, standing hypothesis whose build is complete. It costs
  `protox × p_space × scale × spaceprice × 4^max(0, space − d)` at commitment and takes the funded share each turn like an
  Endeavour (the spread goes on). On completion it works if the method is the true one: then the SS FTL Drive is built in
  `drive[econ][exotic|plain][turn]` turns from Production (research goes on normally), then one turn to deliver and
  launch: **victory**. A failed prototype rules its method out and returns nothing. Report victory against base Civ V's
  reference on the same income: 305 (good economy) or 380 (average).
- **API** (suggested): `new UHEngine(bundle, {world, econ, seed, method?, truth?, rivals: true|false|[...], player, game?})`;
  `setFocus(f)`, `requestEndeavour(id)`, `stopEndeavour()`, `commitPrototype(method)`; `step()` → this turn's events;
  `snapshot()`; `ftl()`; `endeavourQuote(id)` {cost, turns}; `victory`; `serialize()` / `UHEngine.restore(bundle, saved)`
  (seed + options + the list of choices, replayed). Events: discovered (own / diffusion / Endeavour), revealed (glimpse,
  seen in rivals' hands, CORE), moment passed (revealed rows only in the player's log), path not taken, rediscovered,
  focus entered, era entered (by count, §2), FTL changes ("This bears on the question of how to exceed the speed of
  light."), instrument complete, prototype result, Drive done, victory.

## The snapshot (both apps; `engine.snapshot()` and the replay viewer's reconstruction)

The state after a turn, from which `view.js` builds the screen:

```
{ turn, world, ontology, econ, d, inc, share, funded, endeavour: {id, progress, cost?} | null,
  prototype: {method, progress, cost} | null, drive: {method, turnsLeft} | null, victory: {turn} | null,
  have: {id: {turn, via: 'own'|'diffusion'|'endeavour'}}, occurred: [...], glimpsed: [...], seen: [...],
  lost: [...], locked: [...], prog: {id: fraction}, flow: {focus: insight}, events: [...], ftl: {...} | null }
```

`seen`: rows first seen held by contacted rivals (the harness's `diff_since` and `diff_unc` keys); they are Revealed.

## The player's visibility rules (`view.js`), as the earlier mockup applied them (`../research_screen/make_state.py`)

- **Owned**: discovered. **Revealed**: a CORE row whose idea has occurred (its prerequisites are met), a glimpsed idea, or
  a row seen in rivals' hands. Occurring is hidden (§1.2): a non-CORE idea under study but not revealed is not shown.
- Statuses: owned; `studying` (revealed, occurred); `waiting` (revealed, not occurred, not lost: "Awaiting the idea");
  `closed` (revealed, lost: "Its moment passed — only an Endeavour is certain"); `not_taken` (a revealed alternative
  locked out by its primary: "Path not taken"); `unreach` (revealed, prerequisites not all discovered); `endeavour`.
- Never shown to the player: odds, tiers on revealed rows (Rare and Unique appear on owned rows only), meters, window
  lengths, per-focus spread figures (only the funded share and the total spread), unknown breakthroughs, World Truths, FTL
  answers before they are known. Row ids are never shown. Only foci the civilisation has entered are listed (a focus is
  entered when any of its rows is discoverable or owned).
- Owned rows show their effects (`fx`, `flav`); revealed rows show their conjecture (`conj`) if any, otherwise what they
  need and where.
- The era shown is the era entered by count (§2: 5 Ancient, 3 Classical, 3 Medieval, 5 Early Modern, 7 Modern, 6 Atomic,
  4 Space breakthroughs of that era or later); "ahead of its time" appears only in Endeavour prices.
- **Engine view** (a toggle, for Tamsin): everything, marked as hidden: ideas under study but unrevealed, every meter,
  tiers, ideas awaiting with their tier, lost ideas, the World Truth and true method, rivals' holdings.

## Look (both apps)

Unciv's research screen, as the earlier mockup set it (`../research_screen/src/main.js`, `README.md`): a single dark
look, body and surfaces `#000033`, text `#FFFFFF`, secondary `#B3B3B3`, panels `#19263F`/`#252B3E`, accent `#334D80`;
status bodies — owned `#FFD700` fill, `#6B4300` text; studying `#4893AF` fill, `#000033` text; waiting `#0E5C56` fill,
dashed white border; unreachable transparent, dashed grey; moment passed `#1C1C26`, dotted grey, radius 4; path not taken
transparent, dashed `#6A6A8C`; Endeavour `#334D80`, 2px white border. Era bands: past `#FFAF00`/`#782E10`, current
`#0E5C56`, later `#111111`. Font: DejaVu Sans (the subset `../research_screen/canvas/DejaVuSansUH-subset.woff2`, inlined as
a data URI, family "DejaVu Sans UH", fallback `'DejaVu Sans', Verdana, sans-serif`). Statuses differ by fill, border
pattern and glyph, never by hue alone. Must work from a 1440×810 desktop down to a 400-px-wide phone (columns stack; no
horizontal page scroll; 16-px side gutter with `max(16px, env(safe-area-inset-left, 0px))`). Respect
`prefers-reduced-motion`. No `alert`/`confirm`/`prompt` (the artifact frame blocks them) and no downloads (blocked):
export by copying to the clipboard (with a selectable-text fallback); import by file input or paste.
