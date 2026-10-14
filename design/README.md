# Uncharted Horizons — design

Everything about the fork's research system that isn't game code: the design document, the notes that go with it, and the tools that check and measure it.

| Path | What it is |
|---|---|
| `tech_tree.md` | **The tech-tree design document, and the source of truth.** One Markdown file, v3.112. |
| `notes/deferred_tasks.md` | Work parked for later, with the reasons. Keep parked items here, in the repository, so they survive session resets. |
| `notes/ftl_decisions_digest.md` | Every finalised FTL-endgame decision in compact form. Read it before working on §4. |
| `notes/discovery_workshop_report.md` | The 1 October discovery-model workshop. Every measurement since uses its candidate model. |
| `verification-battery/` | 22 structural and Unciv-syntax checks on the design document. Run it after every edit. |
| `simulator/` | The research and FTL-endgame simulator, its measurement scripts and every saved result. |

## Checking an edit

    pip install json5
    python3 design/verification-battery/battery.py design/tech_tree.md

The battery's output on v3.112 is in `verification-battery/RESULTS_v3.112.txt`: 18 checks pass, and 4 fail on known issues listed in its README.

## Simulating

See `simulator/README.md`, and `simulator/docs/WORKSPACE.md` for the conventions, switches and benchmark players.

- **Which tree it measures.** The simulator measures the highest-numbered `simulator/outputs/tech_tree_vNNN.md`. To measure a new version of the design document, first copy `tech_tree.md` there under the next number.
- **Paths.** Its scripts hold absolute paths, kept pointing at `/home/user/Uncharted-Horizons/design/simulator`, where cloud sessions check out the repository. After cloning the repository anywhere else, run `python3 design/simulator/relocate.py` once.
- **Outdated advice in WORKSPACE.md.** It was written for the previous environment, where only `/mnt/user-data/outputs` survived a reset. Here the checkout is the workspace: `restore_workspace.sh` isn't needed, and anything worth keeping is committed.
