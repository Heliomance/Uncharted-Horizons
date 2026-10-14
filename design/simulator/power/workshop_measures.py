"""The discovery-model workshop's measurements (design/notes/discovery_workshop_report.md), rebuilt on the harness that
models rivals and knowledge diffusion (harness_ftl_e.py) and on the agreed design's prices (prices.py). The workshop's own
scripts were lost; each measure follows the report's definitions. The player is the workshop's balanced player: it funds
the focus with the most waiting, has no FTL agenda and commissions no Endeavours. Games end when the civilisation's
development passes the end of the tree.

Usage: python3 workshop_measures.py <world> <setting> [key=value ...]
  setting      isolated (no contacts) | connected (five rivals replayed from results/w7f_<world>_pool.json, met in the
               Early Modern era, as the FTL benchmarks have them)
  games=60     games per measure
  glimpse=0.1  STANDARD's chance a turn of being glimpsed; gu=<p> UNCOMMON's (default 0.03); RARE and UNIQUE never
  gall=<p>     the old rule instead: the same glimpse chance for every tier
  scale=<x>    the model's price calibration (default: w7c_cfg.json's)
  workers=<n>  games played in parallel (default: every core; also the WORKERS variable)
  only=a,b     run only some measures: pace (with tiers, Insight, missed ideas and era entry), catchup, accel, premium, calib
  label=<name> results/workshop_<world>_<setting>_<label>.json (default: the settings)
"""
import sys, os, re, json, math, statistics as st, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import defaults   # noqa: F401  (the tree, and the finalised switches)
import harness_ftl_e as HF, worlds as W, harness as H, prices

NAME, SETTING = sys.argv[1], sys.argv[2]
OPT = dict(a.split('=', 1) for a in sys.argv[3:])
N = int(OPT.get('games', 60))
ROWS = W.set_world(None if NAME == 'familiar' else NAME)
HF.ROWS = ROWS; HF.IDS = sorted(ROWS); HF.FOCUS = {k: ROWS[k]['focus'] for k in HF.IDS}; HF.ERA_I = {k: HF.EO.index(ROWS[k]['era']) for k in HF.IDS}
prices.apply(HF, ROWS)
CFG = json.load(open(os.path.join(HERE, 'w7c_cfg.json')))
if 'scale' in OPT: CFG['scale'] = float(OPT['scale'])
if OPT.get('fundedwin') == '1': CFG['funded_windows'] = True          # a STANDARD window stays open while its focus is funded
if 'rediscover' in OPT: CFG['rediscover'] = float(OPT['rediscover'])  # rediscovery on demand: chance a turn per breakthrough waiting on a lost idea
if 'tieratt' in OPT: CFG['tier_attention'] = OPT['tieratt'] == '1'        # tieratt=0: once occurred, every tier is studied alike
POOL = json.load(open(os.path.join(HERE, 'results', f'w7f_{NAME}_pool.json')))
GL = ({t: float(OPT['gall']) for t in ('STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE')} if 'gall' in OPT else
      {'STANDARD': float(OPT.get('glimpse', 0.1)), 'UNCOMMON': float(OPT.get('gu', 0.03)), 'RARE': 0.0, 'UNIQUE': 0.0})
EO = HF.EO; EVERY = set(HF.IDS); TIER = {k: ROWS[k]['tier'] for k in EVERY}; ERA = {k: ROWS[k]['era'] for k in EVERY}
TIERS = ('CORE', 'STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE')
ENTRY = {'Ancient': 5, 'Classical': 3, 'Medieval': 3, 'Early Modern': 5, 'Modern': 7, 'Atomic': 6, 'Space': 4}   # §2's provisional counts
NAMES = dict(re.findall(r'^\| ([A-Z][A-Z0-9-]*[0-9][A-Z]?(?:-W)?|ME-B) \| \*\*(.+?)\*\* \|', open(defaults.TREE, encoding='utf-8').read(), re.M))
SEED0 = 50000


def game(j, **kw):
    """one game: the j-th seed, this setting's contacts, the agreed glimpse; kw overrides the model's parameters"""
    HF.GLIMPSE = GL; HF.OBS = False; HF.ECON = 1.0
    HF.DIFF = dict(rivals=[POOL[(5 * j + i) % len(POOL)]['t'] for i in range(5)], contact_era=EO.index('Early Modern')) if SETTING == 'connected' else None
    HF.TARGET_FN = None; HF.END_MULT = None; HF.RUN_ON = False; HF.STOP_FN = None; HF.DIFF_LOG.clear(); HF.FUNDED = set()
    have, log = HF.run(HF.P(**{**CFG, **kw}), SEED0 + j)
    return have, log, dict(HF.run.acct), dict(HF.run.opened), set(HF.STATE['glimpsed']), len(HF.DIFF_LOG)


