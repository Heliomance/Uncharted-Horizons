#!/bin/bash
# make_pool.sh <world> <tag> [VAR=value ...]: the rivals' records that knowledge diffusion (DIFF=1) replays, made under the given
# settings so that rivals face the same prices and eras as the player; runs then read them with POOLTAG=<tag>. Ten games a method,
# each a sensible detective (DET=smart) with no Endeavours and no diffusion of its own, run on until certain and built (the old
# pool, results/w7f_<world>_pool.json, was made under an earlier tree and cannot be reproduced).
if [ $# -lt 2 ]; then echo "usage: $(basename "$0") <world> <tag> [VAR=value ...]" >&2; exit 2; fi
W=$1; T=$2; shift 2
env DET=smart RUNON=1 SAVE_T=1 SEED0=27000 TRUTHSEED=77 OBS=0 GLIMPSE=0.1 GLIMPSEU=0.03 INSTR_D=5 "$@" \
  bash /home/user/Uncharted-Horizons/design/simulator/power/scratch_run.sh bash -c "cd /home/user/Uncharted-Horizons/design/simulator/power && timeout 200 python3 w7f.py $W 10 _pool$T" 2>&1 | grep -v "scratch redesign" | sed "s/^/pool $W $T: /"
