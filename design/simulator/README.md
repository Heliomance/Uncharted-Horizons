# Uncharted Horizons — research simulator and tools

Everything used to measure the tech tree's research pacing and the FTL endgame: the simulation harnesses, the measurement scripts, every saved result, the Unciv reference data and the tree viewer's sources. Packaged on 14 October 2026 from the design chats' workspace, and now kept in the repository beside the verification battery (`design/verification-battery/`). It simulates the design document itself, `design/tech_tree.md`.

## Setting up

1. Python 3.10 or later, and `json5` (`pip install json5`; cloud sessions install it at start-up).
2. The scripts hold absolute paths, kept pointing at `/home/user/Uncharted-Horizons/design/simulator`, where cloud sessions check out the repository. In a checkout anywhere else, run `python3 relocate.py` once; it rewrites them to the folder it's in (`--check` lists the changes without making them).

## Layout

| Folder | What's in it |
|---|---|
| `outputs/` | The built tree viewer, `tech_tree_viewer.html`. |
| `power/` | Every tool and measurement script (92 Python scripts), with their data files. |
| `power/results/` | Every saved measurement (504 files, about 67 MB unpacked). The standard runs need it: they load their rival-civilisation pools from here. |
| `unciv/` | Unciv's Gods & Kings and Vanilla rulesets, its uniques documentation and the derived reference files. |
| `unciv_src/` | Extracts of Unciv's engine source (unit movement, capture, combat, the unique types), used when designing engine-dependent rows. |
| `viewer/` | The tree viewer's sources. `power/build.py` builds them into `outputs/tech_tree_viewer.html`. |
| `docs/` | `WORKSPACE.md`, the full working guide: conventions, the standard settings, what each run measures, and the harness switches. Also an example traced game. The discovery-model workshop report is in `design/notes/`. |

## Running a measurement

The standard run is 60 games of one FTL method in one world, played by the expert benchmark player on the finalised design:

    bash power/runcell.sh <world> <method> <suffix>

- **The finalised design is the default.** Every agreed lever (`LEVERS=abcrwgpnyhukqvVm`), Wormhole's MS17 row at 4× (`WROWX=4`) and the Space era's price at 0.8 (`SPACEPRICE=0.8`) apply wherever a switch isn't set: `power/defaults.py` holds them. To try a variant, pass the switch: `bash power/runcell.sh familiar Warp _test SPACEPRICE=1`, or `LEVERS=` to switch every lever off.
- **Players:** `runcell.sh` is the expert, `runnov.sh` the novice and `runavg.sh` the average player (the novice with a weaker economy); all three take `<world> <method> <suffix>`, and `runall.sh <world> <games> <suffix>` runs every method with the expert. Each wrapper builds in its player's settings: the expert's theory-first beeline (`EXPFIX=1 ENDFROM=theory`), the novice's Endeavours on request (`END=2 ENDRULE=request NOVEND=10 NOVFOCUS=1`), and for every player the 10% glimpse with observational revelation off (`GLIMPSE=0.1 OBS=0`).
- **Worlds:** `familiar` (the atomic world), `Substance` and `Process` (the two elemental worlds). Each has a rival-civilisation pool in `power/results/w7f_<world>_pool.json`, which knowledge diffusion needs.
- **Methods:** `Warp`, `Wormhole`, `Hyperspace` and `Tachyonic` in both world types, plus `Tunnelling` in atomic worlds or its mirror, `Plenum`, in elemental ones.
- **Results** are saved as `power/results/w7f_<world><suffix>.json`.
- **Speed:** a cell's games run in parallel on every core (`WORKERS=<n>` to choose, `WORKERS=1` for one after another; the results are the same). On four cores an expert cell takes about 7 seconds, a novice or average cell 2–3. To compare settings, `power/compare_settings.sh <world> <label> [VAR=value ...]` runs all three players on every method of a world (about a minute), and `power/victory_table.py` tabulates victory turns side by side.
- **A shorter run:** call `power/w7f.py <world> <games> <suffix>` inside `power/scratch_run.sh`, with the player's environment variables (copy them from the wrapper). `docs/WORKSPACE.md` lists every variable and what it switches.
- **Repeatability:** identical runs can differ slightly, because Python randomises string hashing in each process, which changes some tie-breaks: more often for the novice and the average player, rarely for the expert (one game in 60 in one check, with the medians unchanged). Set `PYTHONHASHSEED=0` to repeat a run exactly, and always when comparing two settings.
- **One game, turn by turn:** add `TRACE=<path.json>`, then format the record with `power/trace_table.py`.

