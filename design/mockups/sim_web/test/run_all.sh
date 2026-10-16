#!/bin/bash
# run_all.sh [games_per_method=2]: every engine test, from design/mockups/sim_web (or anywhere).
#   1. pyrandom.js against CPython's random.Random, draw by draw (test_pyrandom.js)
#   2. the compensated sum against Python's sum() (test_pysum.js)
#   3. the glibc exp, log, pow and fma ports against Python's, a million arguments each (test_pymath.js)
#   4. the engine against the Python harness: generalist games in all three worlds on both economies, every row's
#      discovery turn, plus one traced game per world and economy, record by record (test_engine_python.js)
#   5. the human path against the harness patched with a scripted player (focus choices, Endeavours), record by record
#      and every float to the bit (py_scripted.py, test_engine_scripted.js)
#   6. the human API played to victory, the failed prototype, save and restore (test_human.js)
#   7. the engine in Chromium as plain scripts, against Node (test_browser.py; skipped without Playwright)
# References are made in a temporary folder, deleted at the end; the simulator's results/ folder is left as it was.
set -e
N=${1:-2}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); WEB=$(dirname "$HERE"); POWER=$(cd "$WEB/../../simulator/power" && pwd)
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cd "$WEB"
echo "== 1. pyrandom";  python3 -I test/pyrandom_ref.py "$TMP/pyrandom.json" >/dev/null && node test/test_pyrandom.js "$TMP/pyrandom.json"
echo "== 2. pysum";     python3 -I test/pysum_ref.py "$TMP/pysum.json" >/dev/null && node test/test_pysum.js "$TMP/pysum.json"
echo "== 3. pymath";    python3 -I test/pymath_ref.py "$TMP/pymath" 1 >/dev/null && node test/test_pymath.js "$TMP/pymath"
echo "== 4. engine against the harness (generalist)"
bash test/make_python_ref.sh "$TMP/ref" "$N" | { grep -v "games reached certainty\|reference games in" || true; }
node test/test_engine_python.js "$TMP/ref"
echo "== 5. the human path against the harness (scripted player)"
mkdir -p "$TMP/scripted"
for ECON in 1.0 0.8; do
  if [ "$ECON" = 1.0 ]; then I=5; MT=450; else I=6; MT=600; fi
  for W in familiar Process Substance; do
    (cd "$POWER" && env PLAYER=generalist DIFF=1 OBS=0 GLIMPSE=0.1 GLIMPSEU=0.03 RUNON=1 SAVE_T=1 PYTHONHASHSEED=0 INSTR_D=$I ECON=$ECON MAXT=$MT END=2 \
      bash scratch_run.sh python3 "$HERE/py_scripted.py" $W "$N" "$TMP/scripted/${W}_${ECON}.json" 2>&1 | { grep -v "scratch redesign\|done:" || true; } >/dev/null)
  done
done
node test/test_engine_scripted.js "$TMP/scripted"
echo "== 6. the human API"; node test/test_human.js 3 | tail -n 16
echo "== 7. the browser"
if python3 -c "import playwright" 2>/dev/null; then node test/browser_ref.js > "$TMP/browser.json" && python3 test/test_browser.py "$TMP/browser.json"; else echo "skipped: no Playwright"; fi