def closure(base, allowed):
    cur = set(base); todo = True
    while todo:
        todo = False
        for k in HF.IDS:
            if k not in cur and k in allowed and H.prereqs_met(k, cur): cur.add(k); todo = True
    return cur


def q(v, p):
    v = sorted(v); return v[min(len(v) - 1, int(round(p / 100 * (len(v) - 1))))] if v else None


WORKERS = int(OPT.get('workers') or os.environ.get('WORKERS') or os.cpu_count() or 1)   # games played in parallel (workers=1: one after another)
_POOL = None


def pmap(fn, args):
    """[fn(*a) for a in args], spread over WORKERS processes, results in order. Each worker is a fork of this process
    after its setup, and every game sets its own state, so the results are the same as one after another."""
    global _POOL
    if WORKERS <= 1 or len(args) <= 1: return [fn(*a) for a in args]
    if _POOL is None:
        import multiprocessing
        _POOL = multiprocessing.get_context('fork').Pool(WORKERS)
    return _POOL.starmap(fn, args, chunksize=1)


def pace_game(j):
    """one game's share of pace(): everything it needs, computed where the game was played"""
    have, log, acct, opened, glimpsed, ndiff = game(j)
    by = collections.defaultdict(list)
    for turn, d, c in log: by[EO[min(int(d), len(EO) - 1)]].append(c)
    rate = {t: [0, 0] for t in TIERS}
    for k in opened: rate[TIER[k]][1] += 1; rate[TIER[k]][0] += k in have
    missed = {k for k in opened if k not in have and ERA[k] != 'Space'}   # opened before the Space era and never discovered
    gl = {}
    for t in TIERS:
        mt = {k for k in missed if TIER[k] == t}; gl[t] = (len(mt & glimpsed), len(mt))
    m_std = {k for k in missed if TIER[k] == 'STANDARD'}; other = missed - m_std
    reach = closure(have, EVERY - missed)
    locked = {k for k in closure(have, EVERY - other) - reach - missed if ERA[k] != 'Space'}
    hard = {k for k in locked - closure(have, EVERY - other - (m_std - glimpsed)) if ERA[k] != 'Space'}
    guards = {k: len(closure(reach | {k}, EVERY - missed) - reach - {k}) for k in m_std}
    dev = {turn: d for turn, d, _ in log}; turns = sorted((have[k][0], HF.ERA_I[k]) for k in have); entry = {}
    for e, n in ENTRY.items():                     # era entry: development at the turn the civilisation holds §2's count
        ei = EO.index(e); cnt = 0
        for turn, i in turns:
            cnt += i >= ei
            if cnt >= n: entry[e] = dev[turn] - ei; break
    return dict(by=dict(by), offs=[have[k][1] - HF.ERA_I[k] for k in have], rate=rate, ndiff=ndiff, gl=gl, entry=entry, guards=guards,
                acct={key: acct.get(key, 0.0) for key in ('income', 'attention', 'premium_dilution', 'lost_empty', 'lost_cap', 'recovered')},
                miss=(len(m_std), len(locked), len(hard)), rec=acct.get('recovered_ideas', 0),
                leaves=sum(1 for k in m_std if not guards[k]),
                held=[acct.get(key, 0) for key in ('lost_standard', 'held_open', 'held_occurred', 'held_lost', 'focus_turns', 'focus_changes')])


