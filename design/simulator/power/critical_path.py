"""Critical-path analysis of time to certainty (W7/W17). For each certain game in results/w7e_<world>_abc.json: find the row whose
discovery completed certainty, then walk back through its prerequisites, at each step following the BINDING one (the group satisfied
last, and within it the latest row of the option that satisfied it), until the chain reaches rows discovered before the unified theory.
Run inside scratch_run.sh with the same LEVERS, so prerequisites match the games. Usage: critical_path.py <world>"""
import sys, json, collections, statistics as st; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
from defaults import TREE   # the design document (or a run's patched copy)
import worlds as W, gen_data as G
wname = sys.argv[1]; world = None if wname == 'familiar' else wname
_rows = W.set_world(world); groups = {k: G.prereq_groups(k) for k in _rows}
CLOSE = 'QP08' if world is None else 'QM-E27'
HOSTS = {'QP11', 'QP09', 'QP10', 'MS08', 'RC07', 'RC11', 'RC05', 'CP21', 'QP14', 'RC06', 'QP06', 'QM-E06', 'QM-E12', 'QM-E17', 'QM-E19', 'AE20'}
INF = float('inf'); runs = json.load(open(f'/home/user/Uncharted-Horizons/design/simulator/power/results/w7e_{wname}_abc.json'))
def ready(k, t):   # turn this row's prerequisites were all met, and the binding prerequisite
    best = (-INF, None)
    for g in groups.get(k, []):
        opts = []
        for o in g:
            ts = [(t.get(p, INF), p) for p in o if p in _rows]
            if ts: opts.append(max(ts))
        if opts: best = max(best, min(opts))
    return best
def chain(k, t, K):
    path = [k]
    while True:
        tr, p = ready(k, t)
        if p is None or tr < K: return path
        path.append(p); k = p
import re
NAMES = {m.group(1): m.group(2) for m in re.finditer(r'^\| ([A-Z]{2,3}(?:-[A-Z]+)?\d+) \| \*\*([^*]+)\*\*', open(TREE, encoding='utf-8').read(), re.M)}
name = lambda k: NAMES.get(k, k)
trig, on_chain, wait, arrive, chains, depth = collections.Counter(), collections.Counter(), collections.defaultdict(list), collections.defaultdict(list), collections.Counter(), []
theory = collections.defaultdict(list); n = 0
for r in runs:
    if not r['cert']: continue
    n += 1; t = r['t']; C, K = r['cert'], r['close']
    cands = [k for k in t if t[k] == C and (k in HOSTS or k == CLOSE)]
    k0 = max(cands, key=lambda k: k == CLOSE) if cands else None   # prefer a host; CLOSE only if certainty came with the theory
    k0 = [k for k in cands if k != CLOSE][0] if any(k != CLOSE for k in cands) else (cands[0] if cands else None)
    if k0 is None: continue
    trig[k0] += 1; theory[k0].append(C - K)
    p = chain(k0, t, K); depth.append(len(p)); chains[' <- '.join(p)] += 1
    for k in set(p): on_chain[k] += 1
    for k in p:
        arrive[k].append(t[k] - K); tr, _ = ready(k, t); wait[k].append(t[k] - max(tr, K))
md = lambda x: st.median(x) if x else float('nan')
print(f"== {wname}: {n} certain games, critical chain median {md(depth):.0f} rows long (rows found after the unified theory, the completing row included)")
print("   Row completing certainty            games  theory median")
for k, c in trig.most_common(): print(f"   {k:7} {name(k)[:28]:28} {c:>5}  {md(theory[k]):>6.0f}")
print("   Rows on the critical chain         share  arrives (med)  waited after prereqs met (med)")
for k, c in on_chain.most_common(14): print(f"   {k:7} {name(k)[:28]:28} {c/n:>5.0%}  {md(arrive[k]):>6.0f}  {md(wait[k]):>8.0f}   [{_rows[k]['era']}, {_rows[k]['tier']}, {_rows[k]['focus'][:22]}]")
print("   Commonest chains:")
for s, c in chains.most_common(6): print(f"   {c:>3}x  {s}")
