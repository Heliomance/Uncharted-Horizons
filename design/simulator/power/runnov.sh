#!/bin/bash
# runnov.sh <world> <method> <suffix> [VAR=value ...]: 60 games of one method by the novice benchmark player (FTL-screen
# hints only; commissions an Endeavour for a revealed step that has held up its funded field for 10 funded turns), on the
# finalised design (defaults.py). VAR=value overrides any setting; END= takes the Endeavours away.
if [ $# -lt 3 ] || { [ -n "$4" ] && [[ "$4" != *=* ]]; }; then
  echo "usage: $(basename "$0") <world> <method> <suffix> [VAR=value ...]  (the finalised levers and Space price are now the defaults; override with LEVERS=..., SPACEPRICE=...)" >&2; exit 2
fi
W=$1; M=$2; S=$3; shift 3
env PLAYER=novice RUNON=1 DIFF=1 INSTR_D=5 END=2 ENDRULE=request NOVEND=10 NOVFOCUS=1 GLIMPSE=0.1 OBS=0 METHODS=$M "$@" \
  bash /home/user/Uncharted-Horizons/design/simulator/power/scratch_run.sh bash -c "cd /home/user/Uncharted-Horizons/design/simulator/power && timeout 115 python3 w7f.py $W 60 $S" 2>&1 | grep -v "scratch redesign" | grep "done\|WARNING\|Error" | sed "s/^/$W $M $S: /"
