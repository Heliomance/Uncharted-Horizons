# Uncharted Horizons

A fork of Unciv (Kotlin/libGDX) that replaces the technology tree with a discovery-based research system: focus areas, breakthroughs, World Truths and an FTL endgame. The game code is still upstream Unciv; so far the work is design, done with Tamsin, whose design it is.

## The hardest design constraint: a science victory takes as long as base Civ V's

**A science victory must take as long as it does in base Civ V, for the same player on the same economy, and never longer. This is absolute.** The fork changes only the research system. Domination, cultural and diplomatic victories are unchanged and balanced against base Civ V's game length, so a longer science victory makes science unviable as a victory condition. (Tamsin, 15 October 2026, after it had been compromised more than once.)

- **Never trade it away.** No other goal outranks it: not the pace of discoveries, prices, the FTL puzzle's feel, incidental discoveries or any lever's elegance. Never offer "accept a longer science victory" as an option, and never call a measurement that runs longer "close enough". If a change you want lengthens the science victory, find what pays the turns back, or drop the change.
- **The reference** is base Civ V's science victory simulated on the same income. `design/simulator/power/base_race.py` runs Unciv's Gods & Kings tree to a launched spaceship, for a player who researches only what the ship needs and builds the Apollo Program and the six parts. On the simulator's economies (15 October 2026) that's **turn 305 on the good economy and 380 on the average one**. Re-run it whenever the simulated income or the ship's construction changes, and use its figures, not the era model's 320, which is base Civ V's whole-tree research time rather than its victory.
- **The check:** every benchmark player's median victory, with the ship's construction costed (`victory.py`), must be within 5 turns of the reference for its economy, either way: the expert and the novice against the good economy's, the average player against the average one's. Games vary, so a few turns' difference is acceptable, but ±5 is the outside limit (Tamsin, 15 October 2026). Parity means matching, so a science victory more than 5 turns shorter is a problem too. Confirm on all 15 victory conditions, and report every victory measurement against the reference.

## The repository is the only memory

Each cloud session starts in a fresh container with a fresh clone of the repository. Anything not committed and pushed is lost when the session ends: tools, results, notes, parked tasks. Commit and push as you go.

**Work goes straight onto `master`.** It's a one-person project, nowhere near release, and Tamsin is happy to work directly on `master` for now, so no pull requests are needed. New sessions clone `master`, so work left only on another branch is invisible to them. If a session is set up on a `claude/*` branch, push its work to `master` as well: fast-forward it, or merge if `master` has moved.

## Where things are

- `design/tech_tree.md`: the design document, and the single source of truth. The GitHub wiki is generated from it.
- `design/notes/deferred_tasks.md`: parked work. Add to it and mark items done there, not in any list outside the repository.
- `design/notes/ftl_decisions_digest.md`: every settled FTL-endgame decision. Read it before touching §4.
- `design/notes/discovery_workshop_report.md`: the candidate discovery model that every measurement since 1 October uses.
- `design/verification-battery/`, `design/simulator/`, `design/wiki/`: the tools. `design/README.md` explains each.
- `docs/Modders/` (`uniques.md`, `Unique-parameters.md`) and `android/assets/jsons/Civ V - Gods & Kings/`: Unciv's unique templates and rulesets, which every effect in the document must be written against.
- `~/.claude/projects/-home-user-Uncharted-Horizons/previous-chats/` (outside the repository): the transcripts of the design conversation on claude.ai, 13 February to 14 October 2026, with a README, a summary of its last stretch and `search_transcripts.py` (run it with `python3 -I`; `--who human` finds Tamsin's own words). Search them before saying what was or wasn't decided. They stay out of this public repository. **If the folder doesn't exist, for any reason (a new session, or a fresh machine under this one), ask Tamsin for the zip** and unpack it there.

## Changing the design document

1. Edit `design/tech_tree.md` and add a changelog entry with the next version number. The wiki takes its version from the newest entry, and refuses to publish an older one.
2. Run the battery: `python3 design/verification-battery/battery.py design/tech_tree.md`. A change is done only when the battery is clean apart from known, recorded failures. Compare its tier tally before and after.
3. Run `python3 design/wiki/build_wiki.py --check`. It fails on a broken link, or on a section it has no page for.
4. Commit and push to `master`. The *Publish design wiki* workflow updates the wiki within a minute or two; check its run in the Actions tab if a change doesn't appear.

Follow the document's own rules, in §7.0 (*Notation in the Prerequisites column*, *Filter discipline*) and §1.2.

## Simulator

- **Which tree it measures.** The design document itself, `design/tech_tree.md`, as it stands in the checkout. Runs patch a private temporary copy (`scratch_run.sh`) and never touch the document.
- **Standard run:** `bash design/simulator/power/runcell.sh <world> <method> <suffix>`: 60 games by the expert player on the finalised design. The agreed levers and `WROWX=4`, the discovery model's safety net (`REDISCOVER=0.1 W16=0`, v3.120), `ENDUNOCC=1` (the simulated players never Endeavour on ideas under study, which the design allows since v3.121), and v3.122's era timing and late prices (`DEVENDS`, `WINTURNS`, `MODERNPRICE=1.25 ATOMICPRICE=1.25 SPACEPRICE=2`) with rivals made under them (`POOLTAG=122`) are defaults (`design/simulator/power/defaults.py`), so pass `VAR=value` after the suffix only to try a variant (`LEVERS=` switches every lever off). A variant that changes prices or eras needs rivals made under it: `make_pool.sh <world> <tag> VAR=value ...`, then `POOLTAG=<tag>`. `runnov.sh` and `runavg.sh` take the same arguments for the novice and average players. A cell plays its games on every core: about 7 seconds for the expert on four. `compare_settings.sh` runs every player and method of a world under a setting (about a minute) and `victory_table.py` compares settings. Size a check to the question, and say what it will run before a large batch. The conventions and switches are in `design/simulator/docs/WORKSPACE.md`.
- **Paths.** The scripts use absolute paths under `/home/user/Uncharted-Horizons/design/simulator`. Anywhere else, run `python3 design/simulator/relocate.py` first.
- **Results** go in `design/simulator/power/results/`. Report how many games failed to finish whenever you report engineering or victory times.

## Setup

`.claude/hooks/session-start.sh` installs `json5` in cloud sessions.

The tree viewer's browser tests (`design/simulator/power/test_*.py`) also need `pip install playwright==1.56.0`, the version that matches the Chromium preinstalled at `/opt/pw-browsers`. They load the design document; `test_stored.py` also reads `/tmp/layout_v3.109.json`, so copy `design/simulator/power/layout_v3.109.json` there first.
