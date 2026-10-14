#!/bin/bash
# runall.sh <world> <games per method> <suffix> [VAR=value ...]: every method, the expert player with everything agreed switched on
W=$1; N=$2; S=$3; shift 3
env DET=smart ORSMART=1 PARALLEL=1 RUNON=1 DIFF=1 OBS=0 GLIMPSE=0.1 END=2 ENDRULE=active INSTR_D=5 LEVERS=abcrw "$@" \
  bash /home/user/Uncharted-Horizons/design/simulator/power/scratch_run.sh bash -c "cd /home/user/Uncharted-Horizons/design/simulator/power && timeout 115 python3 w7f.py $W $N $S" 2>&1 | grep -v "scratch redesign" | grep "done\|WARNING\|Error" | sed "s/^/$W $S: /"
