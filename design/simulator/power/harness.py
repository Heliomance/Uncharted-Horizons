"""Discovery-model comparison harness.

Three rules for turning Insight into breakthroughs, run on one shared world:
  T  threshold — the agreed design: generator positions, a total-Insight gate with half an era of slack,
     running-total focus gates, one discovery per focus per turn, per-turn rolls whose moment passes.
  R  pure rate — a focus's Insight is shared as attention by weight; each breakthrough's chance per turn
     is its attention ÷ its price.
  P  parallel progress — attention fills a meter towards a requirement drawn when the breakthrough
     becomes discoverable.
In R and P a breakthrough's price is its era's price × a prematurity premium for each era it lies ahead
of the civilisation's development, and a rare breakthrough's weight fades once its era has passed.
"""
import sys, math, random, statistics as st, json
sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import gen_data as G, generator as GN, eramodel as M, ledger as Lg

EO = Lg.EO
ROWS = G.familiar
IDS = sorted(ROWS)
FOCUS = {k: ROWS[k]['focus'] for k in IDS}
PRICE = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/era_prices.json'))
TARGET = {'CORE': 1.0, 'STANDARD': 0.85, 'UNCOMMON': 0.4, 'RARE': 0.1, 'UNIQUE': 0.065}
DEP = {}
for k in IDS:
    for grp in ROWS[k]['pre']:
        for opt in grp:
            for p in opt: DEP.setdefault(p, set()).add(k)

# ---- the shared world: Insight per turn from the calibrated era model ------------------------------
TURNS = M.TURNS['fork']
START = {e: (Lg.ERA_END[EO[i - 1]] if i else 0) for i, e in enumerate(EO)}
RATE = {e: (Lg.ERA_END[e] - START[e]) / TURNS[e] for e in EO}          # Insight per turn within each era
def income(cum):
    for e in EO:
        if cum < Lg.ERA_END[e]: return RATE[e]
    return RATE[EO[-1]]
def dev(cum): return GN.era_coord(cum)                                  # development: era index + fraction
ERA_I = {k: EO.index(ROWS[k]['era']) for k in IDS}

def prereqs_met(k, have):
    return all(any(all(p in have for p in opt) for opt in grp) for grp in ROWS[k]['pre'])

# ---- routing and players ---------------------------------------------------------------------------
SO05 = 'SO05'
def route(cum_income, have, open_foci, active, waiting=None):
    """Insight per focus this turn: the active focus takes 80% (50% before SO05); the rest is spread over the
    other open foci in proportion to what each has waiting (a stand-in for the environment-weighted spread)."""
    share = 0.8 if SO05 in have else 0.5
    out = {}
    others = [f for f in open_foci if f != active]
    if active in open_foci: out[active] = cum_income * share
    else: share = 0
    wt = {f: (waiting or {}).get(f, 0) + 0.1 for f in others}; tot = sum(wt.values()) or 1
    for f in others: out[f] = cum_income * (1 - share) * wt[f] / tot
    return out

# ---- the models ------------------------------------------------------------------------------------
class Params:
    def __init__(self, **kw):
        self.spill = 0.30; self.slack = 0.5; self.premium = 4.0; self.shape = 4.0
        self.fade = {'CORE': None, 'STANDARD': 2.0, 'UNCOMMON': 0.5, 'RARE': 0.5, 'UNIQUE': 0.5}  # eras of fade after the era ends
        self.weight = dict(TARGET)
        self.accelerate = {}          # {row: era-shift} — T: applied to the focus threshold; R/P: price × premium^-shift
        self.scale = 1.0                # pace calibration: R/P prices, T focus thresholds
        self.accel_T = 'whole'        # how T applies it: 'whole' threshold or own 'gap'
        self.blocked_focus = None; self.unblock_dev = None   # the landlocked scenario
        self.__dict__.update(kw)

