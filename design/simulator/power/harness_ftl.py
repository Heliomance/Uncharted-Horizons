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
import gen_data as G, generator as GN, eramodel as M, ledger as Lg
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
        self.__dict__.update(kw)

# Measurement copy of harness2: a research-target hook (TARGET_FN), W16's funded-focus rule (FUNDED), price multipliers (COSTMULT).
TARGET_FN = None; FUNDED = set(); COSTMULT = {}
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
    focus_ins = {}; progress = {}; need = {}; line = {}; opened = {}; occurred = set(); elig_since = {}; occ_turn = {}
    acct = {'income': 0.0, 'lost_empty': 0.0, 'lost_cap': 0.0, 'banked_end': 0.0, 'premium_dilution': 0.0, 'attention': 0.0, 'saturation': 0.0, 'linear': 0.0}
    if m == 'T':
        pos, _, focus_thr, _ = GN.generate(ROWS, prm.spill, rng, slack=0.0)
        total_thr = {k: total_gate(pos[k], prm.slack) for k in ROWS}
        for k, sh in prm.accelerate.items():
            if prm.accel_T == 'gap': focus_thr[k] -= 0.5 * PRICE[ROWS[k]['era']] * G.LIK[ROWS[k]['tier']]
            else: focus_thr[k] *= 0.5
        focus_thr = {k: v * prm.scale for k, v in focus_thr.items()}
    log = []; active = None
    while turn < max_turns and len(have) < len(IDS):
        turn += 1; inc = income(cum); cum += inc; d = dev(cum); acct['income'] += inc
        if d >= SPAN_E: break                                          # past the end of the tree
        blocked = prm.blocked_focus if (prm.blocked_focus and d < prm.unblock_dev) else None
        disc = [k for k in IDS if k not in have and FOCUS[k] != blocked and prereqs_met(k, have)]
        for k in disc: opened.setdefault(k, turn)
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
                if turn - opened[k] > W: continue
                if t != 'STANDARD' and d > ERA_I[k] + 1 + prm.grace: continue
                if rng.random() < 1 - (1 - min(TARGET[t], 0.999)) ** (1 / W): occurred.add(k); occ_turn[k] = turn
            live = [k for k in disc if k in occurred]
        else:
            live = disc
        pool = {}
        for k in live: pool.setdefault(FOCUS[k], []).append(k)
        waiting = {f: sum(TARGET[ROWS[k]['tier']] * (1 + max(0.0, d - ERA_I[k])) for k in ks) for f, ks in pool.items()}
        if prm.player == 'specialist' and 'Mathematics' in pool: active = 'Mathematics'
        else: active = _ftl_active(waiting, pool, have)
        open_foci = sorted(set(pool) | set(FOCUS[k] for k in have if FOCUS[k] != blocked))
        share = 0.8 if 'SO05' in have else 0.5
        flow = {}
        others = [f for f in open_foci if f != active and (prm.spread_floor > 0 or f in pool)]
        if active: flow[active] = inc * share + bank; bank = 0.0
        else: share = 0.0
        wt = {f: waiting.get(f, 0) + prm.spread_floor for f in others}; tw = sum(wt.values()) or 1
        for f in others: flow[f] = flow.get(f, 0) + inc * (1 - share) * wt[f] / tw
        found = []
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
            left = ins
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
                    ws = {k: TARGET[ROWS[k]['tier']] * (progress.get(k, 0) + prm.momentum) for k in cands}; tot = sum(ws.values())
                    spent = 0.0; done = []
                    for k in cands:
                        att = left * ws[k] / tot; pk = price(k); room = (need[k] - progress.get(k, 0)) * pk
                        if att >= room: progress[k] = need[k]; done.append(k); spent += room; acct['attention'] += room; acct['premium_dilution'] += room * (1 - 1 / prem(k))
                        else: progress[k] = progress.get(k, 0) + att / pk; spent += att; acct['attention'] += att; acct['premium_dilution'] += att * (1 - 1 / prem(k))
                    found.extend(done); left -= spent
                    if not done: left = 0.0; break
            return left
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
        for k in found: have[k] = (turn, d)
        log.append((turn, d, len(found)))
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
