# The simulator in the browser (15–16 October 2026)

Two prototypes for Tamsin, built on the simulator and the design document as it stands (the bundle records its version):

- **The replay viewer** (`dist/replay.html`) plays a simulated game's turn-by-turn log and shows, turn by turn, what the research screen and the FTL screen looked like to that player.
- **The live game** (`dist/play.html`) is the simulator's engine ported to JavaScript, to play a game by hand from turn 0 to the ship's launch. Each turn you choose what to fund (a focus, a Grand Endeavour, or the FTL prototype) and advance the turn. Knowledge diffusion from five rivals, glimpses, ideas whose moment passes, rediscovery on demand, Competing Solutions' lock-outs, the FTL hypotheses and their tests, instruments, the prototype, the SS FTL Drive and victory against base Civ V's 305 / 380 all work as in the simulator.

Published (private to Tamsin until she shares them): the replay viewer at https://claude.ai/artifact/R6P4DFa7tfXCMD5FQK79Pa and the live game at https://claude.ai/artifact/1v58XZaSDvaArRnkrcAZSY. To update one, rebuild `dist/` and republish to the same link.

Her brief: "don't worry too much about design so long as it's playable, this is just a prototype, but I want to be able to play through the tech tree all the way to victory." Both pages use the research-screen mockup's Unciv look (`../research_screen/`).

## Using them

**The replay viewer** opens on a sample log (an expert in the familiar world playing Warp, a novice in Process playing Plenum, an average player in Substance playing Wormhole). *Open a log file* or *Paste a log* loads another. Play, step, jump to the next event or scrub; the strip chart above shows discoveries per turn, the eras and the race's milestones. *Engine view* shows what the player can't see: ideas under study but unrevealed, every hidden meter, tiers, the World Truth and the working method.

To make a log: `TRACE=<file> WORKERS=1 METHODS=<method>` on `w7f.py`, for one game, through `scratch_run.sh` (see `make_traces.sh`, which makes the three samples). A simulator log ends when the race is won (certainty and the build); the viewer projects the prototype, the Drive and the launch from there as `victory.py` computes them, and marks them as projected. The live game's *Copy the game's log* gives a log in the same format that also carries its own endgame: the prototypes committed and their results (a failed one rules its method out on its turn), the SS FTL Drive and the actual launch, which the viewer shows as they happened.

