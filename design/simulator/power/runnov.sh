#!/bin/bash
# runnov.sh <world> <method> <suffix> [VAR=value ...]: 60 games of one method, the novice player (FTL-screen hints only; no Endeavours)
W=$1; M=$2; S=$3; shift 3
env PLAYER=novice RUNON=1 DIFF=1 INSTR_D=5 LEVERS=abcrw METHODS=$M "$@" \
  bash /home/user/Uncharted-Horizons/design/simulator/power/scratch_run.sh bash -c "cd /home/user/Uncharted-Horizons/design/simulator/power && timeout 115 python3 w7f.py $W 60 $S" 2>&1 | grep -v "scratch redesign" | grep "done\|WARNING\|Error" | sed "s/^/$W $M $S: /"
