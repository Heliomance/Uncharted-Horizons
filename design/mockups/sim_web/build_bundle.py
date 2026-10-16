"""The data both web mockups run on (the replay viewer and the live game), taken from the simulator's own modules so that the
JavaScript engine (engine.js) plays exactly the game the Python harness plays: every row a world holds with its focus, tier,
era and prerequisite groups; the prices, odds, windows and model parameters in force (defaults.py); the economy's Insight and
development turn by turn for each benchmark economy (the harness's income depends only on the turn); the FTL definitions and
world truths (w7f.py, with the agreed levers); Competing Solutions; the rivals that knowledge diffusion replays (the default
pool); and what the victory needs (victory.py's prototype price and SS FTL Drive times).

Run it through scratch_run.sh, which gives it the run's own patched copy of the tree:
  cd design/simulator/power && bash scratch_run.sh python3 ../../mockups/sim_web/build_bundle.py
Output: design/mockups/sim_web/bundle.json
"""
import os, sys, re, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
POWER = os.path.normpath(os.path.join(HERE, '..', '..', 'simulator', 'power'))
sys.path.insert(0, POWER)
import defaults
import harness_ftl_e as HF, worlds as W, gen_data as G, prices, competing, victory as V, harness as H0, reach as R

EO = HF.EO
TREE = open(defaults.TREE, encoding='utf-8').read()
VERSION = re.search(r'Complete Tech Tree Design Document \((v[\d.]+)\)', TREE).group(1)

# ---- the run's switches, as w7f.py reads them -------------------------------------------------------------------------
env = os.environ
HF.DEV_ENDS = {e.replace('_', ' '): float(x) for e, x in (i.split(':') for i in env['DEVENDS'].split(','))} if env.get('DEVENDS') else None
HF.WIN_TURNS = {e.replace('_', ' '): float(x) for e, x in (i.split(':') for i in env['WINTURNS'].split(','))} if env.get('WINTURNS') else None
CFG = json.load(open(os.path.join(POWER, 'w7c_cfg.json')))
if env.get('REDISCOVER'): CFG['rediscover'] = float(env['REDISCOVER'])
P = HF.P(**CFG)
LEVERS = env.get('LEVERS', '')

# ---- rows: names, texts and the player-facing effect, from the document -------------------------------------------------
FOCI = []
for m in re.finditer(r'^#{2,4} FOCUS: ([A-Z][A-Z &\'-]+?)\s*(\S+)?\s*$', TREE[:TREE.index('\n## 4.')], re.M):
    FOCI.append(dict(name=m.group(1).strip().title(), icon=m.group(2) or ''))
NAMES = {k: re.sub(r'\*', '', c[1]).strip() for k, c in R.rows.items()}
try:
    TEXTS = {x['id']: x for x in json.load(open(os.path.join(HERE, '..', 'research_screen', 'texts.json'), encoding='utf-8'))}
except FileNotFoundError:
    TEXTS = {}
HIDDEN = re.compile(r'\bHost|\bhosts\b|FQ\d|World Truth|validated|dead-?end|Frontier|axis|\bworlds? only\b|W\d{1,2}\b|§|\(see |merged here|cut in v|v3\.\d+', re.I)


def plain(s):
    """an effect cell as plain text: the notation's brackets and markup removed"""
    s = re.sub(r'`([^`]*)`', r'\1', s)
    s = s.replace('⟨', '').replace('⟩', '').replace('**', '').replace('*', '').replace('ⁿ', '')
    s = re.sub(r'\[([^\[\]]*)\]', r'\1', s)
    s = re.sub(r'\s+', ' ', s).strip(' ;')
    return s


ROW_ID = re.compile(r'(?<![\w-])(' + '|'.join(sorted(map(re.escape, R.rows), key=len, reverse=True)) + r')(?![\w-])')
TIER_WORD = re.compile(r'\b(?:CORE|STANDARD|UNCOMMON|RARE|UNIQUE)\b')


