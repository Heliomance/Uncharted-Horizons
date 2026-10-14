# Workspace — Uncharted Horizons (read this first in any new session)

**Since 14 October 2026 the workspace is the repository.** Each session starts from a fresh clone, so anything worth keeping is committed and pushed; nothing outside the repository survives, and there is no restore script. This guide began in the design chats' workspace, and its dated sections below are that workspace's log, kept for the decisions and switches they record. Their commands have been updated for the repository; where they name the old workspace's places, read them as:

| Old workspace | Repository |
|---|---|
| `/mnt/user-data/outputs/power_tools/` | `design/simulator/power/` (the viewer's sources are in `design/simulator/viewer/`, the battery in `design/verification-battery/`) |
| `power_tools/results/` | `design/simulator/power/results/` |
| `tech_tree_vNNN.md` (the highest number), `/home/claude/tt.md` | `design/tech_tree.md`, the design document. There are no numbered copies: versions from v3.112 on are in the git history. |
| `deferred-tasks/uncharted-horizons.md`, `~/.claude/deferred-tasks/` | `design/notes/deferred_tasks.md` |
| `ftl_decisions_digest.md` | `design/notes/ftl_decisions_digest.md` |
| `power_tools/unciv_reference/` | `design/simulator/unciv/` (rulesets and the uniques reference) and `design/simulator/unciv_src/` (engine extracts) |

## Conventions
- **New tools and scripts go in `design/simulator/power/`, measurement output in `power/results/`**, and both are committed.
- **The tree is the design document**, `design/tech_tree.md`, and every tool reads it (`power/defaults.py`). A new version is a commit; to measure an old one, check it out.
- **Parked work goes in `design/notes/deferred_tasks.md`**, and nowhere else.
- **Scratch runs go through `power/scratch_run.sh`.** It copies the document to a private temporary file, applies `scratch_patch.py` to the copy, runs the command against it (`UH_TREE` names the copy) and deletes the copy afterwards. The document is never modified, and parallel runs never share a copy.
- **The finalised design is the default.** `LEVERS=abcrwgpnyhukqvVm WROWX=4 SPACEPRICE=0.8` (see *Full design and victory time* below) apply wherever those switches aren't set. Set a switch to try a variant; `LEVERS=` (empty) switches every lever off.

## Where things are
- **The tree:** `design/tech_tree.md` (v3.112 when the workspace moved): the FTL endgame redesign is written into it (see *v3.112* below). The direction document keeps the rationale and measurement history.
- **The FTL direction document** (Claude Doc): https://claude.ai/code/artifact/d300173f-580c-4c14-aa10-fc10404f4a58 — winds W1–W19, decisions and what's open.
- **The viewer artifact:** https://claude.ai/artifact/RKS75AdNNkLjjP3FJxK3mv
- **Physics models:** `physics_model_I_substance.md`, `physics_model_II_process.md`, `physics_model_III_phlogiston.md`. Not in the repository.
- **Power tools:** `design/simulator/power/` — the data loaders (`gen_data.py`, `reach.py`, `prereq.py`, `worlds.py`), the discovery harness (`harness2.py`) and its FTL measurement copies (`harness_ftl.py`, and `harness_ftl_e.py`, which `w7f.py` runs: research-target hook, W16's funded-focus rule, price multipliers). The battery is `design/verification-battery/battery.py`; the viewer's sources are in `design/simulator/viewer/`, built by `power/build.py`.
- **Unciv reference:** `design/simulator/unciv/` and `design/simulator/unciv_src/` — the Gods & Kings and Vanilla rulesets, the generated uniques reference (`uniques.md`), and engine source extracts (`MapUnit.kt`, `UnitMovement.kt`, `UnitActionsFromUniques.kt`, `BattleUnitCapture.kt`, `UniqueType.kt` and others), saved so a session need not hit GitHub's rate limit. The repository's own `docs/Modders/` and `android/assets/jsons/` hold the current versions.
- **Checkpoints:** `CHECKPOINTS.md`. Not in the repository.

## What was lost before this guide existed (2026-10-13)
A reset wiped the measurement scripts and results of the FTL policy and dilemma measurements (their figures are recorded in the direction document, W7) and the deferred file's only copy (rebuilt from the conversation transcripts).

## Scratch runs (updated 13 Oct 2026)
- `power/scratch_run.sh <command>` runs the command against a patched private copy of the design document (see *Conventions*). Until 14 October it patched a shared working copy and restored it from the highest saved `tech_tree_vNNN.md` afterwards, and kept any copy that had drifted as `results/tt_unexpected_<time>.md`; that machinery went with the move, since nothing now writes to a shared tree.
- Switches: `LEAK=RK07` puts the leakage survey on RK07 (tested, rejected); `LEVERS=abc` applies W14's reliability levers (a: condition-hosting rows at 1x; b: MS02 CORE; c: QM-E06 also accepts MS02).
- Keep each tool call to one or two runs (about 2 minutes, the tool's default time limit), or run longer batches in the background. A run that's killed loses only its own results.
- `w7d.py` theory then engineering; `w7e.py` the same, saving every game's discovery record; `critical_path.py <world>` traces what set the time to certainty (run inside scratch_run.sh with the same LEVERS).
- `w7f.py` switches (environment variables): `DET=smart` (cheapest-first focus choice); `END=<multiplier>` Grand Endeavours, with `ENDRULE=naive|active|last` and `ENDFROM=theory`; `RUNON=1` games run past the calibrated end of the Space era until certain and built (always use for engineering or victory times); `DIFF=1` knowledge diffusion from five replayed rivals, which needs a pool `results/w7f_<world>_pool.json`, made with `RUNON=1 SAVE_T=1 SEED0=27000 TRUTHSEED=77 ... w7f.py <world> 10 _pool`. Build lists follow W9 for power (any Atomic-era plant), and the engineering phase targets only unmet requirements.
- Unfinished games: every `w7f` record has `why` (for certain-but-unbuilt games: the missing rows and their root causes). Never report engineering or victory times without the count of games that could not finish.

## Working balance and benchmark players (13 Oct 2026)
- The agreed working balance ("round two") is `LEVERS=abcrwgpnyhuk WROWX=4`: W14's levers (a, b, c), RC06 alongside RC05 (r), Wormhole's MS17 row at 4x (w + WROWX=4), Warp without the Smart Grid prerequisite (g), AE14 at 1x (p), atomic Tachyonic without NP11 (n + y), MA19 at 1x (h), CP16 at 1x (u), TH20 at 4x (k).
- Benchmark players: expert = `runcell.sh <world> <method> <suffix>`; novice = `runnov.sh <world> <method> <suffix>`; average player = `runavg.sh <world> <method> <suffix>` (economy 0.8, prototype 11 turns). Each wrapper builds in its player's settings (the expert's `EXPFIX=1 ENDFROM=theory`; the novice's `END=2 ENDRULE=request NOVEND=10 NOVFOCUS=1 GLIMPSE=0.1 OBS=0`) and takes extra `VAR=value` switches after the suffix. Until 14 October the expert's levers were a positional argument (`runcell.sh <world> <method> <levers> <suffix> ...`) and the novice's settings had to be passed. Results for round two: `results/w7f_<world>_{XF2,NF2,AV2}_<method>.json`.
- Fix `PYTHONHASHSEED` (e.g. `PYTHONHASHSEED=0`) when comparing settings: Python's per-process hash randomisation changes some tie-breaks, rarely for the expert and more often for the novice (checked 14 Oct 2026).
- Compare players and pooled worlds on the absolute game turn of victory (`balance_abs.py`, `balance_rounds.py`), never on turns from a player's own first Space-era discovery.

## Full design and victory time (13 Oct 2026)
- Full design so far = `LEVERS=abcrwgpnyhukq WROWX=4 SPACEPRICE=0.8` (round-two balance, the W18 signature pools, Space-era base price 20% cheaper). Optional `z` adds ASSUMED non-FTL Space pools (measurement only).
- Victory turn = max(certainty, build complete) + prototype (5 turns good economy, 6 average; agreed 5x) + SS FTL Drive (4 / 5 turns, one fewer for Warp, Wormhole, Plenum) + 1 turn delivery and launch (`victory_total.py`; before/after in `results/rebalance_check.txt`).
- Players without an FTL agenda: `PLAYER=generalist` (most work waiting), `PLAYER=specialist` (one wanted field at a time), `PLAYER=aspirant` (all Space-era content, or `ASPIRE=field;field`). Non-science Insight assumed 85% of a science player of the same skill (`ECON=0.85` good, `0.68` average).
- Updated: the full design is now `LEVERS=abcrwgpnyhukqvVm WROWX=4 SPACEPRICE=0.8`, the default since 14 October (`power/defaults.py`) (m: Quantum Computing at 2x, agreed after the final confirmation and not re-simulated) — adding `v` (QP08 needs QP04 Particle Accelerator; QM-E27 needs QM-E08 Boundary Furnace) and `V` (both instruments CORE). The attention boost (`t`) is dropped. The expert keeps its theory-first beeline (`EXPFIX=1 ENDFROM=theory`), which is optimal.

## v3.112 (2026-10-14) — the FTL endgame written into the tree
- **Active tree: `tech_tree_v112.md`**, now `design/tech_tree.md`. Built in stages by `power/v112_stage1.py`–`v112_stage5.py` from v3.111 (re-runnable in the old workspace only; the work-in-progress copy and §4's draft were in `wip/`, which isn't in the repository). After the stages: MS17 revised (Shockproof Walls; Bomb Shelters 50% more effective) and **EL07 Power Grid made CORE** (the CORE great instruments need it; as STANDARD it left 8 of 60 Substance Plenum games without a unified theory).
- `scratch_patch.py` now skips rows the canonical tree already holds, and its instrument-gate switch keeps MA13 in QM-E27's prerequisites (W6), as the tree does. The tree now carries the agreed prerequisites, so old variant switches can no longer recreate pre-round-two shapes; prices still come from `w7f.py`'s switches (full design: `LEVERS=abcrwgpnyhukqvVm WROWX=4 SPACEPRICE=0.8`, now the default). So a price the document changes in a cost note (“**cost ×N**”) reaches the simulator only when `w7f.py` is changed to match.
- Checked on v3.112 (expert, 60 games a cell): atomic Warp 288, Substance Warp 292, Substance Plenum 297, atomic Tachyonic 292, all as in the final confirmation; Process Tachyonic 298 against 294 — probably TH19 Permafrost Engineering, now in the tree, whose tundra condition the harness cannot model.
- **Decisions digest: `design/notes/ftl_decisions_digest.md`** — every finalised FTL-endgame decision in compact form (≈2,700 words). Read it at the start of a session instead of the direction document; open the document only for rationale or measurement detail.
- **Harness switches added 2026-10-14:** `TRACE=<path>` (one game's turn-by-turn record; formatter `power/trace_table.py`, example `docs/hyperspace_game_trace.md`); `EXPCAP` / `EXPCAP_ERA` (the expert's premium cap, off by default). The tachyonic-sector conditions now point at QP15 / QM-E28 with their instruments.

