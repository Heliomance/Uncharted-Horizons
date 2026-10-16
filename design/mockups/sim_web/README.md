# The simulator in the browser (15–16 October 2026)

Two prototypes for Tamsin, built on the simulator and the design document as it stands (the bundle records its version):

- **The replay viewer** (`dist/replay.html`) plays a simulated game's turn-by-turn log and shows, turn by turn, what the research screen and the FTL screen looked like to that player.
- **The live game** (`dist/play.html`) is the simulator's engine ported to JavaScript, to play a game by hand from turn 0 to the ship's launch. Each turn you choose what to fund (a focus, a Grand Endeavour, or the FTL prototype) and advance the turn. Knowledge diffusion from five rivals, glimpses, ideas whose moment passes, rediscovery on demand, Competing Solutions' lock-outs, the FTL hypotheses and their tests, instruments, the prototype, the SS FTL Drive and victory against base Civ V's 305 / 380 all work as in the simulator.

Her brief: "don't worry too much about design so long as it's playable, this is just a prototype, but I want to be able to play through the tech tree all the way to victory." Both pages use the research-screen mockup's Unciv look (`../research_screen/`).

## Using them

**The replay viewer** opens on a sample log (an expert in the familiar world playing Warp, a novice in Process playing Plenum, an average player in Substance playing Wormhole). *Open a log file* or *Paste a log* loads another. Play, step, jump to the next event or scrub; the strip chart above shows discoveries per turn, the eras and the race's milestones. *Engine view* shows what the player can't see: ideas under study but unrevealed, every hidden meter, tiers, the World Truth and the working method.

To make a log: `TRACE=<file> WORKERS=1 METHODS=<method>` on `w7f.py`, for one game, through `scratch_run.sh` (see `make_traces.sh`, which makes the three samples). The live game's *Copy the game's log* gives a log in the same format.

**The live game** starts with a choice of world, economy (good, or average at four-fifths of the Insight), diffusion on or off, and a seed (random, or one of the simulator's games 17000–17299). The working method and the world's truth are drawn from the seed, as the simulator draws them, and stay hidden outside the engine view.
- *Fund*: a focus (the radio buttons, a breakthrough's Fund button, or the menu), or Automatic (the field with the most work waiting). *Next in line* queues foci for when the funded one runs dry.
- *Grand Endeavour*: select a revealed breakthrough whose prerequisites you hold; the button gives its price and about how many turns.
- *Next turn*, *5 turns*, *10 turns*, *To the next event*, and *Fast-forward with the Advisor*, which plays the generalist's choices and then follows the FTL screen's hints, stopping at each milestone of the race. It never commits a prototype for you.
- *Faster than light* opens the FTL screen once Relativity is discovered: the hypotheses, their questions and answers, the instruments, each build's needs, and *Commit to a prototype*. A prototype committed before you are certain fails if its method is wrong, and returns nothing.
- The game saves itself in the browser after every turn; *Copy a save code* gives a code that *New game* loads.

## How faithful it is

The engine (`engine.js`, with `pyrandom.js` for Python's random numbers and maths) is a line-by-line port of `harness_ftl_e.run()` and `w7f.py`'s game setup for the configuration in use. It reproduces the Python simulator **bit for bit**: the same discoveries on the same turns, every hidden meter and flow to the last bit, on 180 generalist games across the three worlds and both economies, and on 60 games driven by scripted human choices (focus changes, foci with nothing to study, Endeavours). The tests are in `test/` (`bash test/run_all.sh`).

What the simulator doesn't model, the prototypes don't either: Endeavours' abandonment decay and spin-offs (§1.5), Production, wonders, and instruments' construction beyond a fixed 5 turns (6 on the average economy). On the FTL screen, the hint for where to look next can differ from Python's when two next steps cost exactly the same.

## Building

- `bundle.json` holds everything the pages need from the simulator and the document: `cd design/simulator/power && bash scratch_run.sh python3 ../../mockups/sim_web/build_bundle.py`. Rebuild it after the document changes.
- `python3 assemble.py` inlines the styles, scripts, font, bundle and sample logs into `dist/replay.html` and `dist/play.html` (single files, as an artifact page needs), plus `dist/*.local.html` wrappers for opening locally.
- `SPEC.md` is the contract the pages were built to: the bundle, the engine's API, the snapshot and the player's visibility rules.
