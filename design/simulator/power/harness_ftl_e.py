"""Discovery-model comparison harness, second version.

Models
  T      threshold — generator positions; a total gate half an era (in era terms) before the position;
         running-total focus gates; one discovery per focus per turn; per-turn rolls whose moment passes.
  R      pure rate — attention shared by weight; chance per turn = attention ÷ price (a breakthrough can absorb
         at most its price per turn).
  Pmom   parallel progress with momentum — attention favours lines already under way.
  Pone   one line at a time — a focus pursues one breakthrough, drawn by weight, until found; progress persists.
In R and the P forms, price = era price × premium^(eras ahead of development), and a non-CORE breakthrough
competes only once its idea has *occurred* — a per-turn chance while its moment lasts, sized to the tier target.

Routings
  none   Insight a focus cannot use is lost (T keeps it in the focus: nothing is spent there).
  spill  Insight a focus cannot use this turn goes at once to the other open foci.
  bank   when a focus's last open discovery is made, its unspent Insight is kept and goes next turn to the new focus.
"""
import sys, math, random, statistics as st, json
sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import gen_data as G, generator as GN, eramodel as M, ledger as Lg, harness as H0
from harness import ROWS, IDS, FOCUS, PRICE, TARGET, ERA_I, EO, TURNS, income, dev, prereqs_met

SPAN_E = len(EO)
def total_gate(pos, slack):
    """a position moved back by `slack` eras, on the timeline (the fix: slack in era terms)"""
    c = GN.era_coord(pos) - slack
    if c <= 0: return 0.0
    i = min(int(c), SPAN_E - 1); return GN.at(i, c - i)

class P:
    def __init__(self, **kw):
        self.model = 'R'; self.routing = 'none'; self.player = 'balanced'
        self.spill = 0.30; self.slack = 0.5; self.premium = 4.0; self.shape = 4.0; self.momentum = 0.1
        self.scale = 1.0; self.accelerate = {}; self.accel_T = 'whole'
        self.blocked_focus = None; self.unblock_dev = None; self.grace = 0.5
        self.compress = 0.0          # >0: an idea behind history occurs faster — window ÷ (1 + compress × eras behind)
        self.window = {'STANDARD': 1.0, 'UNCOMMON': 1.0, 'RARE': 1.0, 'UNIQUE': 1.0}   # occurrence-window multipliers by tier
        self.accel_occ = {}          # {row: factor} — accelerator on the occurrence window (0.5 = the idea comes twice as fast)
        self.accel_price = {}        # {row: factor} — accelerator on the price
        self.accel_head = {}         # {row: fraction} — accelerator as a head start on the meter (P forms)
        self.spread_floor = 0.1
        self.linear = False          # R: chance = min(1, attention ÷ price) instead of 1 − e^(−attention ÷ price)
        self.fade = None             # None: an idea's moment closes (the window). A number: no window; instead attention to an open question
                                     # fades, halving every `fade` eras of development since it opened (Tamsin's proposal, 14 Oct 2026)
        self.fade_funded = True      # fade: whether the active focus fades too (False: funding a field revives its stale questions)
        self.fade_clock = 'opened'   # fade: staleness counted from when the question opened; 'era': from the end of its own era;
                                     # 'later': from whichever comes later (on-time rows stay fresh through their era, late openers start fresh)
        self.fade_tiers = ('STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE')   # the tiers that fade; the others keep the closing window
        self.__dict__.update(kw)

