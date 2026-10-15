#!/bin/bash
# runcell.sh <world> <method> <suffix> [VAR=value ...]: 60 games of one method by the expert benchmark player, on the
# finalised design (defaults.py). VAR=value overrides any setting, e.g. LEVERS=abc or SPACEPRICE=1.
# The expert, retuned for v3.122's prices (15 Oct 2026): it chases the unified theory's chain first (EXPFIX=1) but never
# targets a row whose ahead-of-time premium exceeds 2 (EXPCAP=2), and commissions an Endeavour only for the last thing the race
# waits on (ENDRULE=last); before, ENDRULE=active and no cap (all 15 victory conditions: median 326 -> 323, mean 326.1 -> 323.8).
if [ $# -lt 3 ] || { [ -n "$4" ] && [[ "$4" != *=* ]]; }; then
  echo "usage: $(basename "$0") <world> <method> <suffix> [VAR=value ...]  (the finalised levers and Space price are now the defaults; override with LEVERS=..., SPACEPRICE=...)" >&2; exit 2
fi
W=$1; M=$2; S=$3; shift 3
env DET=smart ORSMART=1 PARALLEL=1 RUNON=1 DIFF=1 OBS=0 GLIMPSE=0.1 GLIMPSEU=0.03 END=2 ENDRULE=last EXPCAP=2 INSTR_D=5 EXPFIX=1 ENDFROM=theory METHODS=$M "$@" \
  bash /home/user/Uncharted-Horizons/design/simulator/power/scratch_run.sh bash -c "cd /home/user/Uncharted-Horizons/design/simulator/power && timeout 110 python3 w7f.py $W 60 $S" 2>&1 | grep -v "scratch redesign" | grep "done\|WARNING\|Error\|error" | sed "s/^/$W $M $S: /"
