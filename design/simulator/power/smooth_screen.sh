#!/bin/bash
# smooth_screen.sh <label> [Era=x ...]: one candidate of the era-smoothing pass (Tamsin, 15 Oct 2026), screened on three victory
# conditions (familiar Warp, Process Tachyonic, Substance Plenum): rivals made under its settings (make_pool.sh), all three players
# with every discovery turn saved, then each player's victory, era entry by count against development, and turns per discovery by
# era (era_pace.py). Settings from smooth.py; eras with underscores (Early_Modern=0.85); ALLCAPS=value passes any other setting
# (POOLTAG=<tag> reuses rivals already made, for settings that leave prices and eras alone, such as diffusion's).
P=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); cd "$P" || exit 1
L=$1; shift; ERAS=(); EXTRA=""
for a in "$@"; do if [[ "${a%%=*}" =~ ^[A-Z0-9_]+$ ]]; then EXTRA="$EXTRA $a"; else ERAS+=("$a"); fi; done   # ALLCAPS=value: other settings
V="$(python3 smooth.py "${ERAS[@]}" 2>/dev/null | grep -v "^scratch")$EXTRA"; export PYTHONHASHSEED=0
echo "== $L: $* -> $V"
PT=$L; if [[ "$EXTRA" =~ POOLTAG=([^ ]+) ]]; then PT=${BASH_REMATCH[1]}   # rivals given (prices and eras unchanged): no new pool
else for w in familiar Process Substance; do bash make_pool.sh $w $L $V | grep -v "50 of 50"; done; fi
for wm in familiar:Warp Process:Tachyonic Substance:Plenum; do w=${wm%%:*}; m=${wm##*:}
  for p in X:runcell N:runnov A:runavg; do bash ${p##*:}.sh $w $m _${L}${p%%:*}_$m SAVE_T=1 $V POOLTAG=$PT | grep -v "60 of 60"; done; done
env $V python3 smooth_report.py $L familiar:Warp Process:Tachyonic Substance:Plenum 2>&1 | grep -v "^scratch"
env $V python3 era_pace.py _$L familiar:Warp Process:Tachyonic Substance:Plenum 2>&1 | grep -E "^\| [A-Z]" | cut -d'|' -f1-5