# W7f copy with three switches: POLICY (focus choice), ATTN (attention weights), END_MULT (Grand Endeavours). Measurement copy of harness2: a research-target hook (TARGET_FN), W16's funded-focus rule (FUNDED), price multipliers (COSTMULT).
TARGET_FN = None; FUNDED = set(); COSTMULT = {}
POLICY = 'waiting'; ATTN = {}; END_MULT = None; END_LOG = []; END_RULE = 'naive'; END_ONLY = None; END_AFTER = None; END_FROM = None; RUN_ON = False; STOP_FN = None
DIFF = None; DIFF_LOG = []
ECON = 1.0   # income relative to the calibrated (good player's) economy
STATE = {}   # live references to lost, glimpsed and diffusing ideas
END_REQUEST = None   # a row the player asks to pursue as an Endeavour (END_RULE 'request')
PRIORITY = set()   # targets that take the active focus first (the tests, during the investigation)
EXPCAP = None; EXPCAP_ERA = None   # premium cap: never make a target the active focus while its premium exceeds EXPCAP (only while development is below era index EXPCAP_ERA, if set)
SPREAD_FIX = True    # while an Endeavour runs, the spread keeps only its own share (20%, or 50% before SO05). False reproduces the fault in
                     # every measurement before 14 Oct 2026: the spread took the whole income on top of the Endeavour's share, 180% in all
TRACE = None   # a list to receive one read-only record per turn (turn-by-turn traces); None = off
CLOCK = {'turn': 0}   # the current turn, for measurements that depend on time rather than discoveries
OBS = True; GLIMPSE = 0.0   # OBS: observational revelation from rivals; GLIMPSE: chance a turn that an eligible idea which fails to occur is glimpsed (Revealed) instead (section 1.2's proximity revelation, provisional form)   # DIFF: dict(rivals=[{row: turn}], contact_era=era index) -- knowledge diffusion from replayed rivals (section 1.2)   # END_AFTER: a row that must be discovered before any Endeavour starts   # END_FROM: era index; Endeavours may start once the civilisation has discovered a row of that era
def _ftl_active(waiting, pool, have):
    global FUNDED
    target = TARGET_FN(have) if TARGET_FN else set()
    FUNDED = target
    fw = {f: w for f, w in waiting.items() if any(k in target for k in pool.get(f, []))}
    if fw: return max(fw, key=fw.get)
    return max(waiting, key=waiting.get) if waiting else None

