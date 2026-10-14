"""W7f (from W7d): detectives and design levers. Env: DET=simple|smart, END=<Endeavour cost multiplier>, LEVERS letters a,b,c (W14), r (RC06 sibling of RC05, in the patch), t (open questions draw 3x attention). W7d (from W7c): theory, then the true method's engineering. W7c: time to certainty under the final condition sets (three per method), for a detective that funds only the tests
that can still matter. Runs on the scratch redesign (via scratch_run.sh). Writes results to power_tools/results/."""
import sys, json, itertools, random, statistics as st; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import harness_ftl_e as HF, worlds as W, gen_data as G
world = None if sys.argv[1] == 'familiar' else sys.argv[1]; N = int(sys.argv[2])
_rows = W.set_world(world); HF.ROWS = _rows; HF.IDS = sorted(_rows); HF.FOCUS = {k: _rows[k]['focus'] for k in HF.IDS}; HF.ERA_I = {k: HF.EO.index(_rows[k]['era']) for k in HF.IDS}
if world is None:
    HOST = {'exotic': ['QP11'], 'extradim': ['QP09', 'QP10'], 'discrete': ['QP09', 'QP10'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'],
            'leak': ['RC11'], 'dark': ['RC05'], 'coherence': ['CP21'], 'hartman': ['QP14'], 'tachDE': ['RC06'], 'tachyon': ['QP15']}   # v3.112: the sector is tested beyond the Standard Model (W1), not on QP06
    COND = {'Warp': ['exotic', 'extradim', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['extradim', 'leak', 'dark'],
            'Tunnelling': ['coherence', 'discrete', 'hartman'], 'Tachyonic': ['tachDE', 'closed', 'tachyon']}
    CLOSE = 'QP08'; ok = lambda a: a['discrete'] != a['extradim'] and (a['extradim'] or not a['leak'])
else:
    HOST = {'exotic': ['QM-E06'], 'strata': ['QM-E12'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'], 'leak': ['RC11'], 'dark': ['RC05'],
            'superlum': ['RC06'], 'catalogue': ['QM-E28'], 'currents': ['QM-E19'], 'coupling': ['AE20']}
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
ORSMART = os.environ.get('ORSMART') == '1' if 'os' in dir() else False
def _cost(k): return HF.PRICE[_rows[k]['era']] * HF.COSTMULT.get(k, 1.0)
def smart_targets(reqs, have):
    """The undiscovered rows a thoughtful player would pursue for a list of requirements, each a list of alternative rows.
    For every either-or choice, down the whole tree: an option already met settles it; options that cannot exist in this
    world are ignored; otherwise the option whose undiscovered rows cost least in total is chosen."""
    memo = {}
    def need(k):
        if k in have: return frozenset()
        if k not in _rows: return None
        S_ = HF.STATE
        if k in S_.get('lost', ()) and k not in S_.get('glimpsed', ()) and k not in S_.get('diff', {}) and k not in S_.get('diff_unc', {}): return None   # an idea that isn't coming
        if k in memo: return memo[k]
        memo[k] = frozenset([k]); req = {k}
        for grp in _rows[k]['pre']:
            best = None
            for opt in grp:
                s = set(); ok = True
                for p in opt:
                    q = need(p)
                    if q is None: ok = False; break
                    s |= q
                if not ok: continue
                if not s: best = (0, set()); break
                c = sum(_cost(x) for x in s)
                if best is None or c < best[0]: best = (c, s)
            if best is None: memo[k] = None; return None
            req |= best[1]
        memo[k] = frozenset(req); return memo[k]
    out = set()
    for alts in reqs:
        opts = [q for q in (need(a) for a in alts) if q is not None]
        if not opts or any(len(q) == 0 for q in opts): continue
        out |= min(opts, key=lambda q: sum(_cost(x) for x in q))
    return out
import os, collections
ORSMART = os.environ.get('ORSMART') == '1'
NOVICE = os.environ.get('PLAYER') == 'novice'
HEDGE = os.environ.get('HEDGE', 'open')   # expert: when hedged engineering starts (open | theory | first | two | never)
def hint_row(alts, have):
    """the step an FTL-screen hint is waiting on: the cheapest workable next step on the cheapest path"""
    fr = [k for k in smart_targets([alts], have) if HF.prereqs_met(k, have)]
    return min(fr, key=_cost) if fr else None
def hint_focus(alts, have):
    """the field an FTL-screen hint points to for a requirement"""
    k = hint_row(alts, have); return HF.FOCUS[k] if k else None
EXPFIX = os.environ.get('EXPFIX') == '1'
NOVFOCUS = os.environ.get('NOVFOCUS') == '1'   # novice: Endeavour only the step holding up the field it is funding
NOVEND = int(os.environ['NOVEND']) if os.environ.get('NOVEND') else None   # novice: turns a revealed step may hold things up before an Endeavour
BLOCK = {}
SPEC = os.environ.get('PLAYER') == 'specialist'
FTLF = {'Computing', 'Energy Systems', 'Materials Science', 'Mathematics', 'Nuclear Physics', 'Thermodynamics', 'Aeronautics', 'Quantum Physics', 'Relativity & Cosmology', 'Quintessic Physics', 'Rocketry', 'Space Engineering'}
def spec_target(have, state):
    """non-science specialist: fund one wanted field until two or fewer of its breakthroughs remain undiscovered, then pick another.
    Moves on early if nothing in the field is workable, or nothing has arrived there for 15 turns. Prefers non-FTL fields."""
    now = HF.CLOCK['turn']; F = state.get('focus')
    undisc = lambda f: [k for k, r in _rows.items() if r['focus'] == f and k not in have]
    workable = lambda f: any(HF.prereqs_met(k, have) for k in undisc(f))
    if F is not None:
        if any(_rows.get(k, {}).get('focus') == F and tt > state['since'] for k, (tt, d) in have.items()): state['since'] = now
        if len(undisc(F)) <= 2 or not workable(F) or now - state['since'] > 15: F = None
    if F is None:
        cands = sorted(f for f in {r['focus'] for r in _rows.values()} if len(undisc(f)) > 2 and workable(f))
        pref = [f for f in cands if f not in FTLF] or cands
        if pref: F = state['srng'].choice(pref); state['since'] = now; state.setdefault('seq', []).append((now, F))
    state['focus'] = F
    return set(undisc(F)) if F else set()
def hint_pick(reqs, have):
    """the novice's choice: the hinted field serving the most requirements (no idea of cost)"""
    cnt = collections.Counter(f for f in (hint_focus(r, have) for r in reqs) if f)
    return max(cnt, key=lambda f: (cnt[f], f)) if cnt else None
SIG = ('CP16', 'CP21', 'CP10', 'AE14', 'AE20', 'MS08', 'QM-E23', 'ES22', 'ES18', 'ES14', 'ES08', 'MA15', 'MA19', 'NP11', 'NP15', 'TH20')
HF.COSTMULT = {k: 2.5 for k in SIG}
if 'z' in os.environ.get('LEVERS', ''):   # assumed non-FTL pools: 2.5x, capstones 4x
    for k in _rows:
        if k.startswith('ZZ'): HF.COSTMULT[k] = 4.0 if k.endswith('C') else 2.5
if 'q' in os.environ.get('LEVERS', ''):   # W18 pool prices: entry and pool rows 2.5x, capstones 4x (round-two overrides apply later)
    for k in ('CP17','CP18','CP19','CP20','CP15','CP09','ES17','ES19','ES20','ES11','MS10','MS11','MS12','MS13','MS16','MA16','MA17','MA18','MA22','MA23','MA20',
              'NP12','NP13','NP16','NP-F03','TH15','TH16','TH17','TH18','TH21','AE15','AE16','AE17','AE18'): HF.COSTMULT[k] = 2.5
    for k in ('CP22','CP12','ES21','ES12','QM-E07','MS15','MS07','MA21','NP17','NP09','NP-F04','TH22','AE19'): HF.COSTMULT[k] = 4.0
if 'a' in os.environ.get('LEVERS', ''):
    for k in ('CP21', 'MS08', 'AE20'): HF.COSTMULT[k] = 1.0      # lever a: rows that host a condition cost as deciders do
if world is None:
    BUILD = {'Warp': [['RC02'], ['QP08'], ['QP11'], ['MS08'], ['ES06', 'ES07', 'ES14', 'ES08'], ['ES18']], 'Wormhole': [['RC02'], ['QP08'], ['QP11'], ['MS08'], ['RC04'], ['QP12'], ['MA13']],
             'Hyperspace': [['QP08'], ['MA13'], ['ES06', 'ES07', 'ES14', 'ES08'], ['MA19']], 'Tunnelling': [['QP02'], ['CP10'], ['MS02', 'GN05'], ['QP14'], ['CP21']],
             'Tachyonic': [['QP06'], ['QP08'], ['NP11'], ['SE02'], ['ES06', 'ES07', 'ES14', 'ES08'], ['NP15']]}
else:
    BUILD = {'Warp': [['RC02'], ['QM-E27'], ['QM-E06'], ['MS08'], ['ES07', 'ES15', 'QM-E05'], ['ES18']], 'Wormhole': [['RC02'], ['QM-E27'], ['QM-E06'], ['MS08'], ['RC04'], ['QM-E13'], ['MA13']],
             'Hyperspace': [['QM-E27'], ['MA13'], ['ES07', 'ES15', 'QM-E05'], ['MA19']], 'Tachyonic': [['QM-E17'], ['QM-E27'], ['ES07', 'ES15', 'QM-E05'], ['SE02'], ['TH20']],
             'Plenum': [['QM-E27'], ['MS02'], ['QM-E19'], ['QM-E23'], ['AE20']]}
import os
if 'a' in os.environ.get('LEVERS', ''): HF.COSTMULT.update({k: 1.0 for k in ('CP21', 'MS08', 'AE20')})   # lever a: rows hosting a condition cost 1x
INSTR_D = int(os.environ['INSTR_D']) if os.environ.get('INSTR_D') else None   # instruments: construction turns after the test's breakthrough
INSTR = {'coherence': ['CP21'], 'leak': ['RC11'], 'dark': ['RC05', 'RC06'], 'tachDE': ['RC05', 'RC06'], 'superlum': ['RC05', 'RC06'], 'tachyon': ['QP15'], 'catalogue': ['QM-E28']}   # + the Very Large Particle Collider / Boundary Furnace   # the Survey Telescope serves dark matter and dark energy
def ready_turn(c, have):
    """turn at which condition c's answer is available: its host's discovery, or, for a measurement, its instrument's completion"""
    hosts = [have[h][0] for h in HOST[c] if h in have]
    if not hosts: return None
    if INSTR_D is None or c not in INSTR: return min(hosts)
    unl = [have[u][0] for u in INSTR[c] if u in have]
    return max(min(hosts), min(unl) + INSTR_D)
def knowledge(have, a):
    """conditions whose result is known, given what's discovered and the world's truth (MS08 exists only where exotic matter does)"""
    kn = {}
    for c, hosts in HOST.items():
        rt = ready_turn(c, have) if any(h in have for h in hosts) else None
        if rt is not None and rt <= HF.CLOCK['turn'] and not (hosts == ['MS08'] and not a['exotic']): kn[c] = a[c]
    return kn
def status(have, m, a):
    kn = knowledge(have, a)
    alive = [o for o in COND if not any(c in kn and not kn[c] for c in COND[o])]
    certain = CLOSE in have and (all(kn.get(c) for c in COND[m]) or alive == [m])
    return kn, alive, certain
HF.POLICY = 'cheapest' if os.environ.get('DET') == 'smart' else 'waiting'
HF.END_MULT = float(os.environ['END']) if os.environ.get('END') else None
HF.END_FROM = HF.EO.index('Space')
HF.OBS = os.environ.get('OBS', '1') == '1'; HF.GLIMPSE = float(os.environ.get('GLIMPSE', '0'))
HF.END_AFTER = CLOSE if os.environ.get('ENDFROM') == 'theory' else None   # Endeavours only once the unified theory is known
ENDRULE = os.environ.get('ENDRULE', 'naive'); HF.END_RULE = 'active' if ENDRULE in ('active', 'last') else 'naive'   # naive: vs observed rate; active: vs activating the row's focus; last: active, on the last missing piece only   # Endeavours chase FTL requirements once the Space era opens
ATT = 't' in os.environ.get('LEVERS', '')
rng = random.Random(int(os.environ.get('TRUTHSEED', '31'))); out = []
METHODS = [x for x in os.environ.get('METHODS', '').split(',') if x]
_L = os.environ.get('LEVERS', '')
PARALLEL = os.environ.get('PARALLEL') == '1'
HF.ECON = float(os.environ.get('ECON', '1'))
HF.EXPCAP = float(os.environ['EXPCAP']) if os.environ.get('EXPCAP') else None; HF.EXPCAP_ERA = HF.EO.index(os.environ['EXPCAP_ERA']) if os.environ.get('EXPCAP_ERA') else None
if os.environ.get('SPACEPRICE'): HF.PRICE['Space'] *= float(os.environ['SPACEPRICE'])   # the Space era's base research price, scaled (every Space-era row's cost derives from it)
if 'w' in _L: BUILD['Wormhole'].append(['MS17']); HF.COSTMULT['MS17'] = float(os.environ.get('WROWX', '2.5'))   # Wormhole's engineering row outside its tests
if 'y' in _L and world is None: BUILD['Tachyonic'] = [g for g in BUILD['Tachyonic'] if g != ['NP11']]   # scenario: atomic Tachyonic without NP11 in its build
if 'x' in _L: HF.COSTMULT['ES18'] = 1.0
if 'p' in _L: HF.COSTMULT['AE14'] = 1.0
if 'h' in _L: HF.COSTMULT['MA19'] = 1.0                                          # round 2: Hyperspace's Higher-Dimensional Geometry at 1x
if 'u' in _L: HF.COSTMULT['CP16'] = 1.0                                          # round 2: Tunnelling's Planetary Data Networks at 1x
if 'k' in _L: HF.COSTMULT['TH20'] = 4.0
if 'm' in _L: HF.COSTMULT['CP10'] = 2.0                                          # agreed nudge: Tunnelling's Quantum Computing at 2x                                          # round 2: elemental Tachyonic's Boundary Ring at 4x                                          # scenario: Plenum's entry row, Aerospace Industry, at 1x                                          # scenario: Superconducting Energy Storage at 1x
SEED0 = int(os.environ.get('SEED0', '17000'))
POOL = json.load(open(f"/home/user/Uncharted-Horizons/design/simulator/power/results/w7f_{sys.argv[1]}_pool.json")) if os.environ.get('DIFF') == '1' else None
for s in range(N * len(COND)):
    m = list(COND)[s % len(COND)]; a = rng.choice(TRUTHS[m]); state = {'cert': None, 'srng': random.Random(SEED0 + s + 7919)}
    if METHODS and m not in METHODS: continue          # skip after the draw, so every game keeps its truth and seed
    def target(have, m=m, a=a, state=state):
        if SPEC: return spec_target(have, state)
        kn, alive, certain = status(have, m, a)
        HF.ATTN = {h: 3.0 for c in HOST if c not in kn for h in HOST[c]} if ATT else {}   # lever t: open questions draw attention
        if state['cert'] is None and certain: state['cert'] = (max([have[CLOSE][0]] + [ready_turn(c, have) for c in kn]), len(kn))   # when the last needed answer arrived
        if NOVICE:                                                       # the novice follows only what the FTL screen shows
            HF.PRIORITY = set()
            if CLOSE not in have: return set()                           # before the unified theory there is nothing on the screen to follow
            if state['cert'] is not None: qreq, nreq = [], [g for g in BUILD[m] if not any(x in have for x in g)]
            else: qreq, nreq = [HOST[c] for c in {c for o in alive for c in COND[o] if c not in kn}], [g for o in alive for g in BUILD[o] if not any(x in have for x in g)]
            pick = hint_pick(qreq, have) or hint_pick(nreq, have)        # questions first; hedge only as the screen invites
            if NOVEND:                                                   # a revealed step that has held things up for a reasonable time: commission it
                now = HF.CLOCK['turn']; S_ = HF.STATE
                blocking = {hint_row(r, have) for r in qreq + nreq} - {None}
                rev = lambda k: _rows[k]['tier'] == 'CORE' or k in S_.get('occurred', ()) or k in S_.get('glimpsed', ())
                for k in list(BLOCK):
                    if k not in blocking or k in have or not rev(k): del BLOCK[k]
                if NOVFOCUS:                                             # only the step holding up the field actually funded; count funded turns
                    for k in blocking:
                        if rev(k) and HF.FOCUS[k] == pick: BLOCK[k] = BLOCK.get(k, 0) + 1
                    due = [k for k, n_ in BLOCK.items() if n_ >= NOVEND and HF.FOCUS[k] == pick]
                    HF.END_REQUEST = max(due, key=lambda k: BLOCK[k]) if due else None
                else:
                    for k in blocking:
                        if rev(k): BLOCK.setdefault(k, now)
                    due = [k for k, t0 in BLOCK.items() if now - t0 >= NOVEND]
                    HF.END_REQUEST = min(due, key=lambda k: BLOCK[k]) if due else None
            return {k for k in HF.IDS if HF.FOCUS[k] == pick} if pick else set()   # the funded field: its ideas keep their moment
        if state['cert'] is not None:
            if ENDRULE == 'last':
                left = [g for g in BUILD[m] if not any(o in have for o in g)]; HF.END_ONLY = with_anc(left[0]) if len(left) == 1 else set()
            HF.PRIORITY = set()
            if ORSMART: return smart_targets([g for g in BUILD[m] if not any(x in have for x in g)], have)
            return with_anc([o for g in BUILD[m] if not any(x in have for x in g) for o in g])   # engineering phase: only requirements not yet met
        need = {c for o in alive for c in COND[o] if c not in kn}
        if ENDRULE == 'last': HF.END_ONLY = with_anc([h for c in need for h in HOST[c]]) if len(need) == 1 and CLOSE in have else set()
        hosts = [h for c in need for h in HOST[c] if not (HOST[c] == ['MS08'] and kn.get('exotic') is False)]
        if ORSMART:
            tests = smart_targets([HOST[c] for c in need] + ([] if CLOSE in have else [[CLOSE]]), have)
            first = smart_targets([[CLOSE]], have) if (EXPFIX and CLOSE not in have) else None   # expert fix: the unified theory's own chain first
            if not PARALLEL:
                HF.PRIORITY = first or set(); return tests
            hedge = {'open': True, 'theory': CLOSE in have, 'first': len(alive) < len(COND), 'two': len(alive) <= 2, 'never': False}[HEDGE]
            if not hedge: HF.PRIORITY = first or set(); return tests
            HF.PRIORITY = first or tests                                          # parallel engineering: the builds of every method still possible, at lower priority
            return tests | smart_targets([g for o in alive for g in BUILD[o] if not any(x in have for x in g)], have)
        return with_anc(hosts + ([] if CLOSE in have else [CLOSE]))
    HF.TARGET_FN = target
    if os.environ.get('PLAYER') == 'generalist': HF.TARGET_FN = None   # no FTL agenda: fund the field with the most work waiting
    if os.environ.get('PLAYER') == 'aspirant':   # no FTL agenda: pursue the Space-era content of chosen fields (ASPIRE=all or field names joined by ';')
        _asp = os.environ.get('ASPIRE', 'all'); _fs = None if _asp == 'all' else set(_asp.split(';'))
        _sp = [k for k, r in _rows.items() if r['era'] == 'Space' and (_fs is None or r['focus'] in _fs)]
        HF.TARGET_FN = lambda have, _sp=_sp: smart_targets([[k] for k in _sp if k not in have], have)
    HF.RUN_ON = os.environ.get('RUNON') == '1'
    HF.STOP_FN = (lambda have, m=m, state=state: state['cert'] is not None and all(any(o in have for o in g) for g in BUILD[m])) if HF.RUN_ON else None
    if os.environ.get('PLAYER') in ('generalist', 'aspirant', 'specialist'): HF.STOP_FN = None
    if POOL is not None:                  # five rivals with the same viable method, replayed from the pool (different seeds)
        pm = [r for r in POOL if r['m'] == m]; j0 = (s // len(COND)) * 5
        HF.DIFF = dict(rivals=[{k: v / HF.ECON for k, v in pm[(j0 + j) % len(pm)]['t'].items()} for j in range(5)], contact_era=HF.EO.index('Early Modern'))   # rivals at the player's own pace
    HF.DIFF_LOG.clear(); BLOCK.clear(); HF.END_REQUEST = None
    HF.TRACE = [] if os.environ.get('TRACE') else None
    HF.END_LOG.clear(); have, log = HF.run(HF.P(**json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/w7c_cfg.json'))), SEED0 + s, max_turns=int(os.environ.get('MAXT', '450'))); t = {k: tt for k, (tt, d) in have.items()}
    space = min((t[k] for k in t if _rows[k]['era'] == 'Space'), default=None)
    if os.environ.get('TRACE'):   # turn-by-turn trace of this one game: the expert's view of which methods remain, each turn
        _alive = {}
        for _T in range(1, (HF.TRACE[-1]['turn'] if HF.TRACE else 0) + 1):
            HF.CLOCK['turn'] = _T; _hT = {k: v for k, v in have.items() if v[0] <= _T}; _kn, _al, _ce = status(_hT, m, a); _alive[_T] = dict(alive=_al, known=_kn, certain=_ce)
        json.dump(dict(m=m, truth=a, seed=SEED0 + s, truthseed=int(os.environ.get('TRUTHSEED', '31')), records=HF.TRACE, alive=_alive, cert=state['cert'], ends=list(HF.END_LOG),
                       instr={c: INSTR.get(c) for c in HOST} if 'INSTR' in globals() else {}, instr_d=INSTR_D, close=CLOSE, focus=dict(HF.FOCUS)), open(os.environ['TRACE'], 'w'))
    diag = None
    if not state['cert']:
        kn, alive, _ = status(have, m, a)
        need = sorted({c for o in alive for c in COND[o] if c not in kn})
        def blockers(h):   # undiscovered rows on the way to h whose own prerequisites were met (missed ideas), else unmet chain
            miss = sorted(r for r in with_anc([h]) if r not in t and all(any(all(p in t for p in o) for o in g) for g in groups.get(r, []) if g))
            return miss
        diag = dict(alive=alive, unknown=need, close_known=CLOSE in t, blockers={c: sorted({b for h in HOST[c] for b in blockers(h)}) for c in need})
    built = max((min((t.get(o, 10**6) for o in g)) for g in BUILD[m]), default=None); built = None if built >= 10**6 else built
    gate = space   # the Endeavour gate opens with the first Space-era discovery
    why = {}
    if state['cert'] and built is None:            # why the build never completed: status of each missing option
        occ = HF.run.occ; opn = HF.run.opened
        for g in BUILD[m]:
            if any(o in have for o in g): continue
            for o in g:
                if o not in _rows: why[o] = 'not in this world'
                elif o not in opn:
                    miss = sorted({p for gg in groups.get(o, []) for p in min(gg, key=lambda op: sum(1 for q in op if q not in have)) if p not in have and p in _rows})
                    why[o] = 'prerequisites unmet: ' + ', '.join(miss[:4])
                elif _rows[o]['tier'] != 'CORE' and o not in occ and o not in HF.FUNDED: why[o] = f"idea never occurred ({_rows[o]['tier']})"
                else: why[o] = 'occurred, not yet found'
        def root(o, seen=None):   # follow unmet prerequisites down to rows whose own prerequisites were met
            seen = seen or set()
            if o in seen or o not in _rows: return set()
            seen.add(o)
            if o in opn: return {o}
            gs = groups.get(o, []); out = set()
            for gg in gs:
                if any(all(p in have for p in op if p in _rows) for op in gg): continue
                op = min(gg, key=lambda op: sum(1 for q in op if q not in have))
                for p in op:
                    if p not in have: out |= root(p, seen)
            return out
        roots = set()
        for g in BUILD[m]:
            if not any(o in have for o in g): roots |= set().union(*[root(o) for o in g])
        why['_roots'] = sorted(f"{r} [{_rows[r]['tier']}, {_rows[r]['era']}]: " + ('occurred, not found' if (r in occ or _rows[r]['tier'] == 'CORE') else 'idea never occurred') for r in roots)
        why['_end'] = f"stopped turn {log[-1][0] if log else '?'}, development {log[-1][1]:.2f}" if log else ''
    out.append(dict(seq=state.get('seq'), truth=a, t=(t if os.environ.get('SAVE_T') == '1' else None), diffs=list(HF.DIFF_LOG), why=why, gate=gate, ends=[e for e in HF.END_LOG], m=m, space=space, close=t.get(CLOSE), built=built, cert=state['cert'][0] if state['cert'] else None, results=state['cert'][1] if state['cert'] else None, diag=diag))
json.dump(out, open(f'/home/user/Uncharted-Horizons/design/simulator/power/results/w7f_{sys.argv[1]}{sys.argv[3] if len(sys.argv) > 3 else ""}.json', 'w')); print(sys.argv[1], 'done:', sum(1 for r in out if r['cert']), 'of', len(out), 'games reached certainty')
