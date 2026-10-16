# Uncharted Horizons — design

Everything about the fork's research system that isn't game code: the design document, the notes that go with it, and the tools that check and measure it.

| Path | What it is |
|---|---|
| `tech_tree.md` | **The tech-tree design document, and the source of truth.** One Markdown file, v3.112. |
| `notes/deferred_tasks.md` | Work parked for later, with the reasons. Keep parked items here, in the repository, so they survive session resets. |
| `notes/ftl_decisions_digest.md` | Every finalised FTL-endgame decision in compact form. Read it before working on §4. |
| `notes/ftl_history.md` | The FTL puzzle's and its costs' history: each round, what changed, why, what it measured, and what later undid it. |
| `notes/discovery_workshop_report.md` | The 1 October discovery-model workshop. Every measurement since uses its candidate model. |
| `verification-battery/` | 22 structural and Unciv-syntax checks on the design document. Run it after every edit. |
| `simulator/` | The research and FTL-endgame simulator, its measurement scripts and every saved result. |
| `wiki/` | The generator that builds the GitHub wiki from `tech_tree.md` (see below). |
| `mockups/research_screen/` | The research-screen mockup (a Design canvas): its source, data, requirements and review. See its README. |
| `mockups/sim_web/` | Two browser prototypes built on the simulator: a replay viewer that plays a simulated game's turn-by-turn log (`w7f.py` with `TRACE=<file>`) as the research and FTL screens saw it, and a live game, the simulator's engine ported to JavaScript (bit for bit with Python) to play a game to victory by hand. See its README and `SPEC.md`. |

## Checking an edit

    pip install json5
    python3 design/verification-battery/battery.py design/tech_tree.md

The battery's output on v3.112 is in `verification-battery/RESULTS_v3.112.txt`: 18 checks pass, and 4 fail on known issues listed in its README.

## Simulating

See `simulator/README.md`, and `simulator/docs/WORKSPACE.md` for the conventions, switches and benchmark players.

    bash design/simulator/power/runcell.sh familiar Hyperspace _mytest    # 60 expert games, finalised design

- **Which tree it measures.** `tech_tree.md` itself, as it stands in the checkout, so a run after an edit measures the edit. The document is never modified: each run patches a private temporary copy.
- **The finalised design is the default.** The agreed levers and prices apply unless a run sets them; see `simulator/power/defaults.py`.
- **Paths.** Its scripts hold absolute paths, kept pointing at `/home/user/Uncharted-Horizons/design/simulator`, where cloud sessions check out the repository. After cloning the repository anywhere else, run `python3 design/simulator/relocate.py` once.

## The wiki

The [GitHub wiki](https://github.com/Heliomance/Uncharted-Horizons/wiki) is built from `tech_tree.md` by `wiki/build_wiki.py`. Edit the document, never the wiki: the next publish overwrites any hand edit to a generated page.

    python3 design/wiki/build_wiki.py --check           # build, and validate every internal link and anchor
    python3 design/wiki/build_wiki.py --out /tmp/wiki   # write the pages to a folder to read

**Publishing.** The *Publish design wiki* workflow (`.github/workflows/publishDesignWiki.yml`) rebuilds the wiki and pushes it whenever `tech_tree.md` or the generator changes on `master` or a `claude/*` branch. It needs GitHub Actions to be enabled for the repository. GitHub has no API for wikis, so without Actions the only way is a push from a machine that can write to the wiki:

    git clone https://github.com/Heliomance/Uncharted-Horizons.wiki.git
    python3 design/wiki/build_wiki.py --sync-into Uncharted-Horizons.wiki
    cd Uncharted-Horizons.wiki && git add -A && git commit -m "Rebuild the design wiki" && git push

- **Hand-made pages are safe.** The generator lists the pages it owns in `.generated-pages` in the wiki, and only ever replaces or deletes those. Pages added by hand are left alone.
- **The wiki only moves forward.** A publish is refused if the document's version is older than the wiki's. The version is the latest changelog entry, so a stale branch can't undo newer work.
- **Nothing is dropped silently.** If the document gains a section the generator has no page for, the build fails and names the section; extend `build_wiki.py` to place it.

**How the document maps onto pages:**

| Document | Pages |
|---|---|
| §1.1–1.2 | Discovery Mechanics, Breakthrough Tiers, Competing Solutions, Knowledge Diffusion |
| §1.3, §1.4, §1.5, §2 | One page each |
| §3 | Focus Areas, and a page per focus: an overview table, a prerequisite map, and an entry for each breakthrough listing what it leads to |
| §4 | FTL Endgame, FTL in Elemental Worlds, Victories |
| §5 | World Truths, Foundational Questions, Worked Example Worlds |
| §6 | Game Balance Rules |
| §7.0, §7 | Mechanical Grounding; Base-Game Object Assignments |
| §8 | Summary Statistics, plus counts computed from the tables |
| Changelog | A page per ten versions; each entry carries its one-line summary from §8 |
| (generated) | Breakthrough Index, Breakthroughs by Era, Breakthroughs by Tier, New Objects |

Bold lead-ins ("**Filter discipline.** …") become headings so they can be linked. Breakthrough IDs, `§` references, italicised section titles, World-Truth axes and flags, understanding tokens and focus names all become links.
