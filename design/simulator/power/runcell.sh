#!/bin/bash
# runcell.sh <world> <method> <levers> <suffix> [VAR=value ...]: 60 games of one method under the standard player with everything agreed switched on
W=$1; M=$2; L=$3; S=$4; shift 4
env DET=smart ORSMART=1 PARALLEL=1 RUNON=1 DIFF=1 OBS=0 GLIMPSE=0.1 END=2 ENDRULE=active INSTR_D=5 LEVERS=$L METHODS=$M "$@" \
  bash /home/user/Uncharted-Horizons/design/simulator/power/scratch_run.sh bash -c "cd /home/user/Uncharted-Horizons/design/simulator/power && timeout 110 python3 w7f.py $W 60 $S" 2>&1 | grep -v "scratch redesign" | grep "done\|WARNING\|Error\|error" | sed "s/^/$W $M $S: /"