def short_name(k):
    return NAMES.get(k, '').split(' (')[0].strip()


def name_of(m):
    """a row id in a text, as the player reads it: the row's name ('NP15's' -> 'Superconducting Storage Rings'')"""
    n = short_name(m.group(1))
    return (n + ("'" if n.endswith('s') else "'s")) if m.group(0).endswith("'s") else n


ID_POSS = re.compile(ROW_ID.pattern + r"(?:'s)?")


def scrub(s):
    """a text the player sees, cleared of what the player must never see (SPEC.md): row ids, the odds of world forks and the
    forks themselves, edit history, tier words in design notes; Unciv's unique syntax read as plain words"""
    if not s: return s
    s = re.sub(r'<([^<>]*)>', r'\1', s)                                     # Unciv conditionals: '<when attacking>' -> 'when attacking'
    s = re.sub(r'\{([^{}]*)\}', r'\1', s)                                   # Unciv parameters: '{Friendly}' -> 'Friendly'
    s = re.sub(r'(Reveals [^:\[\];.]*?):[^\]]*', r'\1', s)                  # 'Reveals the fork this world takes: X in Y worlds (~55%), ...'
    s = re.sub(r'\s*\(~?\d+%\)', '', s)                                     # odds
    s = re.sub(r'\s*—\s*CORE because[^.]*\.', '.', s)                       # 'Public School — CORE because ...'
    s = re.sub(r'[;,]?\s*moved here from\s+' + ROW_ID.pattern, '', s)         # edit history
    s = re.sub(r'\s*(?:—\s*)?\bsee\s+' + ROW_ID.pattern, '', s)               # cross-references
    for k in set(ROW_ID.findall(s)):                                         # 'QP15 Beyond the Standard Model': the id goes, the name stays
        if short_name(k): s = re.sub(r'(?<![\w-])' + re.escape(k) + r'\s+(?=' + re.escape(short_name(k)) + r')', '', s)

    def paren(m):                                                            # a parenthesis naming rows: a design note, or names with codes
        inner = m.group(1)
        if not ROW_ID.search(inner) and not TIER_WORD.search(inner): return m.group(0)
        if TIER_WORD.search(inner) or re.search(r'\bmove[sd]?\b|\bbelong|\.\s*$', inner): return ''
        if not re.search(r'[a-z]', ROW_ID.sub('', inner)): return ''           # nothing but codes: '(O13/O14/O15)', '(AE02, AE13, AE12)'
        inner = re.sub(r',\s*' + ROW_ID.pattern + r'\s*$', '', inner)           # a code annotating the name before it: '(the Harbor, SF08)'
        inner = re.sub(r'^' + ROW_ID.pattern + r',\s*', '', inner)              # '(EN11, with television)'
        return ' (' + ID_POSS.sub(name_of, inner).strip() + ')'
    s = re.sub(r'\s*\(([^()]*)\)', paren, s)
    s = ID_POSS.sub(name_of, s)                                              # a bare id: the row's name
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z(\[“"])', s)
    s = ' '.join(x for x in sentences if not TIER_WORD.search(x))          # design notes about tiers ('RARE.', 'reclassified as RARE ...')
    s = re.sub(r'\s+([,;.])', r'\1', re.sub(r'\s{2,}', ' ', s)).strip()
    return s


def clip(s, n):
    """at most n characters, cut at the end of a sentence or clause"""
    if len(s) <= n: return s
    cut = max(s.rfind('. ', 0, n), s.rfind('; ', 0, n))
    return (s[:cut + 1] if cut > n // 3 else s[:n].rsplit(' ', 1)[0]) + ' …'


def effect_text(k):
    """what the breakthrough does, for the player: the effect cell's sentences that reveal nothing hidden"""
    t = TEXTS.get(k, {})
    cell = re.sub(r'\s*\([^()]*(?:merged here|cut in v3|v3\.\d+)[^()]*\)', '', R.rows[k][5])   # edit history, not effects
    cell = re.sub(r'\s*\((?:[A-Z]{1,3}(?:-[A-Z]+)?\d+[A-Z]?(?:-W)?(?:,? (?:or|and) )?)+\)', '', cell)        # row codes
    parts = re.split(r'(?<=[.;])\s+(?=[A-Z⟨*(])', cell)
    keep = [re.sub(r'(?:^|;\s*)(?:[Gg]rants|[Rr]ead as) [A-Z_]{4,}(?: and [A-Z_]{4,})?;?\s*', ' ', p) for p in parts if not HIDDEN.search(p)]
    note = plain(R.rows[k][6]) if len(R.rows[k]) > 6 and not HIDDEN.search(R.rows[k][6]) else ''
    return dict(fx=clip(scrub(plain(' '.join(keep))), 480), flav=scrub(t['flav']) if t.get('flav') else clip(scrub(note), 300), conj=scrub(t.get('conj', '')))


# ---- the FTL definitions (w7f.py, with the agreed levers) ---------------------------------------------------------------
FTL = {
    'atomic': dict(
        HOST={'exotic': ['QP11'], 'extradim': ['QP09', 'QP10'], 'discrete': ['QP09', 'QP10'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'],
              'leak': ['RC11'], 'dark': ['RC05'], 'coherence': ['CP21'], 'hartman': ['QP14'], 'tachDE': ['RC06'], 'tachyon': ['QP15']},
        COND={'Warp': ['exotic', 'extradim', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['extradim', 'leak', 'dark'],
              'Tunnelling': ['coherence', 'discrete', 'hartman'], 'Tachyonic': ['tachDE', 'closed', 'tachyon']},
        CLOSE='QP08',
        BUILD={'Warp': [['RC01'], ['QP08'], ['QP11'], ['MS08'], ['ES06', 'ES07', 'ES14', 'ES08'], ['ES18']],
               'Wormhole': [['RC01'], ['QP08'], ['QP11'], ['MS08'], ['RC04'], ['QP12'], ['MA13']],
               'Hyperspace': [['QP08'], ['MA13'], ['ES06', 'ES07', 'ES14', 'ES08'], ['MA19']],
               'Tunnelling': [['QP02'], ['CP10'], ['MS02', 'GN05'], ['QP14'], ['CP21']],
               'Tachyonic': [['QP06'], ['QP08'], ['NP11'], ['SE02'], ['ES06', 'ES07', 'ES14', 'ES08'], ['NP15']]},
        PROPOSER={'Warp': 'RC01', 'Wormhole': 'RC01', 'Tachyonic': 'RC01', 'Hyperspace': 'MA13', 'Tunnelling': 'QP02'},
        QUESTION={'exotic': 'Exotic matter holds', 'extradim': 'Extra dimensions exist', 'discrete': 'Spacetime is discrete', 'bubble': 'The bubble is stable',
                  'closed': 'Closed timelike curves are stable', 'throat': 'The throat is stable', 'leak': 'Gravitational leakage shows the dimensions are open',
                  'dark': 'Dark matter is a hidden sector', 'coherence': 'Coherence survives at macroscopic scale',
                  'hartman': 'Tunnelling carries information faster than light (the Hartman effect)', 'tachDE': 'Dark energy is a tachyonic field',
                  'tachyon': 'A tachyonic sector exists'},
        ok='discrete != extradim and (extradim or not leak)'),
    'elemental': dict(
        HOST={'exotic': ['QM-E06'], 'strata': ['QM-E12'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'], 'leak': ['RC11'], 'dark': ['RC05'],
              'superlum': ['RC06'], 'catalogue': ['QM-E28'], 'currents': ['QM-E19'], 'coupling': ['AE20']},
        COND={'Warp': ['exotic', 'strata', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['strata', 'leak', 'dark'],
              'Tachyonic': ['superlum', 'closed', 'catalogue'], 'Plenum': ['currents', 'superlum', 'coupling']},
        CLOSE='QM-E27',
        BUILD={'Warp': [['RC01'], ['QM-E27'], ['QM-E06'], ['MS08'], ['ES07', 'ES15', 'QM-E05'], ['ES18']],
               'Wormhole': [['RC01'], ['QM-E27'], ['QM-E06'], ['MS08'], ['RC04'], ['QM-E13'], ['MA13']],
               'Hyperspace': [['QM-E27'], ['MA13'], ['ES07', 'ES15', 'QM-E05'], ['MA19']],
               'Tachyonic': [['QM-E17'], ['QM-E27'], ['ES07', 'ES15', 'QM-E05'], ['SE02'], ['TH20']],
               'Plenum': [['QM-E27'], ['MS02'], ['QM-E19'], ['QM-E23'], ['AE20']]},
        PROPOSER={'Warp': 'RC01', 'Wormhole': 'RC01', 'Tachyonic': 'RC01', 'Hyperspace': 'MA13', 'Plenum': 'QM-E04'},
        QUESTION={'exotic': 'Exotic matter holds', 'strata': 'Higher strata or a higher-order cycle exist', 'bubble': 'The bubble of shaped Aether holds',
                  'closed': 'Closed circuits of the medium are stable', 'throat': 'The throat is stable', 'leak': 'Leakage into the strata shows they are open',
                  'dark': 'Dark matter is a hidden sector', 'superlum': 'The medium carries a superluminal mode',
                  'catalogue': 'The catalogue contains a superluminal form', 'currents': 'The currents run faster than light',
                  'coupling': 'The currents can be ridden'},
        ok='strata or not leak'),
}
for ont in FTL:
    if 'w' in LEVERS: FTL[ont]['BUILD']['Wormhole'].append(['MS17'])   # Wormhole's engineering row outside its tests
FTL['atomic']['BUILD']['Tachyonic'] = [g for g in FTL['atomic']['BUILD']['Tachyonic'] if not ('y' in LEVERS and g == ['NP11'])]
INSTR = {'coherence': ['CP21'], 'leak': ['RC11'], 'dark': ['RC05', 'RC06'], 'tachDE': ['RC05', 'RC06'], 'superlum': ['RC05', 'RC06'], 'tachyon': ['QP15'],
         'catalogue': ['QM-E28']}
INSTRUMENT = {'coherence': 'Orbital Quantum Laboratory', 'leak': 'Space Interferometer', 'dark': 'Survey Telescope', 'tachDE': 'Survey Telescope',
              'superlum': 'Survey Telescope', 'tachyon': 'Very Large Particle Collider', 'catalogue': 'Very Large Boundary Furnace'}
for ont, F in FTL.items():
    VARS = sorted(F['HOST'])
    ok = F.pop('ok')
    F['TRUTHS'] = {m: [a for a in (dict(zip(VARS, b)) for b in itertools.product([0, 1], repeat=len(VARS))) if eval(ok, {}, a)
                       and all(a[c] for c in F['COND'][m]) and all(not all(a[c] for c in F['COND'][o]) for o in F['COND'] if o != m)]
                   for m in F['COND']}
    F['VARS'] = VARS

# ---- worlds ----------------------------------------------------------------------------------------------------------
WORLDS = {'familiar': (None, 'atomic'), 'Process': ('Process', 'elemental'), 'Substance': ('Substance', 'elemental')}
rows_out, worlds_out = {}, {}
for wname, (alt, ont) in WORLDS.items():
    rows = W.set_world(alt); HF.ROWS = rows; HF.IDS = sorted(rows); HF.FOCUS = {k: rows[k]['focus'] for k in HF.IDS}
    HF.ERA_I = {k: EO.index(rows[k]['era']) for k in HF.IDS}
    prices.apply(HF, rows)
    for k in rows:
        if k not in rows_out:
            r = rows[k]
            rows_out[k] = dict(name=NAMES.get(k, k), focus=r['focus'], tier=r['tier'], era=r['era'], pre=r['pre'], world=r['world'],
                               prereq=re.sub(r'\s+', ' ', R.rows[k][4]).strip(), **effect_text(k))
    pool = json.load(open(os.path.join(POWER, 'results', f"w7f_{wname}_pool{env.get('POOLTAG', '')}.json")))
    ids = sorted(rows)
    worlds_out[wname] = dict(ontology=ont, ids=ids, costmult={k: HF.COSTMULT[k] for k in ids if HF.COSTMULT.get(k, 1.0) != 1.0},
                             compete=dict(HF.COMPETE), tiers={k: rows[k]['tier'] for k in ids if rows[k]['tier'] != rows_out[k]['tier']},
                             pool=[dict(m=g['m'], t=[g['t'].get(k) for k in ids]) for g in pool])

# ---- the economy turn by turn, as the harness accumulates it (RUN_ON: past the last era at its income) -------------------
def tables(econ, n=900):
    cum, inc_l, d_l, cum_l = 0.0, [0.0], [0.0], [0.0]
    for _ in range(n):
        inc = H0.income(cum) * econ
        cum += inc
        inc_l.append(inc); d_l.append(HF.dev_at(cum)); cum_l.append(cum)
    return dict(inc=inc_l, d=d_l)
ECON = {'1.0': tables(1.0), '0.8': tables(0.8)}
DRIVE = {e: {'exotic': [None] + [V.drive_turns(t, float(e), True) for t in range(1, 700)],
             'plain': [None] + [V.drive_turns(t, float(e), False) for t in range(1, 700)]} for e in ECON}

bundle = dict(
    version=VERSION, eras=EO, foci=FOCI, rows=rows_out, worlds=worlds_out,
    model=dict(target=dict(HF.TARGET), price=dict(HF.PRICE), turns=dict(HF.TURNS), win_turns=HF.WIN_TURNS, scale=P.scale, premium=P.premium,
               shape=P.shape, momentum=P.momentum, window=P.window, grace=P.grace, compress=P.compress, spread_floor=P.spread_floor,
               rediscover=P.rediscover, rediscover_tiers=list(P.rediscover_tiers), tier_attention=P.tier_attention, routing=P.routing, model=P.model,
               glimpse={'STANDARD': float(env.get('GLIMPSE', '0.1')), 'UNCOMMON': float(env.get('GLIMPSEU', '0.03')), 'RARE': 0.0, 'UNIQUE': 0.0},
               diff_wait=10, diff_wait_net=5, diff_share=0.5, contact_era='Early Modern', end_mult=2.0, w16=env.get('W16', '1') == '1'),
    economy=ECON, ftl=dict(FTL, INSTR=INSTR, INSTRUMENT=INSTRUMENT, OPENS='RC01', INSTR_D={'1.0': 5, '0.8': 6}),
    victory=dict(protox=V.PROTOX, p_space=V.P_SPACE, scale=V.SCALE, spaceprice=V.SPACEPRICE, space=V.SPACE, drive=DRIVE,
                 exotic=sorted(V.EXOTIC), drive_cost=V.DRIVE_COST),
    settings={k: env.get(k) for k in ('LEVERS', 'WROWX', 'REDISCOVER', 'ENDUNOCC', 'W16', 'DEVENDS', 'WINTURNS', 'ERAPRICE', 'MODERNPRICE',
                                       'ATOMICPRICE', 'SPACEPRICE', 'POOLTAG', 'COMPETE')},
)
out = os.path.join(HERE, 'bundle.json')
json.dump(bundle, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'{out}: {VERSION}, {len(rows_out)} rows, worlds {list(worlds_out)}, {os.path.getsize(out) / 1e6:.2f} MB')
