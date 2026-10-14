#!/bin/bash
# Run a command against the scratch redesign. The working tree is always restored from the CANONICAL saved version
# (the highest tech_tree_vNNN.md in outputs), never from itself, so a contaminated working copy cannot persist.
# If the working tree differs from canonical at the start, the odd copy is kept in results/ as evidence first.
CANON=$(ls /home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_v*.md | sed -E 's/.*_v([0-9]+)\.md/\1 &/' | sort -n | tail -1 | cut -d' ' -f2)
if ! cmp -s /home/user/Uncharted-Horizons/design/simulator/tt.md "$CANON"; then
  ODD=/home/user/Uncharted-Horizons/design/simulator/power/results/tt_unexpected_$(date +%Y%m%d_%H%M%S).md
  cp /home/user/Uncharted-Horizons/design/simulator/tt.md "$ODD"; echo "WARNING: working tree differed from $(basename $CANON); kept as $(basename $ODD), restoring canonical"
  cp "$CANON" /home/user/Uncharted-Horizons/design/simulator/tt.md
fi
trap 'cp "$CANON" /home/user/Uncharted-Horizons/design/simulator/tt.md; echo "document restored from $(basename $CANON): $(sha256sum /home/user/Uncharted-Horizons/design/simulator/tt.md | cut -c1-16)"' EXIT
python3 /home/user/Uncharted-Horizons/design/simulator/power/scratch_patch.py || exit 1
"$@"