**The live game** starts with a choice of world, economy (good, or average at four-fifths of the Insight), diffusion on or off, and the game: *Random* (one of the simulator's 300 games, whose number stays out of sight until the launch, since the game fixes the working method) or, for the designer, a typed seed (17000–17299 replay the simulator's games 0–299, and the seed then gives the method away). The working method and the world's truth are drawn with the game, as the simulator draws them, and stay hidden outside the engine view.
- *Fund*: a focus (the radio buttons, a breakthrough's Fund button, or the menu), or Automatic (the field with the most work waiting; the funding card and the menu show which field that is for the coming turn). *Next in line* queues foci for when the funded one runs dry.
- *Grand Endeavour*: select a revealed breakthrough whose prerequisites you hold; the button gives its price and about how many turns.
- *Next turn*, *5 turns*, *10 turns*, *To the next event*, and *Fast-forward with the Advisor*, which plays the generalist's choices and then follows the FTL screen's hints, stopping at each milestone of the race. It never commits a prototype for you, and when it stops your own funding choice comes back. On a phone a *Next turn* button stays at the bottom of the screen while the turn bar is scrolled away.
- *Faster than light* opens the FTL screen once Relativity is discovered: the hypotheses, their questions and answers, the instruments, each build's needs, and *Commit to a prototype*. A prototype committed before you are certain fails if its method is wrong, and returns nothing.
- The game saves itself in the browser after every turn; *Copy a save code* gives a code that *New game* loads. Once the ship launches the screen is read-only.

## How faithful it is

The engine (`engine.js`, with `pyrandom.js` for Python's random numbers and maths) is a line-by-line port of `harness_ftl_e.run()` and `w7f.py`'s game setup for the configuration in use. It reproduces the Python simulator **bit for bit**: the same discoveries on the same turns, every hidden meter and flow to the last bit, on 180 generalist games across the three worlds and both economies, and on 60 games driven by scripted human choices (focus changes, foci with nothing to study, Endeavours). The tests are in `test/` (`bash test/run_all.sh`).

What the simulator doesn't model, the prototypes don't either: Endeavours' abandonment decay and spin-offs (§1.5: stopping or replacing an Endeavour loses its progress, and the live game says so), Production, wonders, and instruments' construction beyond a fixed 5 turns (6 on the average economy).

Where the pages go beyond the simulator, or show it differently:
- **The prototype.** A failed prototype rules its method out (§4), which changes certainty and rediscovery's goals from then on, so a game is the simulator's game only up to its first failed prototype.
- **The prototype's time.** The live game funds the prototype with each turn's own Insight; `victory.py` prices its whole duration at the finish turn's income. When the income steps up during the prototype, the live game launches a turn earlier than `victory.py` would for the same finish (3 games in 60 tested; the other 57 match).
- **The FTL screen's hints.** Where two next steps cost exactly the same, the pages always pick the same one (the first in a fixed order). `w7f.py`'s `hint_row` takes `min()` over a Python set, so its choice among equal-cost steps changes with Python's hash seed; every hint the pages give is one of Python's cheapest.
- **What shows on the research screen.** A core breakthrough shows as under study from the turn its prerequisites are discovered: the simulator puts it under study at the start of the next turn, before any Insight is spent, so the turn the player is planning is the first it takes Insight. The engine view marks it "Occurs next turn".

## For Tamsin: things found outside the mockups

- **The novice's and the average player's games depend on Python's hash seed.** `w7f.py` breaks equal-cost ties in set order (`hint_row`, and the novice's Endeavour candidates), and that order changes with `PYTHONHASHSEED`. Identical `runnov.sh` or `runavg.sh` runs can give different games: in 10 average-player Substance games, two hash seeds differed in 3 (one built on turn 383 against 358). So the novice and average parity measurements carry this variance. A sorted tie-break in `w7f.py` would remove it; that is a simulator change for you to decide. `make_traces.sh` now fixes `PYTHONHASHSEED=1` (the value the samples were made under) and records it in each log.
- **The harness's trace didn't record rows first seen in rivals' hands** (`seen` was measured after the diffusion step had added them). Fixed on 16 October in `harness_ftl_e.py` (only the log changes, never the game), and the sample logs remade. For older logs the replay viewer rebuilds them from the rival pool, and warns when the rebuild can't explain every arrival from abroad.
- The hash-seed variance and the weaker players' Endeavour rule (which never ran: `ENDREQ=1`) are parked in `design/notes/deferred_tasks.md`.
- **Two FTL-screen questions for the design** (the pages follow `w7f.py`): the hints use the hidden list of lost ideas, so an unseen idea's moment passing can change a hint, or turn it into "No step towards it can be worked on now"; and a host or build option becoming nameable when it is revealed is not announced as a change to the screen.

## Building

- `bundle.json` holds everything the pages need from the simulator and the document: `cd design/simulator/power && bash scratch_run.sh python3 ../../mockups/sim_web/build_bundle.py`. Rebuild it after the document changes. The effect texts the player reads are cleaned of row ids, the odds and forks of World Truths, edit history, tier notes and Unciv's `<…>`/`{…}` syntax; the document itself is untouched.
- `make_traces.sh` makes the replay viewer's three sample logs (a few seconds).
- `python3 assemble.py` inlines the styles, scripts, font, bundle and sample logs into `dist/replay.html` and `dist/play.html` (single files, as an artifact page needs), plus `dist/*.local.html` wrappers for opening locally.
- `SPEC.md` is the contract the pages were built to: the bundle, the engine's API, the snapshot and the player's visibility rules.
- Tests: `bash test/run_all.sh` (the engine against Python, bit for bit, and the human API), `node test/reconstruct.test.js` and `node test/live_logs.js` (the replay on simulator logs and on live games' logs, turn by turn against the engine), and the pages in Chromium: `python3 test/test_replay.py`, `python3 test/test_play.py`, `python3 test/test_api.py`.