def run(prm, seed, max_turns=450):
    rng = random.Random(seed); m = prm.model
    have = {}; cum = 0.0; turn = 0; bank = 0.0
    dependents = {}                                                       # row -> the rows that name it as a prerequisite
    for k in IDS:
        for grp in H0.ROWS[k]['pre']:
            for opt in grp:
                for p in opt: dependents.setdefault(p, []).append(k)
    met = {k for k in IDS if prereqs_met(k, have)}; new_rows = []         # rows whose prerequisites are met: only grows, as `have` does
    focus_ins = {}; progress = {}; need = {}; line = {}; opened = {}; d_open = {}; occurred = set(); elig_since = {}; occ_turn = {}
    acct = {'income': 0.0, 'lost_empty': 0.0, 'lost_cap': 0.0, 'banked_end': 0.0, 'premium_dilution': 0.0, 'attention': 0.0, 'saturation': 0.0, 'linear': 0.0}
    if m == 'T':
        pos, _, focus_thr, _ = GN.generate(ROWS, prm.spill, rng, slack=0.0)
        total_thr = {k: total_gate(pos[k], prm.slack) for k in ROWS}
        for k, sh in prm.accelerate.items():
            if prm.accel_T == 'gap': focus_thr[k] -= 0.5 * PRICE[ROWS[k]['era']] * G.LIK[ROWS[k]['tier']]
            else: focus_thr[k] *= 0.5
        focus_thr = {k: v * prm.scale for k, v in focus_thr.items()}
    diff_since = {}; diff_unc = {}; contact_turn = None; cp04_turn = None
    glimpsed = set(); lost = set(); grng = random.Random(seed * 7919 + 13)   # its own stream: glimpses never perturb the game
    STATE.clear(); STATE.update(lost=lost, glimpsed=glimpsed, diff=diff_since, diff_unc=diff_unc, occurred=occurred)   # what a player can infer, for the detective
    log = []; active = None; end_k = None; end_prog = 0.0; end_cost = 0.0; att_hist = {}
    while turn < max_turns and len(have) < len(IDS):
        turn += 1; inc = income(cum) * ECON; cum += inc; d = dev(cum); acct['income'] += inc   # ECON: the player's economy against the calibrated good player's
        CLOCK['turn'] = turn
        if d >= SPAN_E and not RUN_ON: break                           # past the end of the tree (RUN_ON: carry on at the last era's income)
        if STOP_FN and STOP_FN(have): break                            # the measurement has what it needs
        blocked = prm.blocked_focus if (prm.blocked_focus and d < prm.unblock_dev) else None
        att_turn = {}; end_done = None
        for p in new_rows:                                                 # recheck only the rows that depend on last turn's discoveries
            for k in dependents.get(p, ()):
                if k not in met and prereqs_met(k, have): met.add(k)
        new_rows = []
        disc = [k for k in IDS if k not in have and k in met and FOCUS[k] != blocked]
        diff_due = []; obs = set()
        if DIFF:                                   # knowledge diffusion (section 1.2): contacted rivals, Printing Press, Internet
            if contact_turn is None and any(ERA_I[k] >= DIFF['contact_era'] for k in have): contact_turn = turn
            if cp04_turn is None and 'CP04' in have: cp04_turn = turn
            if contact_turn is not None:
                riv = DIFF['rivals']; nr = len(riv)
                for k in disc:
                    tk = ROWS[k]['tier']
                    if tk == 'UNIQUE': continue
                    nh = sum(1 for r in riv if r.get(k, 10 ** 9) <= turn)
                    if nh == 0: continue
                    if OBS: obs.add(k)             # observational revelation: a contacted rival has it in effect
                    if nh / nr < 0.5: continue
                    if tk in ('CORE', 'STANDARD') and 'MC06' in have:
                        s0 = diff_since.setdefault(k, turn)
                        if turn - s0 >= 10 or (cp04_turn is not None and turn - max(s0, cp04_turn) >= 5): diff_due.append(k)
                    elif tk == 'UNCOMMON' and cp04_turn is not None:
                        s0 = diff_unc.setdefault(k, turn)
                        if turn - s0 >= 5: diff_due.append(k)
        for k in disc: opened.setdefault(k, turn); d_open.setdefault(k, d)
        def fresh(k):
            """fade: the share of attention an open question still draws (CORE never fades, nor W16's funded Space-era rows)"""
            if not prm.fade or ROWS[k]['tier'] not in prm.fade_tiers or (k in FUNDED and ROWS[k]['tier'] == 'STANDARD' and ROWS[k]['era'] == 'Space'): return 1.0
            past = {'era': d - (ERA_I[k] + 1), 'later': d - max(ERA_I[k] + 1, d_open[k])}.get(prm.fade_clock, d - d_open[k])
            return 0.5 ** (max(0.0, past) / prm.fade)
        if TRACE is not None: _occ0, _gl0, _fund0 = set(occurred), set(glimpsed), set(FUNDED)
        # the moment: a non-CORE idea occurs to the civilisation with a small chance each turn while it lasts
        if m != 'T':
            for k in disc:
                if k in occurred: continue
                t = ROWS[k]['tier']
                if t == 'CORE' or (k in FUNDED and t == 'STANDARD' and ROWS[k]['era'] == 'Space'): occurred.add(k); continue   # W16: a funded focus never loses an idea
                W = TURNS[ROWS[k]['era']] * prm.window[t] * prm.accel_occ.get(k, 1.0)
                behind = d - (ERA_I[k] + 1)
                if prm.compress and behind > 0: W = W / (1 + prm.compress * behind)
                W = max(W, 1.0)
                if not (prm.fade and t in prm.fade_tiers):                           # (a fading tier's moment never closes; attention fades instead)
                    if turn - opened[k] > W: lost.add(k); continue                     # the moment has passed: the idea is lost
                    if t != 'STANDARD' and d > ERA_I[k] + 1 + prm.grace: lost.add(k); continue
                if rng.random() < 1 - (1 - min(TARGET[t], 0.999)) ** (1 / W): occurred.add(k); occ_turn[k] = turn
                else:                                                                # proximity revelation: glimpsed, not found
                    g = GLIMPSE.get(t, 0.0) if isinstance(GLIMPSE, dict) else GLIMPSE   # a chance for every tier, or one per tier
                    if g and k not in glimpsed and grng.random() < g: glimpsed.add(k)
            if prm.fade:                                                         # fade: an open question that goes undiscovered can be glimpsed too
                for k in disc:
                    if k in occurred and k not in glimpsed and ROWS[k]['tier'] in prm.fade_tiers:
                        g = GLIMPSE.get(ROWS[k]['tier'], 0.0) if isinstance(GLIMPSE, dict) else GLIMPSE
                        if g and grng.random() < g: glimpsed.add(k)
            live = [k for k in disc if k in occurred]
        else:
            live = disc
        pool = {}
        for k in live: pool.setdefault(FOCUS[k], []).append(k)
        fresh_top = max((fresh(k) for k in live), default=1.0) or 1.0
        waiting = {f: sum(TARGET[ROWS[k]['tier']] * (1 + max(0.0, d - ERA_I[k])) * fresh(k) for k in ks) for f, ks in pool.items()}
        if prm.player == 'specialist' and 'Mathematics' in pool: active = 'Mathematics'
        else: active = _ftl_active(waiting, pool, have)
        def est_price(k): return PRICE[ROWS[k]['era']] * prm.scale * prm.premium ** max(0.0, ERA_I[k] - d)
        def est_rem(k): return max(COSTMULT.get(k, 1.0) - progress.get(k, 0.0), 0.2) * est_price(k)
        if POLICY == 'cheapest' and FUNDED:      # smarter detective: fund the focus whose cheapest targeted row would finish soonest
            pri = (PRIORITY & FUNDED) if PRIORITY else FUNDED   # higher-priority targets (the tests) take the active focus when any is workable
            capped = EXPCAP is not None and (EXPCAP_ERA is None or d < EXPCAP_ERA)
            ok_p = (lambda k: prm.premium ** max(0.0, ERA_I[k] - d) <= EXPCAP) if capped else (lambda k: True)
            pri = {k for k in pri if ok_p(k)}
            fc = {f: min(est_rem(k) for k in ks if k in pri) for f, ks in pool.items() if any(k in pri for k in ks)}
            if not fc: fc = {f: min(est_rem(k) for k in ks if k in FUNDED and ok_p(k)) for f, ks in pool.items() if any(k in FUNDED and ok_p(k) for k in ks)}
            if fc: active = min(fc, key=fc.get)
            elif capped and waiting: active = max(waiting, key=waiting.get)   # nothing affordable to target: fund the most fruitful focus, as development catches up
        sh = 0.8 if 'SO05' in have else 0.5
        if end_k is not None and (end_k in have or (END_RULE != 'request' and end_k not in FUNDED)): END_LOG.append((turn, end_k, 'dropped')); end_k = None
        if END_MULT and end_k is None and (END_FROM is None or any(ERA_I[k] >= END_FROM for k in have)) and (END_AFTER is None or END_AFTER in have):   # gate: first discovery of era END_FROM            # Grand Endeavour: commit to the targeted live row it saves most time on (at least a turn)
            if END_RULE == 'request' and END_REQUEST and END_REQUEST not in have and prereqs_met(END_REQUEST, have):
                end_k, end_cost, end_prog = END_REQUEST, END_MULT * COSTMULT.get(END_REQUEST, 1.0) * est_price(END_REQUEST), 0.0; END_LOG.append((turn, END_REQUEST, 'start'))
            best = None
            for k in ([] if END_RULE == 'request' else live) + [x for x in (obs | glimpsed) if END_RULE != 'request' and x not in occurred and x not in have and prereqs_met(x, have) and (x in lost or x in diff_since or x in diff_unc)]:
                if k not in FUNDED or k in have: continue
                if END_ONLY is not None and k not in END_ONLY: continue   # 'last' rule: only the last missing piece and its chain
                if k in occurred:
                    if len(att_hist.get(k, [])) < 2: continue
                    rate = sum(att_hist[k][-2:]) / 2; t_norm = est_rem(k) / rate if rate > 1e-9 else float('inf')
                    if END_RULE == 'active':      # the real alternative: make k's focus active, where k gets its automatic share of that focus
                        ks = [j for j in pool.get(FOCUS[k], []) if j not in have]
                        wj = {j: TARGET[ROWS[j]['tier']] * (progress.get(j, 0) + prm.momentum) * ATTN.get(j, 1.0) * fresh(j) for j in ks}
                        phi = wj[k] / sum(wj.values()) if k in wj and sum(wj.values()) > 0 else 1.0
                        t_norm = min(t_norm, est_rem(k) / max(inc * sh * phi, 1e-9))
                else:                             # Revealed by a rival, but the idea never occurred here: only diffusion or an Endeavour brings it
                    s0 = diff_since.get(k, diff_unc.get(k))
                    t_norm = max(0, (5 if cp04_turn is not None else 10) - (turn - s0)) if s0 is not None else float('inf')
                cost = END_MULT * COSTMULT.get(k, 1.0) * est_price(k); t_end = cost / max(inc * sh, 1e-9)
                if t_norm - t_end >= 1.0 and (best is None or t_norm - t_end > best[0]): best = (t_norm - t_end, k, cost)
            if best: end_k, end_cost, end_prog = best[1], best[2], 0.0; END_LOG.append((turn, end_k, 'start'))
        if end_k is not None:                     # the Endeavour is the focus: it takes the active share; the spread still rolls
            end_prog += inc * sh + bank; bank = 0.0; active = None
            if end_prog >= end_cost: end_done = end_k; END_LOG.append((turn, end_k, 'done')); end_k = None
        if TRACE is not None: _fund = ('END', end_done or end_k) if (end_done or end_k is not None) else ('FOCUS', active)
        open_foci = sorted(set(pool) | set(FOCUS[k] for k in have if FOCUS[k] != blocked))
        share = 0.8 if 'SO05' in have else 0.5
        flow = {}
        others = [f for f in open_foci if f != active and (prm.spread_floor > 0 or f in pool)]
        if active: flow[active] = inc * share + bank; bank = 0.0
        elif not (SPREAD_FIX and (end_k is not None or end_done)): share = 0.0   # (no active focus: the spread takes everything)
        wt = {f: waiting.get(f, 0) + prm.spread_floor for f in others}; tw = sum(wt.values()) or 1
        if end_k is not None or end_done: acct['endeavour_turns'] = acct.get('endeavour_turns', 0) + 1; acct['endeavour_extra'] = acct.get('endeavour_extra', 0.0) + inc * sh   # (accounting only)
        if not others: acct['spread_dropped'] = acct.get('spread_dropped', 0.0) + inc * (1 - share); acct['spread_dropped_turns'] = acct.get('spread_dropped_turns', 0) + 1   # (accounting only)
        for f in others: flow[f] = flow.get(f, 0) + inc * (1 - share) * wt[f] / tw
        found = []
        if end_done: found.append(end_done)
        for k in diff_due:
            if k not in found: found.append(k); DIFF_LOG.append((turn, k))
        def use(f, ins):
            """spend `ins` Insight in focus f; return what it could not use"""
            cands = [k for k in pool.get(f, []) if k not in have and k not in found]
            if m == 'T':
                usable = any(focus_ins.get(f, 0) < focus_thr[k] for k in cands)
                if prm.routing == 'spill' and not usable: return ins
                if prm.routing == 'bank' and not cands: return ins           # banks only once the focus has emptied
                focus_ins[f] = focus_ins.get(f, 0) + ins
                hits = []
                for k in cands:
                    if focus_ins[f] < focus_thr[k] or cum < total_thr[k]: continue
                    elig_since.setdefault(k, turn); t = ROWS[k]['tier']
                    if t == 'CORE': hits.append(k); continue
                    W = TURNS[ROWS[k]['era']]
                    if turn - elig_since[k] > W: continue
                    if rng.random() < 1 - (1 - TARGET[t]) ** (1 / W): hits.append(k)
                if hits: found.append(rng.choice(hits))
                return 0.0
            if not cands: return ins
            def price(k):
                return PRICE[ROWS[k]['era']] * prm.scale * prm.accel_price.get(k, 1.0) * prm.premium ** max(0.0, ERA_I[k] - d - prm.accelerate.get(k, 0.0))
            def prem(k): return prm.premium ** max(0.0, ERA_I[k] - d)
            if m == 'R':
                w = {k: TARGET[ROWS[k]['tier']] for k in cands}; tot = sum(w.values())
                left = 0.0
                for k in cands:
                    att = ins * w[k] / tot; pk = price(k); used = min(att, pk); left += att - used
                    acct['attention'] += used; acct['premium_dilution'] += used * (1 - 1 / prem(k))
                    acct['linear'] += used / pk; acct['saturation'] += (used / pk) - (1 - math.exp(-used / pk))
                    if rng.random() < (min(1.0, used / pk) if prm.linear else 1 - math.exp(-used / pk)): found.append(k)
                acct['lost_cap_pending'] = acct.get('lost_cap_pending', 0) + left
                return left
            # the P forms: meters in units of each breakthrough's price
            for k in cands:
                if k not in need:
                    need[k] = rng.gammavariate(prm.shape, 1 / prm.shape) * COSTMULT.get(k, 1.0)
                    if k in prm.accel_head: progress[k] = need[k] * prm.accel_head[k]
            held = 0.0
            if prm.fade and not (f == active and not prm.fade_funded):
                eng = max(fresh(k) for k in cands) / fresh_top             # the rest spills to fields with fresher questions
                held = ins * (1 - eng)
            left = ins - held
            for _ in range(len(cands) + 1):
                cands = [k for k in cands if k not in found]
                if not cands or left <= 1e-9: break
                if m == 'Pone':
                    if line.get(f) not in cands:
                        ws = [TARGET[ROWS[k]['tier']] for k in cands]; line[f] = rng.choices(cands, ws)[0]
                    k = line[f]; pk = price(k); room = (need[k] - progress.get(k, 0)) * pk
                    if left >= room: progress[k] = need[k]; found.append(k); left -= room; line[f] = None; acct['attention'] += room; acct['premium_dilution'] += room * (1 - 1 / prem(k))
                    else: progress[k] = progress.get(k, 0) + left / pk; acct['attention'] += left; acct['premium_dilution'] += left * (1 - 1 / prem(k)); left = 0.0
                else:
                    ws = {k: TARGET[ROWS[k]['tier']] * (progress.get(k, 0) + prm.momentum) * ATTN.get(k, 1.0) * fresh(k) for k in cands}; tot = sum(ws.values())
                    spent = 0.0; done = []
                    for k in cands:
                        att = left * ws[k] / tot; pk = price(k); room = (need[k] - progress.get(k, 0)) * pk; att_turn[k] = att_turn.get(k, 0.0) + att
                        if att >= room: progress[k] = need[k]; done.append(k); spent += room; acct['attention'] += room; acct['premium_dilution'] += room * (1 - 1 / prem(k))
                        else: progress[k] = progress.get(k, 0) + att / pk; spent += att; acct['attention'] += att; acct['premium_dilution'] += att * (1 - 1 / prem(k))
                    found.extend(done); left -= spent
                    if not done: left = 0.0; break
            return left + held
        unused = {}
        for f, ins in flow.items():
            had = [k for k in pool.get(f, []) if k not in have and k not in found]
            u = use(f, ins); unused[f] = u
            if u > 1e-9: acct['lost_empty' if not had else 'lost_cap'] += u
        spare = sum(unused.values())
        if prm.routing in ('spill', 'spillbank') and spare > 1e-9:
            remaining = {f: [k for k in pool.get(f, []) if k not in have and k not in found] for f in pool}
            takers = {f: waiting.get(f, 0) + 0.1 for f in pool if remaining[f] and unused.get(f, 0) <= 1e-9}
            tw = sum(takers.values())
            if tw > 0:
                back = 0.0
                for f, w in takers.items(): back += use(f, spare * w / tw)
                recovered = spare - back
                if prm.routing == 'spillbank': bank += back; acct['recovered'] = acct.get('recovered', 0) + back
                scale_down = recovered / spare if spare else 0
                acct['lost_empty'] *= 1; acct['recovered'] = acct.get('recovered', 0) + recovered
        elif prm.routing == 'bank':
            emptied = [f for f, u in unused.items() if u > 1e-9 and not [k for k in pool.get(f, []) if k not in have and k not in found]]
            bank += sum(unused[f] for f in emptied); acct['recovered'] = acct.get('recovered', 0) + sum(unused[f] for f in emptied)
        for k in found: have[k] = (turn, d); new_rows.append(k)
        if m != 'T':
            for k in live: att_hist[k] = (att_hist.get(k, []) + [att_turn.get(k, 0.0)])[-3:]
        log.append((turn, d, len(found)))
        if TRACE is not None:
            _new = sorted(occurred - _occ0)
            TRACE.append(dict(turn=turn, d=d, found=list(found), diff=[k for k in found if k in diff_due], endv=[end_done] if end_done else [],
                              occ=[(k, 'core' if ROWS[k]['tier'] == 'CORE' else ('funded' if (k in _fund0 and ROWS[k]['tier'] == 'STANDARD' and ROWS[k]['era'] == 'Space') else 'chance')) for k in _new],
                              glim=sorted(glimpsed - _gl0), fund=_fund))
    acct['banked_end'] = bank; run.acct = acct; run.opened = opened; run.occ = occ_turn
    return have, log

