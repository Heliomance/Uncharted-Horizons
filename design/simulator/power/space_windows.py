"""Do Space-era occurrence windows close before the FTL race is won? (Tamsin's question, 14 Oct 2026)

For each benchmark game that finishes: when the civilisation's development reaches the Space era, against the end of
research (certainty and the build both done); how many Space-era STANDARD rows open before then, how long before the end
they open, and how many are lost first (and whether the player was targeting them when they were lost).

Step 1, the games, with the engine's accounts written by w7f.py (ACCT); the results files match compare_settings.sh's:
  D=<dir>; for p in X:runcell N:runnov A:runavg; do for m in Warp Wormhole Hyperspace Tachyonic Tunnelling; do
    PYTHONHASHSEED=0 ACCT=$D/<label>_${p%%:*}_$m.json bash ${p##*:}.sh familiar $m _tmp [VAR=value ...]; done; done
Step 2:  bash scratch_run.sh python3 space_windows.py <dir> <label> ...
"""
import sys, os, json, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import defaults, harness_ftl_e as HF   # noqa: F401

R = HF.ROWS; D = sys.argv[1]; W = HF.TURNS['Space'] * 0.5
SP = {k for k in R if R[k]['era'] == 'Space' and R[k]['tier'] == 'STANDARD'}
print(f"{len(SP)} Space-era STANDARD rows; their window {W:.1f} turns before any compression")
for lab in sys.argv[2:]:
    for p, name in (('X', 'expert'), ('N', 'novice'), ('A', 'average')):
        G = []
        for m in ('Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling'):
            path = f'{D}/{lab}_{p}_{m}.json'
            if os.path.exists(path): G += json.load(open(path))
        fin = [g for g in G if g['cert'] and g['built']]
        if not fin: continue
        rows = []
        for g in fin:
            end = max(g['cert'], g['built']); op = g['opened']; la = g['lost_at']; e = g.get('space_entry_turn')
            reached = bool(e and e <= end)
            opened = [k for k in SP if k in op and op[k] <= end]
            lost = [k for k in opened if k in la and la[k][0] <= end]
            rows.append(dict(end=end, reached=reached, lead_entry=(end - e) if reached else None, opened=len(opened),
                             early=sum(1 for k in opened if not reached or op[k] < e), full=sum(1 for k in opened if end - op[k] > W),
                             lost=len(lost), lost_t=sum(1 for k in lost if la[k][2]), lead=[end - op[k] for k in opened]))
        mean = lambda key: st.mean(r[key] for r in rows)
        lead = [x for r in rows for x in r['lead']]; ent = [r['lead_entry'] for r in rows if r['reached']]
        print(f"{lab} {name} ({len(fin)} of {len(G)} finished): development reaches the Space era before research ends in "
              f"{sum(r['reached'] for r in rows) / len(rows):.0%} of games ({st.median(ent) if ent else 0:.0f} turns before, median); "
              f"Space STANDARD rows opened {mean('opened'):.1f} a game ({mean('early'):.1f} before the era), {st.median(lead):.0f} turns before the end "
              f"(median), {mean('full'):.1f} open longer than a window; lost {mean('lost'):.2f} a game ({mean('lost_t'):.2f} of them targets); "
              f"games losing one {sum(1 for r in rows if r['lost']) / len(rows):.0%}, losing a target {sum(1 for r in rows if r['lost_t']) / len(rows):.0%}")
