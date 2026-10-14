# Uncharted Horizons

A fork of Unciv (Kotlin/libGDX) that replaces the technology tree with a discovery-based research system: focus areas, breakthroughs, World Truths and an FTL endgame. The game code is still upstream Unciv; so far the work is design, done with Tamsin, whose design it is.

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

## Changing the design document

1. Edit `design/tech_tree.md` and add a changelog entry with the next version number. The wiki takes its version from the newest entry, and refuses to publish an older one.
2. Run the battery: `python3 design/verification-battery/battery.py design/tech_tree.md`. A change is done only when the battery is clean apart from known, recorded failures. Compare its tier tally before and after.
3. Run `python3 design/wiki/build_wiki.py --check`. It fails on a broken link, or on a section it has no page for.
4. Commit and push to `master`. The *Publish design wiki* workflow updates the wiki within a minute or two; check its run in the Actions tab if a change doesn't appear.

Follow the document's own rules, in §7.0 (*Notation in the Prerequisites column*, *Filter discipline*) and §1.2.

## Simulator

- **Which tree it measures.** The highest-numbered `design/simulator/outputs/tech_tree_vNNN.md`. Copy `design/tech_tree.md` there under the new number before measuring a new version.
- **Standard run:** `bash design/simulator/power/runcell.sh <world> <method> abcrwgpnyhukqvVm <suffix> EXPFIX=1 ENDFROM=theory WROWX=4 SPACEPRICE=0.8`. Keep each tool call to one or two runs, about 2 minutes: a run killed by a timeout can't restore the working tree. The conventions and switches are in `design/simulator/docs/WORKSPACE.md`. Its advice about `/mnt/user-data/outputs` dates from the previous environment; here, commit what's worth keeping.
- **Paths.** The scripts use absolute paths under `/home/user/Uncharted-Horizons/design/simulator`. Anywhere else, run `python3 design/simulator/relocate.py` first.
- **Results** go in `design/simulator/power/results/`. Report how many games failed to finish whenever you report engineering or victory times.

## Setup

`.claude/hooks/session-start.sh` installs `json5` in cloud sessions.

The tree viewer's browser tests (`design/simulator/power/test_*.py`) also need `pip install playwright==1.56.0`, the version that matches the Chromium preinstalled at `/opt/pw-browsers`. They load tree versions v108, v109 and v111, which aren't in `design/simulator/outputs/`; point them at the current document first.
