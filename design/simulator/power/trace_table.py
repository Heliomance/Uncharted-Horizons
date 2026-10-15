"""Turn-by-turn table of one traced game (w7f.py with TRACE=...). Usage: python3 trace_table.py <trace.json> <out.md> <seeds text>"""
import json, re, sys
from defaults import TREE   # the design document (or a run's patched copy)
T = json.load(open(sys.argv[1])); OUT = sys.argv[2]; SEEDS = sys.argv[3] if len(sys.argv) > 3 else ''
NAME = {}; ERA = {}
THRESH = {'Ancient': 5, 'Classical': 3, 'Medieval': 3, 'Early Modern': 5, 'Modern': 7, 'Atomic': 6, 'Space': 4}   # §2: N breakthroughs from that era or later
VERSION = ''   # the newest changelog entry, which names the document's version
for l in open(TREE, encoding='utf-8'):
    if not VERSION and (v := re.match(r'^### (v\d+\.\d+) ', l)): VERSION = v.group(1)
    m = re.match(r'^\| ([A-Z]{1,3}\d+[A-Z]?(?:-W)?|ME-B|NP-F\d+|QM-E\d+|MI05B|MI06B|[A-Z]{2}-[A-Z]\d+) \| \*\*(.+?)\*\* \| \S+ \| ([^|]+?) \|', l)
    if m: NAME[m.group(1)] = m.group(2); ERA[m.group(1)] = m.group(3).strip()
nm = lambda k: NAME.get(k, k)
EO = ['Primitive', 'Ancient', 'Classical', 'Medieval', 'Early Modern', 'Modern', 'Atomic', 'Space']
COND_WORDS = {'exotic': 'exotic matter holds', 'extradim': 'extra dimensions exist', 'bubble': 'the warp bubble is stable', 'closed': 'closed timelike curves are stable',
              'throat': 'the throat is stable', 'leak': 'gravitational leakage shows the dimensions are open', 'dark': 'dark matter is a hidden sector',
              'coherence': 'macro-scale coherence', 'discrete': 'spacetime is discrete', 'hartman': 'the Hartman effect', 'tachDE': 'dark energy is a tachyonic field',
              'tachyon': 'a tachyonic sector exists'}
METHODS = ['Warp', 'Wormhole', 'Hyperspace', 'Tunnelling', 'Tachyonic']
PROPOSER = {'Tachyonic': 'RC01', 'Warp': 'RC01', 'Wormhole': 'RC01', 'Hyperspace': 'MA13', 'Tunnelling': 'QP02'}
recs = T['records']; disc_turn = {}
for r in recs:
    for k in r['found']: disc_turn.setdefault(k, r['turn'])
opens = disc_turn.get('RC01')
prop_turn = {mm: max(opens, disc_turn[p]) for mm, p in PROPOSER.items() if opens and p in disc_turn}
CAUSE = {'core': 'CORE, prerequisites met', 'funded': 'idea occurred — funded field (bad-luck rule)', 'chance': 'idea occurred'}
FOC = T.get('focus', {}); spread_n = [0]
rows = []; prev_alive = None; prev_known = {}; cert_shown = False; have_eras = []
def civ_era():
    e = 'Primitive'
    for i, name in enumerate(EO):
        if name in THRESH and sum(1 for x in have_eras if EO.index(x) >= i) >= THRESH[name]: e = name
    return e
def reveal_groups(rec):
    g = {}
    for k, c in rec['occ']: g.setdefault(CAUSE[c], []).append(nm(k))
    if rec['glim']: g['glimpsed (proximity revelation)'] = [nm(k) for k in rec['glim']]
    return g
def fund_str(f):
    kind, x = f
    return f"Grand Endeavour: {nm(x)}" if kind == 'END' else (x or '—')
