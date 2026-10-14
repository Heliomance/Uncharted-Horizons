# Workspace — Uncharted Horizons (read this first in any new session)

**Only `/mnt/user-data/outputs` survives a container reset.** `/home/claude` and `~/.claude` are wiped between sessions.
So everything worth keeping lives here, and the working copies are rebuilt from it:

    bash /mnt/user-data/outputs/power_tools/restore_workspace.sh

## Conventions
- **Write new tools and scripts straight into `power_tools/`**, and measurement output into `power_tools/results/`, not only into `/home/claude`.
- **Every new tree version is saved as `tech_tree_vNNN.md`** here; the restore script takes the highest number as the working tree (`/home/claude/tt.md`).
- **The deferred-tasks file is kept in two places**: `deferred-tasks/uncharted-horizons.md` here (the safe copy) and `~/.claude/deferred-tasks/` (where the tracking skill looks). Update both.
- Scratch runs against an unsaved redesign go through `power_tools/scratch_run.sh`, which applies `scratch_patch.py` and restores the tree on exit.

## Where things are
- **The tree:** `tech_tree_v112.md` is the latest (v3.112): the FTL endgame redesign is written into it (see *v3.112* below). The direction document keeps the rationale and measurement history.
- **The FTL direction document** (Claude Doc): https://claude.ai/code/artifact/d300173f-580c-4c14-aa10-fc10404f4a58 — winds W1–W19, decisions and what's open.
- **The viewer artifact:** https://claude.ai/artifact/RKS75AdNNkLjjP3FJxK3mv
- **Physics models:** `physics_model_I_substance.md`, `physics_model_II_process.md`, `physics_model_III_phlogiston.md`.
- **Power tools:** `power_tools/` — the data loaders (`gen_data.py`, `reach.py`, `prereq.py`, `worlds.py`), the discovery harness (`harness2.py`) and its FTL measurement copy (`harness_ftl.py`: research-target hook, W16's funded-focus rule, price multipliers), the battery (`battery.py`), the viewer sources (`parse.js`, `solver.js`, `app.js`, `shell.html`, `build.py`).
- **Unciv reference:** `power_tools/unciv_reference/` — the Gods & Kings and Vanilla rulesets, the generated uniques reference (`uniques.md`), and engine source extracts (`MapUnit.kt`, `UnitMovement.kt`, `UnitActionsFromUniques.kt`, `BattleUnitCapture.kt`, `UniqueType.kt`), saved so a session need not hit GitHub's rate limit.
- **Checkpoints:** `CHECKPOINTS.md`.

## What was lost before this guide existed (2026-10-13)
A reset wiped the measurement scripts and results of the FTL policy and dilemma measurements (their figures are recorded in the direction document, W7) and the deferred file's only copy (rebuilt from the conversation transcripts).

## Scratch runs (updated 13 Oct 2026)
- `power_tools/scratch_run.sh <command>` applies `scratch_patch.py` to the working tree, runs the command, then **always restores the working tree from the highest saved `tech_tree_vNNN.md` in outputs**, never from itself. If the working tree differs from that canonical version when a run starts, the odd copy is kept as `results/tt_unexpected_<time>.md` before restoring. (Added after a contaminated working copy survived several "restores".)
- Switches: `LEAK=RK07` puts the leakage survey on RK07 (tested, rejected); `LEVERS=abc` applies W14's reliability levers (a: condition-hosting rows at 1x; b: MS02 CORE; c: QM-E06 also accepts MS02).
- Keep each tool call to one or two runs (about 2 minutes): a run killed by the tool's time limit cannot restore anything itself.
- `w7d.py` theory then engineering; `w7e.py` the same, saving every game's discovery record; `critical_path.py <world>` traces what set the time to certainty (run inside scratch_run.sh with the same LEVERS).
- `w7f.py` switches (environment variables): `DET=smart` (cheapest-first focus choice); `END=<multiplier>` Grand Endeavours, with `ENDRULE=naive|active|last` and `ENDFROM=theory`; `RUNON=1` games run past the calibrated end of the Space era until certain and built (always use for engineering or victory times); `DIFF=1` knowledge diffusion from five replayed rivals, which needs a pool `results/w7f_<world>_pool.json`, made with `RUNON=1 SAVE_T=1 SEED0=27000 TRUTHSEED=77 ... w7f.py <world> 10 _pool`. Build lists follow W9 for power (any Atomic-era plant), and the engineering phase targets only unmet requirements.
- Unfinished games: every `w7f` record has `why` (for certain-but-unbuilt games: the missing rows and their root causes). Never report engineering or victory times without the count of games that could not finish.

## Working balance and benchmark players (13 Oct 2026)
- The agreed working balance ("round two") is `LEVERS=abcrwgpnyhuk WROWX=4`: W14's levers (a, b, c), RC06 alongside RC05 (r), Wormhole's MS17 row at 4x (w + WROWX=4), Warp without the Smart Grid prerequisite (g), AE14 at 1x (p), atomic Tachyonic without NP11 (n + y), MA19 at 1x (h), CP16 at 1x (u), TH20 at 4x (k).
- Benchmark players: expert = `runcell.sh <world> <method> <levers> <suffix> EXPFIX=1 ENDFROM=theory`; novice = `runnov.sh <world> <method> <suffix> END=2 ENDRULE=request NOVEND=10 NOVFOCUS=1 GLIMPSE=0.1 OBS=0 LEVERS=...`; average player = `runavg.sh <world> <method> <suffix> LEVERS=...` (economy 0.8, prototype 11 turns). Results for round two: `results/w7f_<world>_{XF2,NF2,AV2}_<method>.json`.
- Compare players and pooled worlds on the absolute game turn of victory (`balance_abs.py`, `balance_rounds.py`), never on turns from a player's own first Space-era discovery.

## Full design and victory time (13 Oct 2026)
- Full design so far = `LEVERS=abcrwgpnyhukq WROWX=4 SPACEPRICE=0.8` (round-two balance, the W18 signature pools, Space-era base price 20% cheaper). Optional `z` adds ASSUMED non-FTL Space pools (measurement only).
- Victory turn = max(certainty, build complete) + prototype (5 turns good economy, 6 average; agreed 5x) + SS FTL Drive (4 / 5 turns, one fewer for Warp, Wormhole, Plenum) + 1 turn delivery and launch (`victory_total.py`; before/after in `results/rebalance_check.txt`).
- Players without an FTL agenda: `PLAYER=generalist` (most work waiting), `PLAYER=specialist` (one wanted field at a time), `PLAYER=aspirant` (all Space-era content, or `ASPIRE=field;field`). Non-science Insight assumed 85% of a science player of the same skill (`ECON=0.85` good, `0.68` average).
- Updated: the full design is now `LEVERS=abcrwgpnyhukqvVm WROWX=4 SPACEPRICE=0.8` (m: Quantum Computing at 2x, agreed after the final confirmation and not re-simulated) — adding `v` (QP08 needs QP04 Particle Accelerator; QM-E27 needs QM-E08 Boundary Furnace) and `V` (both instruments CORE). The attention boost (`t`) is dropped. The expert keeps its theory-first beeline (`EXPFIX=1 ENDFROM=theory`), which is optimal.

## v3.112 (2026-10-14) — the FTL endgame written into the tree
- **Active tree: `tech_tree_v112.md`** (the restore and scratch scripts pick it up as the highest version). Built in stages by `power_tools/v112_stage1.py`–`v112_stage5.py` from v3.111 (re-runnable; the work-in-progress copy and §4's draft are in `wip/`). After the stages: MS17 revised (Shockproof Walls; Bomb Shelters 50% more effective) and **EL07 Power Grid made CORE** (the CORE great instruments need it; as STANDARD it left 8 of 60 Substance Plenum games without a unified theory).
- `scratch_patch.py` now skips rows the canonical tree already holds, and its instrument-gate switch keeps MA13 in QM-E27's prerequisites (W6), as the tree does. The tree now carries the agreed prerequisites, so old variant switches can no longer recreate pre-round-two shapes; prices still come from `w7f.py`'s switches (full design: `LEVERS=abcrwgpnyhukqvVm WROWX=4 SPACEPRICE=0.8`).
- Checked on v3.112 (expert, 60 games a cell): atomic Warp 288, Substance Warp 292, Substance Plenum 297, atomic Tachyonic 292, all as in the final confirmation; Process Tachyonic 298 against 294 — probably TH19 Permafrost Engineering, now in the tree, whose tundra condition the harness cannot model.
- **Decisions digest: `ftl_decisions_digest.md`** — every finalised FTL-endgame decision in compact form (≈2,700 words). Read it at the start of a session instead of the direction document; open the document only for rationale or measurement detail.
- **Harness switches added 2026-10-14:** `TRACE=<path>` (one game's turn-by-turn record; formatter `power_tools/trace_table.py`, example `hyperspace_game_trace.md`); `EXPCAP` / `EXPCAP_ERA` (the expert's premium cap, off by default). The tachyonic-sector conditions now point at QP15 / QM-E28 with their instruments.

