#!/bin/bash
# runavg.sh <world> <method> <suffix> [VAR=value ...]: 60 games of one method, the average player (novice endgame, economy at 0.8)
W=$1; M=$2; S=$3; shift 3
env PLAYER=novice ECON=0.8 MAXT=600 RUNON=1 DIFF=1 INSTR_D=6 LEVERS=abcrw END=2 ENDRULE=request NOVEND=10 NOVFOCUS=1 GLIMPSE=0.1 OBS=0 METHODS=$M "$@" \
  bash /home/user/Uncharted-Horizons/design/simulator/power/scratch_run.sh bash -c "cd /home/user/Uncharted-Horizons/design/simulator/power && timeout 115 python3 w7f.py $W 60 $S" 2>&1 | grep -v "scratch redesign" | grep "done\|WARNING\|Error" | sed "s/^/$W $M $S: /"
