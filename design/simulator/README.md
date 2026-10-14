# Uncharted Horizons — research simulator and tools

Everything used to measure the tech tree's research pacing and the FTL endgame: the simulation harnesses, the measurement scripts, every saved result, the Unciv reference data, the tree viewer's sources and the current tree. Packaged on 14 October 2026 from the design chats' workspace. The verification battery is packaged separately, in `verification-battery.zip`.

## Setting up

1. Unpack this folder anywhere.
2. Run `python3 relocate.py` once. The scripts were written for one particular machine's layout, which this package reproduces; this rewrites their paths to wherever you unpacked it. (`python3 relocate.py --check` lists the 175 paths in 89 files it will change, without changing anything.)
3. Python 3.10 or later. `json5` is needed by some data loaders: `pip install json5`.

Tested on 14 October 2026: unpacked into a fresh folder, relocated, then a three-game standard Hyperspace run. All three games reached certainty, the result was written inside the folder, and nothing outside it was touched.

## Layout

| Folder | What's in it |
|---|---|
| `tt.md` | The working copy of the tree, which the harness reads (v3.112). |
| `outputs/` | The canonical saved tree, `tech_tree_v112.md`, and the built viewer, `tech_tree_viewer.html`. |
| `power/` | Every tool and measurement script (87 Python scripts), with their data files. |
| `power/results/` | Every saved measurement (504 files, about 67 MB unpacked). The standard runs need it: they load their rival-civilisation pools from here. |
| `unciv/` | Unciv's Gods & Kings and Vanilla rulesets, its uniques documentation and the derived reference files. |
| `unciv_src/` | Extracts of Unciv's engine source (unit movement, capture, combat, the unique types), used when designing engine-dependent rows. |
| `viewer/` | The tree viewer's sources. `power/build.py` builds them into `outputs/tech_tree_viewer.html`. |
| `docs/` | `WORKSPACE.md`, the full working guide: conventions, the standard settings, what each run measures, and the harness switches. Also the discovery-model workshop report and an example traced game. |

## Running a measurement

The standard run is 60 games of one FTL method in one world type, with every agreed design lever switched on:

    bash power/runcell.sh <world> <method> abcrwgpnyhukqvVm <suffix> EXPFIX=1 ENDFROM=theory WROWX=4 SPACEPRICE=0.8

- **Worlds:** `familiar` is the atomic world. Elemental runs (the Substance and Process worlds) pass that world's name instead, which the runner hands to the harness. I couldn't confirm the exact names from the saved results, which are all atomic runs, so check `worlds.py` and `harness_ftl_e.py` first.
- **Methods:** `Warp`, `Wormhole`, `Hyperspace` and `Tachyonic` in both world types, plus `Tunnelling` in atomic worlds or its mirror, `Plenum`, in elemental ones.
- **Results** are saved as `power/results/w7f_<world><suffix>.json`.
- **A shorter run:** call `power/w7f.py <world> <games> <suffix>` directly, inside `power/scratch_run.sh`, with the same environment variables. `docs/WORKSPACE.md` lists every variable and what it switches.
- **One game, turn by turn:** add `TRACE=<path.json>`, then format the record with `power/trace_table.py`.

`scratch_run.sh` restores `tt.md` from the highest-numbered `outputs/tech_tree_vNNN.md` before every run, so a damaged working copy can't persist. To measure a newer tree, save it there as the next number. Once the design lives in the wiki, assemble the wiki's pages back into one document in the original order first.

## The main scripts

| Script | Role |
|---|---|
| `w7f.py` | The runner: plays N games per method, applying the levers and players. |
| `harness_ftl_e.py` | The simulation engine for the FTL endgame: discovery, focus choice, Endeavours, the theory phase, tests and building. |
| `harness2.py` | The discovery-model workshop's harness, where the candidate model was developed (results in `harness2_results.json`; report in `docs/`). |
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
| `v112_stage1.py` – `v112_stage5.py`, `v112_tachyonic_fix.py`, `thin_batch*.py`, `stage*.py`, `ledger*.py` | The scripts that made past tree versions. They're a record, tied to the versions they edited, not something to re-run. |

## What the simulator can't tell you

Its income depends only on cumulative Insight, never on what has been discovered, and it models no production or military pressure. So it measures the research structure well, but it overrates beelining: an expert who starves its economy loses nothing here. The decisions digest (`ftl_decisions_digest.md`) records this, and the plan to check the benchmarks with bot games once the fork is playable.