def pace():
    """cadence, clumps, dry spells, lateness, tier rates, Insight accounting, missed ideas and era entry, from one set of games"""
    per = collections.defaultdict(list); clumps = collections.defaultdict(list); drought = collections.defaultdict(list)
    offs = []; rate = {t: [0, 0] for t in TIERS}; acc = collections.Counter(); diffused = []
    miss = collections.defaultdict(list); gl = {t: [0, 0] for t in TIERS}; gate = collections.defaultdict(list)
    entry = collections.defaultdict(list); rec = []; leaves = []; held = []
    for g in pmap(pace_game, [(j,) for j in range(N)]):
        rec.append(g['rec']); leaves.append(g['leaves']); held.append(g['held'])
        for e, cs in g['by'].items():
            per[e].append(st.mean(cs)); clumps[e].append(sum(c >= 3 for c in cs) / len(cs))
            best = cur = 0
            for c in cs: cur = cur + 1 if c == 0 else 0; best = max(best, cur)
            drought[e].append(best)
        offs += g['offs']
        for t, (a, b) in g['rate'].items(): rate[t][0] += a; rate[t][1] += b
        for key, v in g['acct'].items(): acc[key] += v
        diffused.append(g['ndiff'])
        for t, (a, b) in g['gl'].items(): gl[t][0] += a; gl[t][1] += b
        miss['standard'].append(g['miss'][0]); miss['locked'].append(g['miss'][1]); miss['hard'].append(g['miss'][2])
        for k, n in g['guards'].items(): gate[k].append(n)
        for e, v in g['entry'].items(): entry[e].append(v)
    out = {'cadence': {e: round(st.mean(per[e]), 2) for e in EO if per[e]},
           'clump%': {e: round(100 * st.mean(clumps[e]), 1) for e in EO if clumps[e]},
           'drought': {e: round(st.mean(drought[e]), 1) for e in EO if drought[e]},
           'lateness': round(st.median(offs), 2), 'outside own era %': round(100 * sum(not (0 <= o < 1) for o in offs) / len(offs), 1),
           '>=1 era early %': round(100 * sum(o < -1 for o in offs) / len(offs), 2), 'earliest': round(min(offs), 2),
           'rates among discoverable': {t: round(a / b, 2) if b else None for t, (a, b) in rate.items()},
           'insight': {'became progress': round(acc['attention'] / acc['income'], 3), 'premium share of progress': round(acc['premium_dilution'] / max(acc['attention'], 1e-9), 3),
                       'net lost': round((acc['lost_empty'] + acc['lost_cap'] - acc['recovered']) / acc['income'], 3)},
           'diffusion arrivals a game': round(st.mean(diffused), 1),
           'missed STANDARD before Space': [round(st.mean(miss['standard']), 1), q(miss['standard'], 90)],
           'of them guarding nothing': round(st.mean(leaves), 1), 'ideas rediscovered a game': round(st.mean(rec), 1),
           'rows they lock': [round(st.mean(miss['locked']), 1), q(miss['locked'], 90), max(miss['locked'])],
           'still locked with Endeavours on glimpsed': [round(st.mean(miss['hard']), 1), q(miss['hard'], 90), max(miss['hard'])],
           'missed glimpsed %': {t: round(100 * a / b) if b else None for t, (a, b) in gl.items() if t != 'CORE'},
           'missed a game by tier': {t: round(b / N, 1) for t, (a, b) in gl.items() if t != 'CORE'},
           'gateways': [(k, NAMES.get(k, ''), round(100 * len(v) / N), round(st.mean(v))) for k, v in sorted(gate.items(), key=lambda kv: -sum(kv[1]))[:8]],
           'era entry, development minus era (median)': {e: round(st.median(v), 2) for e, v in entry.items() if v}}
    if CFG.get('funded_windows'):              # what the funded-window rule did: windows it held open, and what became of those ideas
        h = [sum(x[i] for x in held) / N for i in range(6)]
        out['funded windows, a game'] = {'STANDARD ideas lost': round(h[0], 1), 'held open while funded': round(h[1], 2), 'then occurred': round(h[2], 2),
                                         'then closed when the focus moved on': round(h[3], 2), 'turns a focus stays funded': round(h[4] / max(h[5], 1e-9), 1)}
    return out


def catchup_game(j, unblock, old):
    have, log, *_ = game(j, blocked_focus='Seafaring', unblock_dev=unblock)
    t0 = next(turn for turn, d, _ in log if d >= unblock)
    return (have['SF09'][0] - t0 if 'SF09' in have else None), sum(1 for k in old if k in have and have[k][0] - t0 <= 10) / len(old)


def catchup(unblock=5.0):
    """a landlocked civilisation reaches the coast as its development enters the Modern era (5.0: the point at which this test
    reproduces the workshop's median of 6 turns): turns until its Caravel (SF09), and the share of its old Seafaring
    foundations (CORE and STANDARD rows from earlier eras) it holds within 10 turns of reaching the coast"""
    old = [k for k in EVERY if HF.FOCUS[k] == 'Seafaring' and HF.ERA_I[k] < int(unblock) and TIER[k] in ('CORE', 'STANDARD')]
    res = pmap(catchup_game, [(j, unblock, old) for j in range(N)])
    cav = [c for c, _ in res if c is not None]; share = [sh for _, sh in res]
    return {'unblock at development': unblock, 'Caravel turns after the coast (median)': st.median(cav) if cav else None,
            'games without a Caravel %': round(100 * (N - len(cav)) / N), 'old Seafaring foundations within 10 turns %': round(100 * st.mean(share))}


