#!/bin/bash
# make_python_ref.sh <out_dir> [games_per_method=2]: reference games from the Python harness for test_engine_python.js.
#
# The generalist player (PLAYER=generalist: the focus with the most work waiting, no Endeavours) on the finalised design,
# with the settings the JavaScript engine ports: rivals and diffusion (DIFF=1), no observational revelation (OBS=0),
# glimpses by tier (GLIMPSE=0.1 GLIMPSEU=0.03), RUN_ON, instruments 5 turns (6 on the average economy), every row's
# discovery turn saved (SAVE_T=1). For each world (familiar, Process, Substance) and economy (1.0, 0.8): <games> games of
# each of the five methods (w7f.py's draws 0 .. 5*games-1), plus one traced game (TRACE=: every turn's record) of the
# first method. The results go to <out_dir> with a meta.json describing them; the harness's own results files are
# deleted (labels _webref*).
#   bash test/make_python_ref.sh /tmp/uh_ref 2
set -e
OUT=$(realpath -m "${1:?usage: make_python_ref.sh <out_dir> [games_per_method]}"); N=${2:-2}
POWER=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../simulator/power" && pwd)
mkdir -p "$OUT"
META="$OUT/meta.json"; echo '[' > "$META"; first=1
for ECON in 1.0 0.8; do
  if [ "$ECON" = 1.0 ]; then INSTR=5; MAXT=450; else INSTR=6; MAXT=600; fi
  for W in familiar Process Substance; do
    TAG=_webref_${W}_${ECON/./}
    env PLAYER=generalist DIFF=1 OBS=0 GLIMPSE=0.1 GLIMPSEU=0.03 RUNON=1 SAVE_T=1 PYTHONHASHSEED=0 INSTR_D=$INSTR ECON=$ECON MAXT=$MAXT \
      bash "$POWER/scratch_run.sh" bash -c "cd '$POWER' && python3 w7f.py $W $N $TAG" 2>&1 | grep -v 'scratch redesign' || true
    mv "$POWER/results/w7f_${W}${TAG}.json" "$OUT/games_${W}_${ECON}.json"
    M1=$(python3 -c "import json,sys; print(list(json.load(open('$OUT/games_${W}_${ECON}.json'))[0]['m'] for _ in [0])[0])")
    env PLAYER=generalist DIFF=1 OBS=0 GLIMPSE=0.1 GLIMPSEU=0.03 RUNON=1 SAVE_T=1 PYTHONHASHSEED=0 INSTR_D=$INSTR ECON=$ECON MAXT=$MAXT \
      METHODS=$M1 WORKERS=1 TRACE="$OUT/trace_${W}_${ECON}.json" \
      bash "$POWER/scratch_run.sh" bash -c "cd '$POWER' && python3 w7f.py $W 1 ${TAG}tr" 2>&1 | grep -v 'scratch redesign' || true
    rm -f "$POWER/results/w7f_${W}${TAG}tr.json"
    [ $first = 1 ] || echo ',' >> "$META"; first=0
    printf '{"world":"%s","econ":%s,"n":%s,"methods":null,"maxTurns":%s,"instrD":%s,"games":"games_%s_%s.json","trace":"trace_%s_%s.json"}\n' \
      "$W" "$ECON" "$N" "$MAXT" "$INSTR" "$W" "$ECON" "$W" "$ECON" >> "$META"
  done
done
echo ']' >> "$META"
echo "reference games in $OUT"
