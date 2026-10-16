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
        self.era_hold = None         # 'start': a window cannot close before its row's era has begun (an overdue one closes when it does);
                                     # 'clock': its clock starts no earlier than the era's start, so it gets a whole window from then
        self.era_hold_tiers = ('STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE')   # the tiers era_hold covers
        self.funded_windows = False  # True: a STANDARD idea's window does not close while its focus is the funded (active) focus; a window
                                     # already closed is not reopened (Tamsin's alternative to W16, 14 Oct 2026)
        self.rediscover = 0.0        # >0: a lost idea of a tier in rediscover_tiers gets a new chance each turn, `rediscover` for every undiscovered
                                     # breakthrough ready but for it (all its other prerequisites discovered): rediscovery on demand (14 Oct 2026)
        self.rediscover_tiers = ('STANDARD',)
        self.space_open = False      # True: a Space-era idea's window never closes, so it is never lost (the Space era as the endgame:
                                     # Tamsin, 16 Oct 2026)
        self.space_chance = {}       # {tier: chance a turn} for Space-era ideas when space_open, set directly instead of from the
                                     # window's length; a tier left out keeps its window-derived chance
        self.tier_attention = True   # True: tier odds also weight attention once an idea has occurred (within its focus, and its focus's pull
                                     # on the spread and spill-over). False: once occurred, every tier is studied alike (Tamsin, 14 Oct 2026)
        self.__dict__.update(kw)

# W7f copy with three switches: POLICY (focus choice), ATTN (attention weights), END_MULT (Grand Endeavours). Measurement copy of harness2: a research-target hook (TARGET_FN), W16's funded-focus rule (FUNDED), price multipliers (COSTMULT).
TARGET_FN = None; FUNDED = set(); COSTMULT = {}
COMPETE = {}   # Competing Solutions (section 1.2; competing.py): {alternative: primary}. A civilisation that discovers the primary first
               # locks the alternative out for good: it never occurs, is never studied, diffuses or comes back. An Endeavour already
               # running on it carries on (Grand Endeavours suspend lock-out). Empty (COMPETE=0): no lock-out, as before v3.124
POLICY = 'waiting'; ATTN = {}; END_MULT = None; END_LOG = []; END_RULE = 'naive'; END_ONLY = None; END_AFTER = None; END_FROM = None; RUN_ON = False; STOP_FN = None
DIFF = None; DIFF_LOG = []
DIFF_WAIT = 10; DIFF_WAIT_NET = 5; DIFF_SHARE = 0.5   # section 1.2: turns after the Printing Press, after the Internet; the share of contacts that must hold it
ECON = 1.0   # income relative to the calibrated (good player's) economy
STATE = {}   # live references to lost, glimpsed and diffusing ideas
INSIGHT_CUT = 0.0    # >0: from the first discovery of era INSIGHT_CUT_FROM, this share of every turn's Insight is lost before it is
INSIGHT_CUT_FROM = 'Atomic'   # allocated (development still counts it): Tamsin's question, 15 Oct 2026, what losing Insight costs late on
INSIGHT_CUT_DEV = False       # True: the lost share does not count towards development either (the era clock slows)
INCOME_FULL = False  # True: income follows all the Insight ever produced, not development, so Insight withheld from development (above,
                     # or END_ALL_NODEV) slows only the era clock's prices, as in the real game, where income comes from cities
END_REQUEST = None   # a row the player asks to pursue as an Endeavour (END_RULE 'request')
PRIORITY = set()   # targets that take the active focus first (the tests, during the investigation)
EXPCAP = None; EXPCAP_ERA = None   # premium cap: never make a target the active focus while its premium exceeds EXPCAP (only while development is below era index EXPCAP_ERA, if set)
W16 = True           # W16: a Space-era STANDARD idea the player is pursuing (in FUNDED) occurs at once; False switches the rule off
FTL_OCC = False      # FTLOCC: an FTL-related idea (FTL_ROWS: every breakthrough the FTL screen names) occurs as soon as its prerequisites are
FTL_ROWS = frozenset()  # met while its focus is the funded focus, in the turn it is funded; a lost one comes back the same way (Tamsin's question,
FTL_OCC_FROM = None  # 16 Oct 2026). FTL_OCC_FROM: a row that must be held first (e.g. RC01, the FTL screen), or None
VISIBLE = False      # VISIBLE: the simulated players decide what to fund only on what the screens show (Tamsin, 16 Oct 2026: where a
                     # breakthrough isn't revealed, a player cannot know whether its idea has occurred). Revealed ideas under study count as
                     # work; a discoverable idea the player cannot see counts as possibly under study, one it can see is not under study (or
                     # whose moment it can see has passed) does not; costs are full prices, with no hidden progress. Off: the players see
                     # every idea's occurrence and progress, as in every measurement before 16 Oct 2026
