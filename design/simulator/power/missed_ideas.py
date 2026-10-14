"""How much of the tree missed ideas lock, on the discovery model every measurement since 1 October uses (the workshop's
candidate, w7c_cfg.json) with what has been agreed since: the glimpse (proximity revelation: STANDARD ideas 10% a turn,
UNCOMMON 3% provisionally, RARE and UNIQUE never) and knowledge diffusion from five contacted rivals. The workshop's balanced player funds the focus with the most waiting; it has no FTL agenda and
commissions no Endeavours, so a lost idea it glimpsed stays lost here, counted as one an Endeavour could still bring.
A game ends when the civilisation's development passes the end of the tree. Space-era figures leave out the FTL pricing
levers' effect on an agenda and W16's funded-focus rule (this player has no agenda), so read the eras before it.
workshop_measures.py measures the same and more (pace, tiers, catch-up, accelerators); this script adds the bare setting
and runs any world quickly.

Usage: python3 missed_ideas.py <world> <games> [bare] [isolated] [connected]
  bare       the 2 October sweep's setting: no glimpse, no diffusion
  isolated   the glimpse, no contacts
  connected  the glimpse, and five rivals replayed from results/w7f_<world>_pool.json, met in the Early Modern era
"""
import sys, os, re, json, statistics as st, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import defaults   # noqa: F401  (the tree, and the finalised switches)
import harness_ftl_e as HF, worlds as W, harness as H, prices

NAME = sys.argv[1]; N = int(sys.argv[2]); MODES = sys.argv[3:] or ['bare', 'isolated', 'connected']
ROWS = W.set_world(None if NAME == 'familiar' else NAME)
HF.ROWS = ROWS; HF.IDS = sorted(ROWS); HF.FOCUS = {k: ROWS[k]['focus'] for k in HF.IDS}; HF.ERA_I = {k: HF.EO.index(ROWS[k]['era']) for k in HF.IDS}
prices.apply(HF, ROWS)
CFG = json.load(open(os.path.join(HERE, 'w7c_cfg.json')))
POOL = json.load(open(os.path.join(HERE, 'results', f'w7f_{NAME}_pool.json')))
NAMES = dict(re.findall(r'^\| ([A-Z][A-Z0-9-]*[0-9][A-Z]?(?:-W)?|ME-B) \| \*\*(.+?)\*\* \|', open(defaults.TREE, encoding='utf-8').read(), re.M))
EVERY = set(HF.IDS); TIER = {k: ROWS[k]['tier'] for k in EVERY}; ERA = {k: ROWS[k]['era'] for k in EVERY}

def closure(base, allowed):
    """everything reachable from `base`, discovering only rows in `allowed`"""
    cur = set(base); todo = True
    while todo:
        todo = False
        for k in HF.IDS:
            if k not in cur and k in allowed and H.prereqs_met(k, cur): cur.add(k); todo = True
    return cur

def game(mode, j):
    HF.GLIMPSE = 0.0 if mode == 'bare' else {'STANDARD': 0.1, 'UNCOMMON': 0.03, 'RARE': 0.0, 'UNIQUE': 0.0}; HF.OBS = False
    HF.DIFF = dict(rivals=[POOL[(5 * j + i) % len(POOL)]['t'] for i in range(5)], contact_era=HF.EO.index('Early Modern')) if mode == 'connected' else None
    HF.TARGET_FN = None; HF.END_MULT = None; HF.RUN_ON = False; HF.STOP_FN = None; HF.DIFF_LOG.clear()
    have, _ = HF.run(HF.P(**CFG), 40000 + j)
    have = set(have); lost = set(HF.STATE['lost']); glimpsed = set(HF.STATE['glimpsed'])
    gone = lost - have; gone_std = {k for k in gone if TIER[k] == 'STANDARD'}
    other = gone - gone_std                                                   # lost UNCOMMON, RARE and UNIQUE ideas: missable by design
    reach = closure(have, EVERY - gone)                                       # still reachable without the lost ideas
    locked = closure(have, EVERY - other) - reach - gone                      # rows that only lost STANDARD ideas stand in front of
    hard = locked - closure(have, EVERY - other - (gone_std - glimpsed))      # ... still locked after an Endeavour for every glimpsed one
    guards = {k: len(closure(reach | {k}, EVERY - gone) - reach - {k}) for k in gone_std}
    pre = lambda S: {k for k in S if ERA[k] != 'Space'}
    gl_tier = {t: (sum(1 for k in gone if TIER[k] == t and k in glimpsed), sum(1 for k in gone if TIER[k] == t)) for t in ('STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE')}
    return dict(gl_tier=gl_tier, found=len(have), lost=collections.Counter(TIER[k] for k in gone), std=len(pre(gone_std)), std_gl=len(pre(gone_std & glimpsed)),
                recovered=len(lost & have), locked=len(pre(locked)), hard=len(pre(hard)), guards=guards,
                lost_era=collections.Counter(ERA[k] for k in gone_std))

def q(v, p):
    v = sorted(v); return v[min(len(v) - 1, int(round(p / 100 * (len(v) - 1))))]

print(f"{NAME}: {len(EVERY)} rows, {N} games per setting (balanced player, no Endeavours; games end at the end of the tree)")
for mode in MODES:
    G = [game(mode, j) for j in range(N)]
    def line(key):
        v = [g[key] for g in G]; return f"mean {st.mean(v):.1f} (median {st.median(v):.0f}, p90 {q(v, 90)}, max {max(v)})"
    print(f"\n{mode:9}  discovered {st.mean(g['found'] for g in G):.0f}; lost ideas later recovered by diffusion {st.mean(g['recovered'] for g in G):.1f}")
    print(f"           before the Space era: STANDARD ideas lost for good {line('std')}; of them glimpsed {st.mean(g['std_gl'] for g in G):.1f}")
    print(f"           before the Space era: rows locked behind lost STANDARD ideas {line('locked')}")
    print(f"           ... and still locked after an Endeavour for every glimpsed one {line('hard')}")
    by_era = collections.Counter()
    for g in G: by_era.update(g['lost_era'])
    print("           lost STANDARD ideas by era (mean a game): " + ', '.join(f"{e} {by_era[e] / N:.1f}" for e in HF.EO if by_era[e]))
    if mode != 'bare':
        print('           lost ideas glimpsed (Revealed, so an Endeavour can take them), by tier: ' + ', '.join(
            f"{t} {100 * sum(g['gl_tier'][t][0] for g in G) / max(1, sum(g['gl_tier'][t][1] for g in G)):.0f}% of {sum(g['gl_tier'][t][1] for g in G) / N:.1f}" for t in ('STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE')))
    print("           other tiers lost (missable by design): " + ', '.join(f"{t} {st.mean(g['lost'][t] for g in G):.1f}" for t in ('UNCOMMON', 'RARE', 'UNIQUE')))
    gate = collections.defaultdict(list)
    for g in G:
        for k, n in g['guards'].items(): gate[k].append(n)
    top = sorted(gate.items(), key=lambda kv: -sum(kv[1]))[:12]
    print("           biggest gateways (lost in % of games; rows it alone guards when lost, mean):\n             " +
          '; '.join(f"{k} {NAMES.get(k, '')} {100 * len(v) / N:.0f}%, {st.mean(v):.0f}" for k, v in top))
