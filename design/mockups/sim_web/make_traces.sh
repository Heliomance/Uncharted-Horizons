#!/bin/bash
# make_traces.sh: the replay viewer's three sample logs, one game each, written to design/mockups/sim_web/traces/.
#   expert_familiar_Warp.json       the expert (runcell.sh's settings), the familiar world, Warp
#   novice_Process_Plenum.json      the novice (runnov.sh's settings), the Process world, Plenum
#   average_Substance_Wormhole.json the average player (runavg.sh's settings: the novice on the 0.8 economy), Substance, Wormhole
# Each is w7f.py's TRACE output for the first game of its method (N=1: the draw that falls to that method), played through
# scratch_run.sh on the finalised design (defaults.py). The results file each run writes is deleted afterwards.
# Usage: bash design/mockups/sim_web/make_traces.sh        (about a minute)
#        GAME=<n> picks the n-th game of each method instead of the first (n from 0).
set -e
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
POWER=$(cd "$HERE/../../simulator/power" && pwd)
OUT="$HERE/traces"
mkdir -p "$OUT"
N=$(( ${GAME:-0} + 1 ))

trace() {   # trace <out name> <world> <method> <label> VAR=value ...
  local name=$1 world=$2 method=$3 label=$4; shift 4
  env "$@" METHODS="$method" TRACE="$OUT/$name.json" WORKERS=1 \
    bash "$POWER/scratch_run.sh" bash -c "cd '$POWER' && python3 w7f.py $world $N $label" 2>&1 | grep -v "scratch redesign" || true
  rm -f "$POWER/results/w7f_${world}${label}.json"
  python3 - "$OUT/$name.json" <<'EOF'
import json, sys
p = sys.argv[1]; t = json.load(open(p))
json.dump(t, open(p, 'w'), separators=(',', ':'))
r = t['records']
print(f"{p}: {t['world']} {t['m']} {t['player']} econ {t['econ']}: {len(r)} turns, {sum(len(x['found']) for x in r)} discovered, "
      f"certain {t['cert'] and t['cert'][0]}, built {t['built']}")
EOF
}

trace expert_familiar_Warp familiar Warp _webtrace_x \
  DET=smart ORSMART=1 PARALLEL=1 RUNON=1 DIFF=1 OBS=0 GLIMPSE=0.1 GLIMPSEU=0.03 END=2 ENDRULE=last EXPCAP=2 INSTR_D=5 EXPFIX=1 ENDFROM=theory
trace novice_Process_Plenum Process Plenum _webtrace_n \
  PLAYER=novice RUNON=1 DIFF=1 INSTR_D=5 END=2 ENDRULE=request NOVEND=10 NOVFOCUS=1 GLIMPSE=0.1 GLIMPSEU=0.03 OBS=0
trace average_Substance_Wormhole Substance Wormhole _webtrace_a \
  PLAYER=novice ECON=0.8 MAXT=600 RUNON=1 DIFF=1 INSTR_D=6 END=2 ENDRULE=request NOVEND=10 NOVFOCUS=1 GLIMPSE=0.1 GLIMPSEU=0.03 OBS=0
