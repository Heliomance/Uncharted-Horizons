#!/bin/bash
# compare_settings.sh <world> <label> [VAR=value ...]: the three benchmark players (expert, novice, average) on every FTL
# method of one world, under the given settings, four runs at a time, with PYTHONHASHSEED fixed so that two settings
# compare cleanly. Results: results/w7f_<world>_cmp<label><X|N|A>_<method>.json; tabulate with
#   python3 victory_table.py <world> <label>=_cmp<label>{p}_{m} ...
P=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [ $# -lt 2 ] || { [ -n "$3" ] && [[ "$3" != *=* ]]; }; then echo "usage: $(basename "$0") <world> <label> [VAR=value ...]" >&2; exit 2; fi
W=$1; LABEL=$2; shift 2; EXTRA="$*"
if [ "$W" = familiar ]; then LAST=Tunnelling; else LAST=Plenum; fi
for m in Warp Wormhole Hyperspace Tachyonic $LAST; do
  for p in X:runcell N:runnov A:runavg; do
    echo "PYTHONHASHSEED=0 bash $P/${p##*:}.sh $W $m _cmp${LABEL}${p%%:*}_$m $EXTRA"
  done
done | xargs -P 4 -I CMD bash -c CMD
