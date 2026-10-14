#!/bin/bash
# Rebuild the working environment from the persistent outputs folder (run at the start of any session
# where /home/user/Uncharted-Horizons/design/simulator is empty). Only /home/user/Uncharted-Horizons/design/simulator/outputs survives a container reset.
set -e
O=/home/user/Uncharted-Horizons/design/simulator/outputs; PT=$O/power_tools
mkdir -p /home/user/Uncharted-Horizons/design/simulator/power /home/user/Uncharted-Horizons/design/simulator/unciv /home/user/Uncharted-Horizons/design/simulator/unciv_src ~/.claude/deferred-tasks
cp -r $PT/. /home/user/Uncharted-Horizons/design/simulator/power/                                   # tools, harnesses, measurement scripts
cp $PT/unciv_reference/rulesets/* /home/user/Uncharted-Horizons/design/simulator/unciv/              # Techs/Buildings/Units/UnitTypes .json, uniques.md (ledger.py reads these)
cp $PT/unciv_reference/src/* /home/user/Uncharted-Horizons/design/simulator/unciv_src/               # engine source extracts (carrying, paradrop, capture)
latest=$(ls $O/tech_tree_v*.md | sed -E 's/.*_v([0-9]+)\.md/\1 &/' | sort -n | tail -1 | cut -d' ' -f2)
cp "$latest" /home/user/Uncharted-Horizons/design/simulator/tt.md                                    # the working tree = the highest-numbered saved version
cp $O/deferred-tasks/uncharted-horizons.md ~/.claude/deferred-tasks/uncharted-horizons.md
echo "restored: tree $(basename $latest) (sha $(sha256sum /home/user/Uncharted-Horizons/design/simulator/tt.md | cut -c1-16)), $(ls /home/user/Uncharted-Horizons/design/simulator/power | wc -l) tool files, $(grep -c '^## ' ~/.claude/deferred-tasks/uncharted-horizons.md) deferred tasks"