for r in recs:
    t = r['turn']; dev_era = EO[min(int(r['d']), len(EO) - 1)]
    have_eras += [ERA[k] for k in r['found'] if ERA.get(k) in EO]
    ce = civ_era(); era = ce if ce == dev_era else f"{ce} (development: {dev_era})"
    found = []
    kind_t, x_t = r['fund']   # what was funded during this turn (the previous row's end-of-turn choice)
    for k in r['found']:
        if k in r['diff']: mark = 'ᴰ'
        elif k in r['endv']: mark = 'ᴱ'
        elif kind_t == 'END' or FOC.get(k) != x_t: mark = f"ˢ ({FOC.get(k, '?')})"; spread_n[0] += 1
        else: mark = ''
        found.append(f"{nm(k)} [{ERA.get(k, '?')}]{mark}")
    i_r = recs.index(r); groups = reveal_groups(recs[i_r + 1]) if i_r + 1 < len(recs) else {}   # reveals belong to the end of this turn (the harness applies them as the next turn opens)
    hyp = [f"{mm} (proposed by {nm(PROPOSER[mm])})" for mm in METHODS if prop_turn.get(mm) == t]
    if hyp: groups['FTL hypothesis'] = hyp
    reveal = '; '.join(f"*{c}:* {', '.join(v)}" for c, v in groups.items())
    fund = fund_str(recs[i_r + 1]['fund']) if i_r + 1 < len(recs) else f"Grand Endeavour: {T['m']} prototype (begins)"   # set at the end of this turn
    al = T['alive'][str(t)]; known = al['known']
    proposed = [mm for mm in METHODS if prop_turn.get(mm) is not None and prop_turn[mm] <= t]
    ftl = ''
    if proposed:
        alive = [mm for mm in proposed if mm in al['alive']]
        ftl = ', '.join(alive)
        news = [f"{COND_WORDS[c]} {'✓' if v else '✗'}" for c, v in known.items() if c not in prev_known]
        out = [mm for mm in (prev_alive or []) if mm not in alive]
        if out: ftl += f" — ruled out: {', '.join(out)}"
        if news: ftl += f" — results: {'; '.join(news)}"
        if al['certain'] and not cert_shown: ftl += ' — **certain**'; cert_shown = True
        prev_alive = alive
    if T['close'] in r['found']: ftl = (ftl + ' — ' if ftl else '') + 'unified theory: the list of hypotheses is closed'
    prev_known = dict(known)
    rows.append((t, ', '.join(found), reveal, era, fund, ftl))