def run(model, player, prm, seed, turns=400):
    rng = random.Random(seed)
    have = {}; cum = 0.0; turn = 0
    focus_ins = {}; progress = {}; need = {}; eligible_since = {}
    if model == 'T':
        pos, total_thr, focus_thr, _ = GN.generate(ROWS, prm.spill, rng, slack=prm.slack)
        for k, shift in prm.accelerate.items():                   # accelerators in T: along the focus's own curve
            if prm.accel_T == 'gap': focus_thr[k] -= 0.5 * PRICE[ROWS[k]['era']] * G.LIK[ROWS[k]['tier']]
            else: focus_thr[k] *= 0.5
        focus_thr = {k: v * prm.scale for k, v in focus_thr.items()}
    active = None; log = []
    while turn < turns and len(have) < len(IDS):
        turn += 1; inc = income(cum); cum += inc; d = dev(cum)
        blocked = prm.blocked_focus if (prm.blocked_focus and d < prm.unblock_dev) else None
        disc = [k for k in IDS if k not in have and FOCUS[k] != blocked and prereqs_met(k, have)]
        open_foci = sorted(set(FOCUS[k] for k in disc) | set(FOCUS[k] for k in have if FOCUS[k] != blocked))
        pool = {}
        for k in disc: pool.setdefault(FOCUS[k], []).append(k)
        waiting = {f: sum(prm.weight[ROWS[k]['tier']] * (1 + max(0.0, d - ERA_I[k])) for k in ks) for f, ks in pool.items()}
        if player == 'specialist' and 'Mathematics' in pool: active = 'Mathematics'
        else: active = max(waiting, key=waiting.get) if waiting else None
        flow = route(inc, have, open_foci, active, waiting)
        found = []
        for f, ins in flow.items():
            focus_ins[f] = focus_ins.get(f, 0) + ins
            cands = pool.get(f, [])
            if not cands: continue
            if model == 'T':
                hits = []
                for k in cands:
                    if focus_ins[f] < focus_thr[k] or cum < total_thr[k]: continue
                    eligible_since.setdefault(k, turn)
                    t = ROWS[k]['tier']
                    if t == 'CORE': hits.append(k); continue
                    window = TURNS[ROWS[k]['era']]
                    if turn - eligible_since[k] > window: continue          # the moment has passed
                    p = 1 - (1 - TARGET[t]) ** (1 / window)
                    if rng.random() < p: hits.append(k)
                if hits: found.append(rng.choice(hits))                     # one discovery per focus per turn
                continue
            ws = {}
            for k in cands:
                t = ROWS[k]['tier']; w = prm.weight[t]
                behind = d - (ERA_I[k] + 1)
                if prm.fade[t] is not None and behind > 0: w *= math.exp(-behind / prm.fade[t])
                ws[k] = w
            tot = sum(ws.values())
            if tot <= 0: continue
            for k in cands:
                att = ins * ws[k] / tot
                ahead = ERA_I[k] - d
                price = PRICE[ROWS[k]['era']] * prm.scale * (prm.premium ** max(0.0, ahead))
                price *= prm.premium ** -prm.accelerate.get(k, 0.0)
                if model == 'R':
                    if rng.random() < 1 - math.exp(-att / price): found.append(k)
                else:
                    if k not in need: need[k] = rng.gammavariate(prm.shape, 1 / prm.shape)
                    progress[k] = progress.get(k, 0) + att / price
                    if progress[k] >= need[k]: found.append(k)
        for k in found: have[k] = (turn, d)
        log.append((turn, d, len(found)))
    return have, log

# ---- measurements ----------------------------------------------------------------------------------
def summarise(model, player, prm, n=30, seed0=0):
    runs = [run(model, player, prm, seed0 + s) for s in range(n)]
    out = {}
    # cadence, clumps and droughts, by era of development
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
    out['longest drought'] = {e: round(st.mean(v), 1) for e, v in drought.items() if v}
    # era of arrival against the label
    offs = [have[k][1] - ERA_I[k] for have, _ in runs for k in have]          # 0..1 = within its own era
    out['outside own era %'] = round(100 * sum(not (0 <= o < 1) for o in offs) / len(offs), 1)
    out['early by ≥1 era %'] = round(100 * sum(o < -1 for o in offs) / len(offs), 2)
    out['earliest (eras)'] = round(min(offs), 2)
    # lifetime rates by tier
    rate = {}
    for t in TARGET:
        ks = [k for k in IDS if ROWS[k]['tier'] == t]
        rate[t] = round(st.mean(sum(k in have for k in ks) / len(ks) for have, _ in runs), 2)
    out['tier rates'] = rate
    out['turns to finish Space'] = round(st.mean(next((turn for turn, d, c in log if d >= len(EO)), 400) for _, log in runs))
    return out, runs


def lateness(model, player, prm, n=8, seed0=100):
    offs = [have[k][1] - ERA_I[k] for s in range(n) for have, _ in [run(model, player, prm, seed0 + s)] for k in have]
    return st.median(offs)

def calibrate_pace(model, prm, target=0.5, n=8):
    """scale prices (or focus thresholds) so the median arrival sits mid-era"""
    lo, hi = 0.02, 2.0
    for _ in range(12):
        mid = math.sqrt(lo * hi); prm.scale = mid
        if lateness(model, 'balanced', prm, n) > target: hi = mid
        else: lo = mid
    prm.scale = math.sqrt(lo * hi); return prm.scale

def calibrate_tiers(model, prm, rounds=5, n=8):
    """adjust each tier's weight until lifetime rates meet the targets (rate models only)"""
    for _ in range(rounds):
        out, _ = summarise(model, 'balanced', prm, n=n, seed0=200)
        for t, r in out['tier rates'].items():
            if t == 'CORE': continue
            prm.weight[t] *= max(0.2, min(5.0, (TARGET[t] / max(r, 0.01)) ** 1.5))
    return prm.weight