def lateness(prm, n=6, seed0=100):
    offs = [have[k][1] - ERA_I[k] for s in range(n) for have, _ in [run(prm, seed0 + s)] for k in have]
    return st.median(offs) if offs else 9

def calibrate(prm, target=0.5, n=6):
    lo, hi = 0.01, 3.0
    for _ in range(10):
        mid = math.sqrt(lo * hi); prm.scale = mid
        if lateness(prm, n) > target: hi = mid
        else: lo = mid
    prm.scale = math.sqrt(lo * hi); return prm.scale

def summarise(prm, n=16, seed0=500):
    runs = [run(prm, seed0 + s) for s in range(n)]
    out = {}
    per = {e: [] for e in EO}; clumps = {e: [] for e in EO}; drought = {e: [] for e in EO}
    for have, log in runs:
        by = {e: [] for e in EO}
        for turn, d, c in log: by[EO[min(int(d), len(EO) - 1)]].append(c)
        for e in EO:
            if by[e]:
                per[e].append(st.mean(by[e])); clumps[e].append(sum(c >= 3 for c in by[e]) / len(by[e]))
                best = cur = 0
                for c in by[e]: cur = cur + 1 if c == 0 else 0; best = max(best, cur)
                drought[e].append(best)
    out['cadence'] = {e: round(st.mean(v), 2) for e, v in per.items() if v}
    out['clump%'] = {e: round(100 * st.mean(v), 1) for e, v in clumps.items() if v}
    out['drought'] = {e: round(st.mean(v), 1) for e, v in drought.items() if v}
    offs = [have[k][1] - ERA_I[k] for have, _ in runs for k in have]
    out['outside own era %'] = round(100 * sum(not (0 <= o < 1) for o in offs) / len(offs), 1)
    out['≥1 era early %'] = round(100 * sum(o < -1 for o in offs) / len(offs), 2)
    out['earliest'] = round(min(offs), 2)
    out['tiers'] = {t: round(st.mean(sum(k in have for k in IDS if ROWS[k]['tier'] == t) / sum(ROWS[k]['tier'] == t for k in IDS) for have, _ in runs), 2) for t in TARGET}
    return out