PROTO_UNTIL = None   # TOVICTORY (w7f.py): the game plays on past the race's finish to the launch; until this turn the prototype takes the
                     # funded share (no focus is funded, no Endeavour starts) and the spread goes on, as during an Endeavour
END_UNOCCURRED_ONLY = False   # True: a Grand Endeavour may target only an idea that has not occurred (a revealed goal nobody knows how to reach yet),
                              # never one already under study. The design allows both since v3.121 (for needs the game situation creates);
                              # the simulated players keep to this (ENDUNOCC=1), since with nothing pressing they would only reorder research
END_CREDIT = None    # an Endeavour on an idea under study: None, it starts from nothing (2x the price); 'before', the study already done
                     # comes off the price before the 2x premium, which then multiplies only the remaining work (Tamsin's question,
                     # 15 Oct 2026); 'after', it comes off the 2x price; 'meter', 2x the price x the share of the idea's hidden meter still to
                     # fill (Tamsin, the same day); 'true', the Insight its hidden meter still needs (unoccurred: the price). With any of them,
                     # the idea leaves ordinary study while the Endeavour runs
END_CREDIT_FLOOR = 0.0   # with END_CREDIT 'before': the remaining work counts as at least this share of the price (0.5: never less than half)
END_SHARE = None     # the share of each turn's Insight an Endeavour receives: None, the active share (80%; 50% before SO05), the spread keeping
                     # the rest; 1.0, all of it, the spread pausing too (Tamsin's urgent button, 15 Oct 2026)
END_SPREAD = None    # the spread's share of the turn while an Endeavour runs: None, whatever the Endeavour leaves; 0.2 with END_SHARE 0.7, the
                     # rest (10%) lost (Tamsin's model, 15 Oct 2026: 70% to the breakthrough, 20% to the spread, 10% lost, no premium)
END_LOST_NODEV = False   # True: the share of the turn an Endeavour loses (with END_SPREAD) does not count towards development either
END_ALL_NODEV = False    # True: nor does the share it receives: an Endeavour's Insight builds its breakthrough, not the civilisation's development
END_COOLDOWN = 0     # turns after an Endeavour ends (completed, repaid or dropped) before another may start (Tamsin's urgent button)
URGENT = False       # True: an Endeavour on an idea under study is urgent. It takes every Insight (the spread waits too) and fills the idea's
                     # meter with no premium; when it is done, no focus is funded for URGENT_DEBT x the turns it saved against funding the
                     # idea's focus when committed (played forward at expected meters) (Tamsin's aim, 15 Oct 2026: always faster for the target,
                     # always slower overall).
                     # Endeavours on ideas that have not occurred are unchanged
URGENT_DEBT = 1.25
END_ABANDON = 0.0    # with URGENT: when an urgent Endeavour starts, every other idea under study in its focus loses this share of its progress
                     # (the field drops everything for the one breakthrough; Tamsin's ideal, 15 Oct 2026)
END_ABANDON_ALL = False   # True: every idea under study, in every focus, loses END_ABANDON of its progress (the whole nation drops everything)
END_NOW = False      # True: a crash programme. The Endeavour delivers its breakthrough the turn it starts; its price is then repaid from the
                     # same share of the turns that follow, nothing else funded until it is paid (Tamsin's urgent button, 15 Oct 2026)
GOALS_FN = None      # rediscovery: a function of `have` returning goals that also wait on ideas (each a list of prerequisite groups,
                     # one row of each needed), e.g. the FTL prototypes of the hypotheses still standing
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


def _ftl_active_visible(vwaiting, cand, have, prev):
    """VISIBLE: the focus with targets the player can work on (cand: discoverable rows not seen to be idle), most visible work
    first, then most such targets; else the focus with the most visible work; else the focus funded last turn"""
    global FUNDED
    target = TARGET_FN(have) if TARGET_FN else set()
    FUNDED = target
    fw = {f: (vwaiting.get(f, 0.0), sum(k in target for k in ks)) for f, ks in cand.items() if any(k in target for k in ks)}
    if fw: return max(fw, key=fw.get)
    if vwaiting: return max(vwaiting, key=vwaiting.get)
    return prev

SPACE_I = EO.index('Space')   # development at which the Space era begins (era i spans development i to i + 1)
SPACE_FROM = None    # the cumulative Insight at which development enters the Space era: None, the Atomic span's end (143,768; section 2).
                     # Lower, development crosses the Atomic era faster and the Space era more slowly, both eras' outer ends unchanged;
                     # income (the simulator's stand-in economy) and every price stay as they are (Tamsin, 15 Oct 2026: the development
                     # thresholds look wrong if the game ends before the Space era begins)
