# Uncharted Horizons — verification battery

Checks the tech tree design document (the single Markdown file, `tech_tree_v112.md` or later) for structural and Unciv-syntax errors. It's the routine run after every edit to the tree: a change is done only when the battery is clean, apart from known, recorded exceptions.

## Running it

Requirements: Python 3.10 or later, and the `json5` package (`pip install json5`).

    python3 battery.py path/to/tech_tree_v112.md

It can be run from any folder: it finds `unciv/`, `filtercheck.py` and `prereq.py` beside itself. Each check prints PASS or FAIL with a count and the first offenders. `info` lines are notes, not failures.

## The 22 checks

1. templates/conditionals
2. filter values
3. prerequisite references
4. duplicate IDs
5. CORE closure (mandatory prerequisites)
6. per-world token sources
7. exclusion by replacement
8. no placeholder `replaces`
9. no Remove clause removes its own building
10. every row has seven cells
11. no hard prerequisite sits in a later era than its dependent
12. every focus table's header is followed by its separator
13. required buildings exist, arrive in time, share their worlds, and are inherited
14. every required building is a safe predecessor
15. no row's only grant is a world wonder
16. every fork building has an explicit cost; the cost-scaling table covers every era
17. every breakthrough named in a tech conditional exists
18. every prerequisite ID is read by the shared parser (prereq.py)
19. no prerequisite relies on operator precedence
20. every validated prerequisite sits on a row that declares its world
21. both records of every dual path agree, every named focus exists
22. every breakthrough row is a well-formed table row, closing pipe included

The battery also prints a tier tally (CORE, STANDARD, UNCOMMON, RARE, UNIQUE). Compare it before and after an edit, to confirm only the intended rows changed tier.

## Files

| File | What it is |
|---|---|
| `battery.py` | The battery itself (version of 2 October 2026, used through v3.111). Its one hard-wired path was replaced on 14 October so it runs from any folder. |
| `filtercheck.py` | Checks every filter value in the tree's uniques against Unciv's vocabulary. `battery.py` runs it and prints its report. |
| `prereq.py` | The shared prerequisite parser, also used by the simulator. |
| `build_reference.sh` | Rebuilds the three derived reference files below from Unciv's documentation and rulesets. |
| `unciv/uniques.md` | Unciv's documentation of every unique (saved in September 2026). |
| `unciv/Unique-parameters.md`, `unciv/*.json` | Unciv's parameter documentation and Gods & Kings rulesets. Buildings, Techs and Units were saved in September; the rest were downloaded from the fork on 14 October, while it was still identical to Unciv. |
| `unciv/unique_templates.txt`, `unciv/conditionals.txt`, `unciv/vocab.json` | Derived files (833 templates, 168 conditionals, the filter vocabulary), rebuilt on 14 October by `build_reference.sh`. |
| `RESULTS_v3.112.txt` | The battery's output on v3.112: see below. |

To check against a newer Unciv, replace the files in `unciv/` with current copies from Unciv's `docs/Modders/` and `android/assets/jsons/Civ V - Gods & Kings/`, then run `build_reference.sh`.

One fix was needed when the derived files were rebuilt: newer copies of `uniques.md` escape conditionals as `&lt;…&gt;`. The recipe in `build_reference.sh` now accepts both forms.

## Results on v3.112: 18 pass, 4 fail

These are real issues in the tree. The battery's reference files had been lost in a container reset, so it hadn't run since 2 October, and v3.110 to v3.112 were never checked by it.

1. **Templates and conditionals: 10 unique strings Unciv wouldn't recognise.** Most lack a required parameter. Unciv's templates end in a city filter, e.g. `[relativeAmount]% Production when constructing [buildingFilter] wonders [cityFilter]`, and the tree's versions omit it. The conditional `<upon building>` isn't an Unciv conditional. Full list in `RESULTS_v3.112.txt` and below.
2. **Filter values: 3 problems.** The Advisory Council row still has the placeholders `+X` and `N` (its numbers are "set at spec"), and the Spy Satellite row uses `Satellite`, which isn't a valid unit filter.
3. **Costs: 2 fork buildings have no explicit cost,** Shockproof Walls and Storage Array.
4. **Worlds: Exotic Matter Engineering** has a prerequisite that depends on a validated hypothesis, but the row doesn't declare which worlds it belongs to.

The 10 unrecognised strings:

- `[+15]% Food is carried over after population increases`
- `<upon building>`
- `New spies start with [1] level`
- `[+25]% spy effectiveness <when espionage is enabled>`
- `Can transform to`
- `<before discovering [Helium Extraction]>`
- `up to [20] tiles away`
- `[+25]% Production when constructing [Wonder] wonders`
- `[+15]% Production when constructing [All] buildings`
- `[-50]% maintenance cost for [Power Plant] buildings`

## When the wiki becomes the source of truth

The battery reads one Markdown file. Once the design lives in the wiki, assemble the pages back into a single document in the original order before running it, or adapt its row reader to read the wiki pages.
