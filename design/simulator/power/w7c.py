"""W7c: time to certainty under the final condition sets (three per method), for a detective that funds only the tests
that can still matter. Runs on the scratch redesign (via scratch_run.sh). Writes results to power_tools/results/."""
import sys, json, itertools, random, statistics as st; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import harness_ftl as HF, worlds as W, gen_data as G
world = None if sys.argv[1] == 'familiar' else sys.argv[1]; N = int(sys.argv[2])
_rows = W.set_world(world); HF.ROWS = _rows; HF.IDS = sorted(_rows); HF.FOCUS = {k: _rows[k]['focus'] for k in HF.IDS}; HF.ERA_I = {k: HF.EO.index(_rows[k]['era']) for k in HF.IDS}
if world is None:
    HOST = {'exotic': ['QP11'], 'extradim': ['QP09', 'QP10'], 'discrete': ['QP09', 'QP10'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'],
            'leak': ['RC11'], 'dark': ['RC05'], 'coherence': ['CP21'], 'hartman': ['QP14'], 'tachDE': ['RC06'], 'tachyon': ['QP06']}
    COND = {'Warp': ['exotic', 'extradim', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['extradim', 'leak', 'dark'],
            'Tunnelling': ['coherence', 'discrete', 'hartman'], 'Tachyonic': ['tachDE', 'closed', 'tachyon']}
    CLOSE = 'QP08'; ok = lambda a: a['discrete'] != a['extradim'] and (a['extradim'] or not a['leak'])
else:
    HOST = {'exotic': ['QM-E06'], 'strata': ['QM-E12'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'], 'leak': ['RC11'], 'dark': ['RC05'],
            'superlum': ['RC06'], 'catalogue': ['QM-E17'], 'currents': ['QM-E19'], 'coupling': ['AE20']}
    COND = {'Warp': ['exotic', 'strata', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['strata', 'leak', 'dark'],
            'Tachyonic': ['superlum', 'closed', 'catalogue'], 'Plenum': ['currents', 'superlum', 'coupling']}
    CLOSE = 'QM-E27'; ok = lambda a: a['strata'] or not a['leak']
VARS = sorted(HOST)
TRUTHS = {m: [a for a in (dict(zip(VARS, b)) for b in itertools.product([0, 1], repeat=len(VARS))) if ok(a)
              and all(a[c] for c in COND[m]) and all(not all(a[c] for c in COND[o]) for o in COND if o != m)] for m in COND}
groups = {k: G.prereq_groups(k) for k in HF.IDS}
def with_anc(roots):
    out = set(); stack = [r for r in roots if r in _rows]
    while stack:
        k = stack.pop()
        if k in out: continue
        out.add(k); stack += [p for g in groups.get(k, []) for o in g for p in o if p in _rows and p not in out]
    return out
HF.COSTMULT = {k: 2.5 for k in ('CP16', 'CP21', 'AE14', 'AE20', 'MS08', 'QM-E23')}
import os
if 'a' in os.environ.get('LEVERS', ''): HF.COSTMULT.update({k: 1.0 for k in ('CP21', 'MS08', 'AE20')})   # lever a: rows hosting a condition cost 1x
def knowledge(have, a):
    """conditions whose result is known, given what's discovered and the world's truth (MS08 exists only where exotic matter does)"""
    kn = {}
    for c, hosts in HOST.items():
        if any(h in have for h in hosts) and not (hosts == ['MS08'] and not a['exotic']): kn[c] = a[c]
    return kn
def status(have, m, a):
    kn = knowledge(have, a)
    alive = [o for o in COND if not any(c in kn and not kn[c] for c in COND[o])]
    certain = CLOSE in have and (all(kn.get(c) for c in COND[m]) or alive == [m])
    return kn, alive, certain
rng = random.Random(31); out = []
for s in range(N * len(COND)):
    m = list(COND)[s % len(COND)]; a = rng.choice(TRUTHS[m]); state = {'cert': None}
    def target(have, m=m, a=a, state=state):
        kn, alive, certain = status(have, m, a)
        if state['cert'] is None and certain: state['cert'] = (max(t for t, d in have.values()), len(kn))
        if state['cert'] is not None: return set()
        need = {c for o in alive for c in COND[o] if c not in kn}
        hosts = [h for c in need for h in HOST[c] if not (HOST[c] == ['MS08'] and kn.get('exotic') is False)]
        return with_anc(hosts + ([] if CLOSE in have else [CLOSE]))
    HF.TARGET_FN = target
    have, log = HF.run(HF.P(**json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/w7c_cfg.json'))), 17000 + s); t = {k: tt for k, (tt, d) in have.items()}
    space = min((t[k] for k in t if _rows[k]['era'] == 'Space'), default=None)
    diag = None
    if not state['cert']:
        kn, alive, _ = status(have, m, a)
        need = sorted({c for o in alive for c in COND[o] if c not in kn})
        def blockers(h):   # undiscovered rows on the way to h whose own prerequisites were met (missed ideas), else unmet chain
            miss = sorted(r for r in with_anc([h]) if r not in t and all(any(all(p in t for p in o) for o in g) for g in groups.get(r, []) if g))
            return miss
        diag = dict(alive=alive, unknown=need, close_known=CLOSE in t, blockers={c: sorted({b for h in HOST[c] for b in blockers(h)}) for c in need})
    out.append(dict(m=m, space=space, close=t.get(CLOSE), cert=state['cert'][0] if state['cert'] else None, results=state['cert'][1] if state['cert'] else None, diag=diag))
json.dump(out, open(f'/home/user/Uncharted-Horizons/design/simulator/power/results/w7c_{sys.argv[1]}{sys.argv[3] if len(sys.argv) > 3 else ""}.json', 'w')); print(sys.argv[1], 'done:', sum(1 for r in out if r['cert']), 'of', len(out), 'games reached certainty')