g0 = reveal_groups(recs[0]); rows.insert(0, ('Start', '', '; '.join(f"*{c}:* {', '.join(v)}" for c, v in g0.items()), 'Primitive', fund_str(recs[0]['fund']), ''))
last = recs[-1]['turn']; m = T['m']; exo = m in ('Warp', 'Wormhole', 'Plenum'); drive = 3 if exo else 4
ce_last = civ_era()
for i in range(1, 6): rows.append((last + i, f"{m} prototype — success (modelled)" if i == 5 else '', '', f"{ce_last} (development not simulated)", (f"Grand Endeavour: {m} prototype (modelled)" if i < 5 else '— (SS FTL Drive into production; research not simulated)'), f"{m} — certain"))
for i in range(1, drive + 1): rows.append((last + 5 + i, 'SS FTL Drive completed (modelled)' if i == drive else '', '', f"{ce_last} (development not simulated)", '— (SS FTL Drive in production; research not simulated)', f"{m} — certain"))
victory = last + 5 + drive + 1
rows.append((victory, 'Ship assembled and launched — **Science Victory** (modelled)', '', f"{ce_last} (development not simulated)", '—', f"{m} — certain"))
truth = T['truth']
holds = [COND_WORDS[c] for c, v in truth.items() if v]; fails = [COND_WORDS[c] for c, v in truth.items() if not v]
def first(pred): return next((r['turn'] for r in recs if pred(r)), None)
space1 = first(lambda r: any(k for k in r['found'] if k in NAME and EO[min(int(r['d']), 7)] == 'Space'))
answers = sorted({int(t_) for t_, a in T['alive'].items() if a['known']})
md = [f"# Turn-by-turn game: atomic world, Hyperspace viable (expert player)", "",
      f"Simulated by the FTL-endgame harness on the design document ({VERSION}) with the agreed full design; seeds {SEEDS}. "
      f"**World truth** (the FTL conditions, drawn at random under the generation rules with Hyperspace viable): holds — {'; '.join(holds)}. Fails — {'; '.join(fails)}. "
      "Frontier truths outside the FTL puzzle (fusion, vacuum energy, fossil fuels and the like) are not modelled by the harness, so they take their familiar values.", "",
      "**Player and world:** the expert (knows every method's conditions and builds; beelines the unified theory; hedges engineering across the methods still possible; uses Grand Endeavours at 2× by the fair rule; builds instruments at once, 5 turns each); a connected civilisation with five rivals replayed from other games of the same world, met in the Early Modern era (knowledge diffusion); proximity revelation at 10%; observational revelation off.", "",
      f"**Milestones:** unified theory (Quantum Gravity Theory) turn {disc_turn.get(T['close'])}; first FTL result turn {answers[0] if answers else '—'}; certainty turn {T['cert'][0] if T['cert'] else '—'}; build complete turn {last}; "
      f"prototype turns {last + 1}–{last + 5}; SS FTL Drive turns {last + 6}–{last + 5 + drive}; **launch and Science Victory turn {victory}**. "
      f"{sum(len(r['found']) for r in recs)} breakthroughs discovered ({sum(len(r['diff']) for r in recs)} by diffusion, {spread_n[0]} from foci not being funded); Grand Endeavours: "
      + ', '.join(f"{nm(k)} (turns {s}–{d})" for (s, k, a1), (d, k2, a2) in zip([e for e in T['ends'] if e[2] == 'start'], [e for e in T['ends'] if e[2] in ('done', 'dropped')])) + ".", "",
      "**Reading the table.** *Discovered:* each breakthrough's own era in brackets; ᴰ = arrived by knowledge diffusion; ᴱ = completed as a Grand Endeavour; ˢ = found in a focus that was not being funded that turn (the spread of Insight across every open focus, or Insight spilling over from a focus with nothing left to research), with that focus named. *Revealed:* what became known at the end of this turn and why (the same moment the focus is set, so a CORE breakthrough appears on the turn its last prerequisite is gained; *Start* shows what is known before turn 1) — a CORE breakthrough is known as soon as its prerequisites are met; a non-CORE idea *occurs* by chance while its moment lasts (or at once in a funded field in the Space era, the bad-luck rule); a glimpse reveals an idea that did not occur (it can then be pursued as an Endeavour); FTL hypotheses are proposed by their theory rows once Special Relativity opens the puzzle. *Era* is the civilisation's era by §2's rule (it enters an era on discovering enough breakthroughs from that era or later — 4 for the Space era), with its *development* (cumulative Insight, which sets prices) in brackets where it lags: research ahead of development costs ×4 per era. *Funded:* the focus set at the end of the turn, after its discoveries — the one that receives the active share next turn (the rest spreads across every open focus) — or the Grand Endeavour committed to. *FTL methods alive:* hypotheses proposed and not yet ruled out, with each result on the turn it arrives (✓ holds, ✗ fails); results from measurement tests arrive when their instrument is built. Turns after the build are modelled from the agreed timings (prototype 5 turns, Drive 4, launch 1), since the harness stops when certainty and the build are both complete.", "",
      "| Turn | Breakthroughs discovered | Breakthroughs revealed (and what revealed them) | Era | Funded | FTL methods alive |", "|---|---|---|---|---|---|"]
for t, f, rv, era, fund, ftl in rows:
    md.append(f"| {t} | {f} | {rv} | {era} | {fund} | {ftl} |")
open(OUT, 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print(f"written {OUT}: {len(rows)} rows; victory turn {victory}; unnamed codes: {sorted({k for r in recs for k in r['found'] if k not in NAME})}")
