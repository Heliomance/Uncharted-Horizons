#!/bin/bash
# scratch_run.sh <command ...>: run a command against the scratch redesign. The design document (design/tech_tree.md)
# is copied to a private temporary file, scratch_patch.py applies the agreed redesign's switches to the copy, and the
# command runs with UH_TREE pointing at it; the copy is deleted when the command ends, however it ends. The document
# itself is never modified, and parallel runs never share a copy. Switches that aren't set take the finalised
# design's values (defaults.py). UH_DOC=<file> runs against another copy of the document instead (an older version from
# git history, say); it is copied and patched the same way.
P=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
eval "$(python3 "$P/defaults.py")"
UH_TREE=$(mktemp --suffix=.md) || exit 1
export UH_TREE
trap 'rm -f "$UH_TREE"' EXIT
cp "${UH_DOC:-$CANONICAL}" "$UH_TREE" || exit 1   # UH_DOC=<file>: run on another version of the document (e.g. one from git history)
python3 "$P/scratch_patch.py" || exit 1
"$@"
