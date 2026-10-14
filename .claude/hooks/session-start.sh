#!/bin/bash
# Installs what the design tools in design/ need (the verification battery and the simulator read
# JSON5 rulesets). Cloud sessions only; the game's Gradle build is not needed for design work.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

python3 -c 'import json5' 2>/dev/null || pip install --quiet --disable-pip-version-check --root-user-action=ignore json5