DEV_ENDS = None      # {era: cumulative Insight at which development leaves it}: development's own era boundaries where they differ from
                     # the spans income follows (a redraw of section 2 that leaves the simulated economy alone); None, the spans themselves
WIN_TURNS = None     # {era: turns}: the era lengths that size idea windows (section 1.2), where they differ from the era model's
def dev_at(cum):
    if DEV_ENDS:
        ends = [DEV_ENDS.get(e, Lg.ERA_END[e]) for e in EO]; lo = 0.0
        for i, hi in enumerate(ends):
            if cum <= hi: return i + (cum - lo) / (hi - lo)
            lo = hi
        return len(EO) - 1 + (cum - ends[-2]) / (ends[-1] - ends[-2])
    if SPACE_FROM is None: return dev(cum)
    a0, s1 = Lg.ERA_END['Modern'], Lg.ERA_END['Space']
    if a0 <= cum < SPACE_FROM: return SPACE_I - 1 + (cum - a0) / (SPACE_FROM - a0)
    if SPACE_FROM <= cum <= s1: return SPACE_I + (cum - SPACE_FROM) / (s1 - SPACE_FROM)
    return dev(cum)

def run(prm, seed, max_turns=450):
    rng = random.Random(seed); m = prm.model
    have = {}; cum = 0.0; turn = 0; bank = 0.0
    dependents = {}                                                       # row -> the rows that name it as a prerequisite
    for k in IDS:
        for grp in H0.ROWS[k]['pre']:
            for opt in grp:
                for p in opt: dependents.setdefault(p, []).append(k)
    met = {k for k in IDS if prereqs_met(k, have)}; new_rows = []         # rows whose prerequisites are met: only grows, as `have` does
    alts_of = {}                                                          # Competing Solutions: primary -> its alternatives
    for a_, p_ in COMPETE.items(): alts_of.setdefault(p_, []).append(a_)
    locked = set()                                                        # alternatives locked out: their primary came first
    focus_ins = {}; progress = {}; need = {}; line = {}; opened = {}; occurred = set(); elig_since = {}; occ_turn = {}
    acct = {'income': 0.0, 'lost_empty': 0.0, 'lost_cap': 0.0, 'banked_end': 0.0, 'premium_dilution': 0.0, 'attention': 0.0, 'saturation': 0.0, 'linear': 0.0,
            'att_era': {}, 'prem_era': {}}   # by the era of the row studied: Insight spent on study, and the premium's share of it (accounting only)
    if m == 'T':
        pos, _, focus_thr, _ = GN.generate(ROWS, prm.spill, rng, slack=0.0)
        total_thr = {k: total_gate(pos[k], prm.slack) for k in ROWS}
        for k, sh in prm.accelerate.items():
            if prm.accel_T == 'gap': focus_thr[k] -= 0.5 * PRICE[ROWS[k]['era']] * G.LIK[ROWS[k]['tier']]
            else: focus_thr[k] *= 0.5
        focus_thr = {k: v * prm.scale for k, v in focus_thr.items()}
    diff_since = {}; diff_unc = {}; contact_turn = None; cp04_turn = None
    glimpsed = set(); lost = set(); grng = random.Random(seed * 7919 + 13)   # its own stream: glimpses never perturb the game
    rrng = random.Random(seed * 104729 + 7); rediscovered = {}                  # rediscovery's own stream, and when each lost idea came back
    held = set()                                                               # (accounting only) ideas the funded focus kept open past their window
    era_start = []                                                             # era_start[i]: the turn development reached era i
    lost_at = {}                                                               # (accounting only) when each idea was lost: turn, its window, whether it was a target
    STATE.clear(); STATE.update(lost=lost, glimpsed=glimpsed, diff=diff_since, diff_unc=diff_unc, occurred=occurred, locked=locked, end_k=None)   # what a player can infer, for the detective
    log = []; active = None; end_k = None; end_prog = 0.0; end_cost = 0.0; att_hist = {}; debt = 0.0; cool_until = 0   # debt: a crash programme's price still to repay; cool_until: END_COOLDOWN
    pause_until = 0; end_urgent = False; end_tstudy = 0.0; end_t0 = 0   # URGENT: the debt's last turn; the running Endeavour's estimate and start
    cum_all = 0.0                                                          # all the Insight ever produced (INCOME_FULL)
    while turn < max_turns and len(have) < len(IDS):
        turn += 1; inc = income(cum_all if INCOME_FULL else cum) * ECON
        cut = inc * INSIGHT_CUT if INSIGHT_CUT and any(ERA_I[k] >= EO.index(INSIGHT_CUT_FROM) for k in have) else 0.0   # lost before it is allocated
        cum_all += inc; cum += inc - (cut if INSIGHT_CUT_DEV else 0.0); d = dev_at(cum); acct['income'] += inc; inc -= cut   # ECON: the player's economy against the calibrated good player's
        CLOCK['turn'] = turn
        if d >= SPACE_I and 'space_entry_turn' not in acct: acct['space_entry_turn'] = turn   # (accounting only) development reaches the Space era
        while len(era_start) < len(EO) and d >= len(era_start): era_start.append(turn)       # the turn development reached each era
        if d >= SPAN_E and not RUN_ON: break                           # past the end of the tree (RUN_ON: carry on at the last era's income)
        if STOP_FN and STOP_FN(have): break                            # the measurement has what it needs
        blocked = prm.blocked_focus if (prm.blocked_focus and d < prm.unblock_dev) else None
        att_turn = {}; end_done = None
        for p in new_rows:                                                 # recheck only the rows that depend on last turn's discoveries
            for k in dependents.get(p, ()):
                if k not in met and prereqs_met(k, have): met.add(k)
        new_rows = []
        disc = [k for k in IDS if k not in have and k in met and FOCUS[k] != blocked and (k not in locked or k == end_k)]   # a locked-out alternative only by Endeavour
        diff_due = []; obs = set()
        if TRACE is not None: _seen0 = set(diff_since) | set(diff_unc)   # before this turn's diffusion, so the log's seen lists the rows first seen this turn
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
                    if nh / nr < DIFF_SHARE: continue
                    if tk in ('CORE', 'STANDARD') and 'MC06' in have:
                        s0 = diff_since.setdefault(k, turn)
                        if turn - s0 >= DIFF_WAIT or (cp04_turn is not None and turn - max(s0, cp04_turn) >= DIFF_WAIT_NET): diff_due.append(k)
                    elif tk == 'UNCOMMON' and cp04_turn is not None:
                        s0 = diff_unc.setdefault(k, turn)
                        if turn - s0 >= DIFF_WAIT_NET: diff_due.append(k)
        for k in disc: opened.setdefault(k, turn)
        if TRACE is not None: _occ0, _gl0, _fund0, _lost0, _lk0 = set(occurred), set(glimpsed), set(FUNDED), set(lost), set(locked)
        # the moment: a non-CORE idea occurs to the civilisation with a small chance each turn while it lasts
        funded = active                                                    # the focus funded last turn (None while an Endeavour ran)
        if m != 'T':
            for k in disc:
                if k in occurred: continue
                t = ROWS[k]['tier']
                if t == 'CORE' or (W16 and k in FUNDED and t == 'STANDARD' and ROWS[k]['era'] == 'Space'): occurred.add(k); continue   # W16: a funded focus never loses an idea
                if k in lost: continue                                                 # its window closed on an earlier turn: it stays closed
                W = (WIN_TURNS.get(ROWS[k]['era'], TURNS[ROWS[k]['era']]) if WIN_TURNS else TURNS[ROWS[k]['era']]) * prm.window[t] * prm.accel_occ.get(k, 1.0)
                behind = d - (ERA_I[k] + 1)
                if prm.compress and behind > 0: W = W / (1 + prm.compress * behind)
                W = max(W, 1.0)
                endgame = prm.space_open and ROWS[k]['era'] == 'Space'               # the endgame: a Space-era window never closes
                if not endgame:
                    t0 = opened[k]                                                   # when the window's clock started
                    if prm.era_hold and t in prm.era_hold_tiers:                     # era hold: no window closes before its row's era has begun
                        if ERA_I[k] >= len(era_start): t0 = turn                     # the era has not begun: the clock has not run out
                        elif prm.era_hold == 'clock': t0 = max(t0, era_start[ERA_I[k]])
                    if prm.funded_windows and t == 'STANDARD' and turn - t0 > W and FOCUS[k] == funded: held.add(k)   # (accounting only)
                    if turn - t0 > W and not (prm.funded_windows and t == 'STANDARD' and FOCUS[k] == funded):
                        lost.add(k); lost_at.setdefault(k, (turn, round(W, 1), k in FUNDED)); continue   # the moment has passed: the idea is lost
                    if t != 'STANDARD' and d > ERA_I[k] + 1 + prm.grace: lost.add(k); lost_at.setdefault(k, (turn, round(W, 1), k in FUNDED)); continue
                chance = prm.space_chance[t] if endgame and t in prm.space_chance else 1 - (1 - min(TARGET[t], 0.999)) ** (1 / W)
                if rng.random() < chance: occurred.add(k); occ_turn[k] = turn
                else:                                                                # proximity revelation: glimpsed, not found
                    g = GLIMPSE.get(t, 0.0) if isinstance(GLIMPSE, dict) else GLIMPSE   # a chance for every tier, or one per tier
                    if g and k not in glimpsed and grng.random() < g: glimpsed.add(k)
            if prm.rediscover:                                                   # rediscovery on demand: a lost idea that other work is waiting on comes back
                goals = GOALS_FN(have) if GOALS_FN else []
                for k in disc:
                    if k not in lost or k in occurred or ROWS[k]['tier'] not in prm.rediscover_tiers: continue
                    n = sum(1 for j in dependents.get(k, ()) if j not in have and j not in met and
                            all(any(all(p in have or p == k for p in opt) for opt in grp) for grp in H0.ROWS[j]['pre']))   # ready but for k
                    n += sum(1 for gs in goals if not all(any(o in have for o in g) for g in gs) and all(any(o in have for o in g) or k in g for g in gs))   # a goal ready but for k
                    if n and rrng.random() < 1 - (1 - prm.rediscover) ** n: occurred.add(k); occ_turn[k] = turn; lost.discard(k); rediscovered[k] = turn
            live = [k for k in disc if k in occurred]
        else:
            live = disc
        pool = {}
        for k in live:
            if not ((END_CREDIT or URGENT) and k == end_k): pool.setdefault(FOCUS[k], []).append(k)   # (the Endeavour has taken it over)
        waiting = {f: sum(TARGET[ROWS[k]['tier']] * (1 + max(0.0, d - ERA_I[k])) for k in ks) for f, ks in pool.items()}   # the simulated player's sense of where work waits
        def aw(k): return TARGET[ROWS[k]['tier']] if prm.tier_attention else 1.0   # attention weight of an idea under study
        pull = waiting if prm.tier_attention else {f: sum((1 + max(0.0, d - ERA_I[k])) for k in ks) for f, ks in pool.items()}   # the rule: each focus's draw on the spread
        ready_ftl = [k for k in disc if k in FTL_ROWS and k not in occurred] if (FTL_OCC and m != 'T' and (FTL_OCC_FROM is None or FTL_OCC_FROM in have)) else []
        if ready_ftl:   # FTLOCC: funding a focus makes its ready FTL ideas occur, so a player choosing a focus counts them as if under study
            cpool = {f: pool.get(f, []) + [k for k in ready_ftl if FOCUS[k] == f] for f in set(pool) | {FOCUS[k] for k in ready_ftl}}
            waiting_c = {f: sum(TARGET[ROWS[k]['tier']] * (1 + max(0.0, d - ERA_I[k])) for k in ks) for f, ks in cpool.items()}
        else: cpool, waiting_c = pool, waiting
        if VISIBLE:   # what the player can see: revealed ideas (CORE once discoverable, glimpsed, seen in rivals' hands) and their state
            rev_now = glimpsed | set(diff_since) | set(diff_unc) | obs
            idle = {k for k in disc if k not in occurred and (ROWS[k]['tier'] == 'CORE' or k in rev_now) and k not in ready_ftl}   # seen not to be under study
            vwaiting = {}
            for k in live:
                if ROWS[k]['tier'] == 'CORE' or k in rev_now: vwaiting[FOCUS[k]] = vwaiting.get(FOCUS[k], 0.0) + TARGET[ROWS[k]['tier']] * (1 + max(0.0, d - ERA_I[k]))
            cand = {}
            for k in disc:
                if k not in idle: cand.setdefault(FOCUS[k], []).append(k)
        STATE['end_k'] = end_k                                             # (a running Endeavour keeps its target open: lock-out suspended)
        if prm.player == 'specialist' and 'Mathematics' in pool: active = 'Mathematics'
        elif VISIBLE: active = _ftl_active_visible(vwaiting, cand, have, active)
        else: active = _ftl_active(waiting_c, cpool, have)
        def est_price(k): return PRICE[ROWS[k]['era']] * prm.scale * prm.premium ** max(0.0, ERA_I[k] - d)
        def est_rem(k): return max(COSTMULT.get(k, 1.0) - progress.get(k, 0.0), 0.2) * est_price(k)
        def end_price(k):                         # a Grand Endeavour's cost: 2x the price, less any study already done (END_CREDIT)
            full = COSTMULT.get(k, 1.0) * est_price(k); done = progress.get(k, 0.0) * est_price(k) if (END_CREDIT and k in occurred) else 0.0
            if END_CREDIT == 'before': return END_MULT * max(full - done, END_CREDIT_FLOOR * full)
            if END_CREDIT == 'after': return max(END_MULT * full - done, 0.0)
            if END_CREDIT == 'meter' and k in occurred and k in need: return END_MULT * full * max(1.0 - progress.get(k, 0.0) / need[k], 0.0)
            if END_CREDIT == 'true' and k in occurred and k in need: return END_MULT * max(need[k] - progress.get(k, 0.0), 0.0) * est_price(k)
            return END_MULT * full
        def is_urgent(k): return URGENT and k in occurred
        def urgent_price(k): return max(need.get(k, COSTMULT.get(k, 1.0)) - progress.get(k, 0.0), 0.0) * est_price(k)   # the meter's remainder
        def study_turns(k):                       # turns to discovery by funding k's focus: its ideas played forward under momentum, each meter
            ks = [j for j in pool.get(FOCUS[k], []) if j not in have]   # at its estimate (the price, less the study done, at least 0.2 of it)
            if k not in ks: ks.append(k)
            rem = {j: max(COSTMULT.get(j, 1.0) - progress.get(j, 0.0), 0.2) for j in ks}; prog = {j: progress.get(j, 0.0) for j in ks}
            pr = {j: est_price(j) for j in ks}; F = inc * (0.8 if 'SO05' in have else 0.5)
            for t in range(1, 401):
                left = F
                for _ in range(len(ks) + 1):
                    open_ = [j for j in ks if rem[j] > 1e-12]
                    if not open_ or left <= 1e-9: break
                    w = {j: aw(j) * (prog[j] + prm.momentum) * ATTN.get(j, 1.0) for j in open_}; tw = sum(w.values()); spent = 0.0; fin = False
                    for j in open_:
                        att = left * w[j] / tw; room = rem[j] * pr[j]
                        if att >= room: spent += room; prog[j] += rem[j]; rem[j] = 0.0; fin = True
                        else: spent += att; prog[j] += att / pr[j]; rem[j] -= att / pr[j]
                    left -= spent
                    if not fin: break
                if rem[k] <= 1e-12: return t
            return 400
        if POLICY == 'cheapest' and FUNDED:      # smarter detective: fund the focus whose cheapest targeted row would finish soonest
            pri = (PRIORITY & FUNDED) if PRIORITY else FUNDED   # higher-priority targets (the tests) take the active focus when any is workable
            capped = EXPCAP is not None and (EXPCAP_ERA is None or d < EXPCAP_ERA)
            ok_p = (lambda k: prm.premium ** max(0.0, ERA_I[k] - d) <= EXPCAP) if capped else (lambda k: True)
            pri = {k for k in pri if ok_p(k)}
            cp, est, wt = (cand, (lambda k: COSTMULT.get(k, 1.0) * est_price(k)), vwaiting) if VISIBLE else (cpool, est_rem, waiting_c)   # VISIBLE: no hidden state
            fc = {f: min(est(k) for k in ks if k in pri) for f, ks in cp.items() if any(k in pri for k in ks)}
            if not fc: fc = {f: min(est(k) for k in ks if k in FUNDED and ok_p(k)) for f, ks in cp.items() if any(k in FUNDED and ok_p(k) for k in ks)}
            if fc: active = min(fc, key=fc.get)
            elif capped and wt: active = max(wt, key=wt.get)   # nothing affordable to target: fund the most fruitful focus, as development catches up
        sh = 0.8 if 'SO05' in have else 0.5; es = END_SHARE or sh   # es: an Endeavour's share of the turn's Insight
        pausing = turn <= pause_until or (PROTO_UNTIL is not None and turn <= PROTO_UNTIL); started = False   # pausing: an urgent Endeavour's debt is being paid, or the prototype is being built
        if end_k is not None and (end_k in have or (END_RULE != 'request' and end_k not in FUNDED)): END_LOG.append((turn, end_k, 'dropped')); end_k = None; cool_until = turn + END_COOLDOWN; end_urgent = False
        if END_MULT and end_k is None and debt <= 0 and not pausing and turn >= cool_until and (END_FROM is None or any(ERA_I[k] >= END_FROM for k in have)) and (END_AFTER is None or END_AFTER in have):   # gate: first discovery of era END_FROM            # Grand Endeavour: commit to the targeted live row it saves most time on (at least a turn)
            if END_RULE == 'request' and END_REQUEST and END_REQUEST not in have and prereqs_met(END_REQUEST, have) and not (END_UNOCCURRED_ONLY and END_REQUEST in occurred):
                end_k, end_cost, end_prog = END_REQUEST, end_price(END_REQUEST), 0.0; END_LOG.append((turn, END_REQUEST, 'start')); started = True
                _ek = 'end_on_occurred' if end_k in occurred else 'end_on_unoccurred'; acct[_ek] = acct.get(_ek, 0) + 1   # (accounting only)
            best = None
            for k in ([] if (END_RULE == 'request' or END_UNOCCURRED_ONLY) else live) + [x for x in (obs | glimpsed) if END_RULE != 'request' and x not in occurred and x not in have and prereqs_met(x, have) and (x in lost or x in diff_since or x in diff_unc)]:
                if k not in FUNDED or k in have: continue
                if END_ONLY is not None and k not in END_ONLY: continue   # 'last' rule: only the last missing piece and its chain
                if k in occurred:
                    if len(att_hist.get(k, [])) < 2: continue
                    rate = sum(att_hist[k][-2:]) / 2; t_norm = est_rem(k) / rate if rate > 1e-9 else float('inf')
                    if END_RULE == 'active':      # the real alternative: make k's focus active, where k gets its automatic share of that focus
                        ks = [j for j in pool.get(FOCUS[k], []) if j not in have]
                        wj = {j: aw(j) * (progress.get(j, 0) + prm.momentum) * ATTN.get(j, 1.0) for j in ks}
                        phi = wj[k] / sum(wj.values()) if k in wj and sum(wj.values()) > 0 else 1.0
                        t_norm = min(t_norm, est_rem(k) / max(inc * sh * phi, 1e-9))
                else:                             # Revealed by a rival, but the idea never occurred here: only diffusion or an Endeavour brings it
                    s0 = diff_since.get(k, diff_unc.get(k))
                    t_norm = max(0, (5 if cp04_turn is not None else 10) - (turn - s0)) if s0 is not None else float('inf')
                cost = urgent_price(k) if is_urgent(k) else end_price(k); t_end = 1.0 if END_NOW else cost / max(inc * (1.0 if is_urgent(k) else es), 1e-9)
                if t_norm - t_end >= 1.0 and (best is None or t_norm - t_end > best[0]): best = (t_norm - t_end, k, cost)
            if best:
                end_k, end_cost, end_prog = best[1], best[2], 0.0; END_LOG.append((turn, end_k, 'start')); started = True
                _ek = 'end_on_occurred' if end_k in occurred else 'end_on_unoccurred'; acct[_ek] = acct.get(_ek, 0) + 1   # (accounting only)
        if started and is_urgent(end_k):
            end_cost, end_urgent, end_tstudy, end_t0 = urgent_price(end_k), True, (study_turns(end_k) if URGENT_DEBT else 0.0), turn
            if END_ABANDON:                       # the field's other work is dropped: it loses END_ABANDON of its progress
                for j in ([x for ks_ in pool.values() for x in ks_] if END_ABANDON_ALL else pool.get(FOCUS[end_k], [])):
                    if j != end_k and j not in have and j in progress: progress[j] *= 1.0 - END_ABANDON
        busy = end_k is not None or debt > 0 or pausing   # an Endeavour, a crash programme's repayment or an urgent one's debt holds the focus
        urgent_now = end_k is not None and end_urgent
        if end_k is not None and END_NOW:            # a crash programme: delivered now, repaid from the turns that follow
            debt, end_done = end_cost, end_k; END_LOG.append((turn, end_k, 'done')); end_k = None
        if debt > 0:
            debt -= inc * es + bank; bank = 0.0; active = None
            if debt <= 0: cool_until = turn + END_COOLDOWN
        elif end_k is not None:                     # the Endeavour is the focus: it takes the active share; the spread still rolls
            end_prog += inc * (1.0 if end_urgent else es) + bank; bank = 0.0; active = None
            if end_prog >= end_cost:
                end_done = end_k; END_LOG.append((turn, end_k, 'done')); end_k = None; cool_until = turn + END_COOLDOWN
                if end_urgent: pause_until = turn + math.ceil(URGENT_DEBT * max(0.0, end_tstudy - (turn - end_t0 + 1)) - 1e-9); end_urgent = False
        elif pausing: active = None                 # an urgent Endeavour's debt: no focus is funded; the spread goes on
        if ready_ftl and active is not None:        # FTLOCC: the funded focus's ready FTL ideas occur now and take their share this turn
            for k in ready_ftl:
                if FOCUS[k] == active and k not in occurred:
                    occurred.add(k); occ_turn[k] = turn; lost.discard(k); live.append(k); pool.setdefault(active, []).append(k)
                    acct['ftl_occ'] = acct.get('ftl_occ', 0) + 1   # (accounting only)
        if active is not None:                    # (accounting only) turns a focus was funded, and how often the funded focus changed
            acct['focus_turns'] = acct.get('focus_turns', 0) + 1
            if active != funded: acct['focus_changes'] = acct.get('focus_changes', 0) + 1
        if TRACE is not None: _fund = ('END', end_done or end_k) if (end_done or end_k is not None) else ('FOCUS', active)
        open_foci = sorted(set(pool) | set(FOCUS[k] for k in have if FOCUS[k] != blocked))
        share = 0.8 if 'SO05' in have else 0.5
        flow = {}
        others = [f for f in open_foci if f != active and (prm.spread_floor > 0 or f in pool)]
        if active: flow[active] = inc * share + bank; bank = 0.0
        elif not (SPREAD_FIX and (busy or end_done)): share = 0.0   # (no active focus: the spread takes everything)
        elif urgent_now: share = 1.0                   # an urgent Endeavour takes every Insight: the spread waits too
        elif END_SHARE:                                # the spread keeps END_SPREAD, or what the Endeavour leaves (nothing, at 1.0);
            share = 1.0 - END_SPREAD if END_SPREAD is not None else END_SHARE   # anything else is lost
            if END_ALL_NODEV and END_SPREAD is not None: cum -= inc * max(0.0, 1.0 - END_SPREAD)   # none of it counts towards development
            elif END_LOST_NODEV and END_SPREAD is not None: cum -= inc * max(0.0, 1.0 - END_SHARE - END_SPREAD)   # ...nor counts towards development
        wt = {f: pull.get(f, 0) + prm.spread_floor for f in others}; tw = sum(wt.values()) or 1
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
            def by_era(k, x):   # accounting only: x Insight of study on k, and what the premium took of it, by k's era
                e = ROWS[k]['era']; acct['att_era'][e] = acct['att_era'].get(e, 0.0) + x; acct['prem_era'][e] = acct['prem_era'].get(e, 0.0) + x * (1 - 1 / prem(k))
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
                    ws = {k: aw(k) * (progress.get(k, 0) + prm.momentum) * ATTN.get(k, 1.0) for k in cands}; tot = sum(ws.values())
                    spent = 0.0; done = []
                    for k in cands:
                        att = left * ws[k] / tot; pk = price(k); room = (need[k] - progress.get(k, 0)) * pk; att_turn[k] = att_turn.get(k, 0.0) + att
                        if att >= room: progress[k] = need[k]; done.append(k); spent += room; acct['attention'] += room; acct['premium_dilution'] += room * (1 - 1 / prem(k)); by_era(k, room)
                        else: progress[k] = progress.get(k, 0) + att / pk; spent += att; acct['attention'] += att; acct['premium_dilution'] += att * (1 - 1 / prem(k)); by_era(k, att)
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
            takers = {f: pull.get(f, 0) + 0.1 for f in pool if remaining[f] and unused.get(f, 0) <= 1e-9}
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
        for k in found:                                                   # Competing Solutions: a primary found first locks its alternatives out
            for a_ in alts_of.get(k, ()):
                if a_ not in have: locked.add(a_)
        if m != 'T':
            for k in live: att_hist[k] = (att_hist.get(k, []) + [att_turn.get(k, 0.0)])[-3:]
        log.append((turn, d, len(found)))
        if TRACE is not None:
            _new = sorted(occurred - _occ0)
            TRACE.append(dict(turn=turn, d=d, found=list(found), diff=[k for k in found if k in diff_due], endv=[end_done] if end_done else [],
                              occ=[(k, 'core' if ROWS[k]['tier'] == 'CORE' else ('funded' if (k in _fund0 and ROWS[k]['tier'] == 'STANDARD' and ROWS[k]['era'] == 'Space') else 'chance')) for k in _new],
                              glim=sorted(glimpsed - _gl0), fund=_fund,
                              # the rest of the research state, for the replay viewer (design/mockups/sim_web): ideas lost this turn, rows first seen in
                              # rivals' hands, alternatives locked out, ideas rediscovered, the turn's Insight, the funded share and each focus's Insight, every
                              # idea under study's hidden meter (progress / need) and a running Endeavour's progress
                              lost=sorted(lost - _lost0), seen=sorted((set(diff_since) | set(diff_unc)) - _seen0), locked=sorted(locked - _lk0),
                              redisc=sorted(k for k, tt in rediscovered.items() if tt == turn), inc=round(inc, 3), share=share,
                              flow={f: round(v, 2) for f, v in flow.items()},
                              prog={k: round(min(progress.get(k, 0.0) / need[k], 1.0), 3) for k in live if k not in have and need.get(k)},
                              end=[end_k, round(end_prog / end_cost, 3) if end_cost else 0.0] if end_k is not None else None))
    acct.update(held_open=len(held), held_occurred=len(held & occurred), held_lost=len(held & lost),
                lost_standard=sum(1 for k in lost if ROWS[k]['tier'] == 'STANDARD'))   # (accounting only)
    acct['banked_end'] = bank; acct['recovered_ideas'] = len(rediscovered); run.acct = acct; run.opened = opened; run.occ = occ_turn; run.rediscovered = rediscovered; run.lost_at = lost_at; run.locked = locked
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