ACCEL = [('MA05', 'balanced'), ('MA05', 'specialist'), ('MC19', 'balanced'), ('ME18', 'balanced'), ('CH09-W', 'balanced'), ('SF09', 'balanced')]


def found_in(j, kw):
    """one game's discoveries, {row: (turn, development)}"""
    return game(j, **kw)[0]


def accel():
    """paired runs, the same seed with and without an accelerator: median turns and eras earlier, where both find the row"""
    out = {}; base = {}
    for player in ('balanced', 'specialist'):
        base[player] = pmap(found_in, [(j, {'player': player}) for j in range(N)])
    for k, player in ACCEL:
        if k not in EVERY: continue
        for kind, kw in (('head start 1/2', {'accel_head': {k: 0.5}}), ('price x0.5', {'accel_price': {k: 0.5}})):
            accd = pmap(found_in, [(j, {'player': player, **kw}) for j in range(N)])
            dt = []; dd = []
            for a, b in zip(base[player], accd):
                if k in a and k in b: dt.append(a[k][0] - b[k][0]); dd.append(a[k][1] - b[k][1])
            out[f"{k} {NAMES.get(k, '')} ({player}), {kind}"] = [st.median(dt), round(st.median(dd), 2)] if dt else None
    return out


def offsets(j, kw):
    """one game: each discovery's development at the time minus its era"""
    have = game(j, **kw)[0]; return [have[k][1] - HF.ERA_I[k] for k in have]


def lateness_at(scale, n=8, **kw):
    return st.median([o for offs in pmap(offsets, [(j, {'scale': scale, **kw}) for j in range(n)]) for o in offs])


def calibrate(target=0.5, **kw):
    """the scale on the era prices at which half of all breakthroughs arrive by the middle of their own era, as the workshop calibrated"""
    lo, hi = 0.2, 3.0
    for _ in range(12):
        mid = math.sqrt(lo * hi)
        if lateness_at(mid, **kw) > target: hi = mid
        else: lo = mid
    return round(math.sqrt(lo * hi), 3)


def premium():
    out = {}
    for p in (2.0, 4.0, 8.0):
        sc = calibrate(premium=p); offs = []; calc = {'balanced': [], 'specialist': []}
        args = [(j, {'premium': p, 'scale': sc, 'player': player}) for j in range(N) for player in ('balanced', 'specialist')]
        for (j, kw), have in zip(args, pmap(found_in, args)):
            if kw['player'] == 'balanced': offs += [have[k][1] - HF.ERA_I[k] for k in have]
            if 'MA05' in have: calc[kw['player']].append(have['MA05'][1] - HF.ERA_I['MA05'])
        out[f'x{p:g}'] = {'scale': sc, 'outside own era %': round(100 * sum(not (0 <= o < 1) for o in offs) / len(offs), 1),
                          '>=1 era early %': round(100 * sum(o < -1 for o in offs) / len(offs), 2), 'earliest': round(min(offs), 2),
                          'Calculus, balanced / specialist (median eras from its era)': [round(st.median(v), 2) for v in calc.values()]}
    return out


MEASURES = {'pace': pace, 'catchup': catchup, 'accel': accel, 'premium': premium, 'calib': lambda: {'scale': calibrate(), 'in use': CFG['scale']}}
only = [m for m in OPT['only'].split(',') if m] if 'only' in OPT else list(MEASURES)   # only= (empty): load, run nothing
label = OPT.get('label') or '_'.join(f'{k}{v}' for k, v in OPT.items() if k not in ('only', 'games')) or 'agreed'
res = {'world': NAME, 'setting': SETTING, 'games': N, 'glimpse': GL, 'model': CFG}
for m in only: res[m] = MEASURES[m](); print(f'{m}: {json.dumps(res[m], ensure_ascii=False)}', flush=True)
if only:
    path = os.path.join(HERE, 'results', f'workshop_{NAME}_{SETTING}_{label}.json')
    old = json.load(open(path)) if os.path.exists(path) else {}
    json.dump({**old, **res}, open(path, 'w'), indent=1, ensure_ascii=False)