**Which tree it reads.** Every tool reads the design document, `design/tech_tree.md`, so a run always measures the document as it stands in your checkout. `scratch_run.sh` copies it to a private temporary file, applies `scratch_patch.py` (the redesign's variant switches; under the finalised switches it leaves the tree's rows and prerequisites as the document has them), runs the command with `UH_TREE` pointing at the copy, and deletes the copy afterwards. The document itself is never modified, and runs in parallel never share a copy. To measure an older version, check it out from git.

## The main scripts

| Script | Role |
|---|---|
| `w7f.py` | The runner: plays N games per method, applying the levers and players. |
| `harness_ftl_e.py` | The simulation engine for the FTL endgame: discovery, focus choice, Endeavours, the theory phase, tests and building. |
| `harness2.py` | The discovery-model workshop's harness, where the candidate model was developed (results in `harness2_results.json`; report in `design/notes/discovery_workshop_report.md`). |
| `harness.py`, `harness_ftl.py` | The earlier discovery-model comparison harnesses (threshold against rate models), kept for the record. |
| `eramodel.py` | Era model: calibrated era lengths, city Production and per-era building loads, the fork against base Civ V. |
| `era_prices.json` | The price per discovery in each era. |
| `prereq.py` | The shared prerequisite parser. |
| `reach.py` | Guaranteed ancestry: whether one row is certain to be discovered before another can be. |
| `gen_data.py` | Row data (focus, tier, era, prerequisite structure, world) for the threshold generator. |
| `worlds.py` | The world sets used in the thinning pass: the familiar world and one alternative per world-truth branch. |
| `generator.py` | The Insight-threshold generator of the original discovery design, run per civilisation at world creation. |
| `balance_*.py`, `theory_phase.py`, `ftl_timing.py`, `victory_total.py` | Summaries of the measurement runs. |
| `trace_table.py` | Formats a traced game as a readable table. |
| `missed_ideas.py` | How much of the tree missed ideas lock under the agreed settings, isolated and connected (`results/missed_ideas_<world>.txt`). |
| `workshop_measures.py` | The discovery-model workshop's measures, rebuilt with rivals and diffusion: pace, tier rates, Insight, missed ideas, era entry, catch-up, accelerators, the premium's steepness, calibration (`results/workshop_<world>_<setting>_<label>.json`). |
| `prices.py` | The agreed design's prices (Space-era price and row multipliers), shared by every script that runs the harness. |
| `compare_settings.sh`, `victory_table.py` | Setting-against-setting FTL checks, and their victory table. |
| `victory.py` | Every tool's victory turn: the race's finish, the prototype priced from the Space price, the SS FTL Drive built from Production, launch. |
| `base_race.py` | Base Civ V's science victory on Unciv's Gods & Kings tree, run on the simulator's income, for comparison with the fork's. |
| `row_survey.py` | One line of data per row for the row survey: tier, era, grants, dependents, the victory rows it must precede, and how often and when each player discovers it. |
| `make_pool.sh` | Rebuilds the rivals that knowledge diffusion replays, under a run's prices and eras (`POOLTAG`). |
| `era_pace.py` | Turns per discovery while development is in each era, beside base Civ V's turns per tech on the same income. |
| `smooth.py`, `smooth_screen.sh`, `smooth_report.py`, `discovery_mix.py` | The era-smoothing pass: settings for a set of era price multipliers, a three-condition screen of them, its victory, era-alignment and discovery-count report, and where each era's discoveries come from (`results/smooth_20261015.txt`). |
| `ledger.py`, `ledger2.py` – `ledger6.py` | The power ledgers: per-city building power by era, which the era model reads. |
| `defaults.py` | Where the tree is, and the finalised design's switches. |
| `v112_stage1.py` – `v112_stage5.py`, `v112_tachyonic_fix.py`, `thin_batch*.py`, `stage*.py` and the other scripts that edit `tt.md` | The scripts that made past tree versions. They're a record, tied to the versions they edited and to the old workspace's `tt.md` and numbered copies, not something to re-run. |

## What the simulator can't tell you

Its income depends only on cumulative Insight, never on what has been discovered, and it models no production or military pressure. So it measures the research structure well, but it overrates beelining: an expert who starves its economy loses nothing here. The decisions digest (`design/notes/ftl_decisions_digest.md`) records this, and the plan to check the benchmarks with bot games once the fork is playable.
