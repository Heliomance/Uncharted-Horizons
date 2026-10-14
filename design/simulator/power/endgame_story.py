"""How the FTL endgame plays, from the player's side: replays each game in results/w7f_<world>_<tag>.json (needs SAVE_T=1 and truth),
reconstructing when each FTL answer arrives (instruments included), how many methods remain possible, the rhythm of discoveries,
and where Endeavours, diffusion and the build fall. Usage: endgame_story.py <tag> <instrument turns>"""
import sys, json, re, statistics as st, collections
from defaults import TREE   # the design document (or a run's patched copy)
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'; TAG = sys.argv[1]; D = int(sys.argv[2])
ERA = {}
for l in open(TREE, encoding='utf-8'):
    m = re.match(r'^\| ([A-Z]{2,3}(?:-[A-Z]+)?\d+[A-Z]?) \| \*\*[^*]+\*\* \| [A-Z]+ \| ([A-Za-z ]+) \|', l)
    if m: ERA.setdefault(m.group(1), m.group(2).strip())
for k in ('RC11', 'CP16', 'CP21', 'AE14', 'AE20', 'ES22', 'ES18', 'MA15', 'MA19', 'NP15', 'TH20'): ERA[k] = 'Space'
A = dict(HOST={'exotic': ['QP11'], 'extradim': ['QP09', 'QP10'], 'discrete': ['QP09', 'QP10'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'],
              'leak': ['RC11'], 'dark': ['RC05'], 'coherence': ['CP21'], 'hartman': ['QP14'], 'tachDE': ['RC06'], 'tachyon': ['QP06']},
         COND={'Warp': ['exotic', 'extradim', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['extradim', 'leak', 'dark'],
               'Tunnelling': ['coherence', 'discrete', 'hartman'], 'Tachyonic': ['tachDE', 'closed', 'tachyon']},
         INSTR={'coherence': ['CP21'], 'leak': ['RC11'], 'dark': ['RC05', 'RC06'], 'tachDE': ['RC05', 'RC06']}, CLOSE='QP08')
E = dict(HOST={'exotic': ['QM-E06'], 'strata': ['QM-E12'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'], 'leak': ['RC11'], 'dark': ['RC05'],
              'superlum': ['RC06'], 'catalogue': ['QM-E17'], 'currents': ['QM-E19'], 'coupling': ['AE20']},
         COND={'Warp': ['exotic', 'strata', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['strata', 'leak', 'dark'],
               'Tachyonic': ['superlum', 'closed', 'catalogue'], 'Plenum': ['currents', 'superlum', 'coupling']},
         INSTR={'leak': ['RC11'], 'dark': ['RC05', 'RC06'], 'superlum': ['RC05', 'RC06']}, CLOSE='QM-E27')
md = lambda x: st.median(x) if x else float('nan')
def iqr(x): q = st.quantiles(x, n=4) if len(x) >= 4 else [float('nan')] * 3; return f"{q[0]:.0f}–{q[2]:.0f}"
G = collections.defaultdict(list); per_m = collections.defaultdict(list); example = None
for w in ('familiar', 'Substance', 'Process'):
    O = A if w == 'familiar' else E
    for g in json.load(open(f'{R}w7f_{w}_{TAG}.json')):
        if not (g['cert'] and g['built'] and g['t']): G['cannot win'].append(1); continue
        t, a, S, K, C = g['t'], g['truth'], g['space'], g['close'], g['cert']; V = max(C, g['built']) + 9
        res = {}
        for c, hosts in O['HOST'].items():
            hs = [t[h] for h in hosts if h in t]
            if not hs or (hosts == ['MS08'] and not a['exotic']): continue
            r = min(hs)
            if c in O['INSTR']: r = max(r, min(t[u] for u in O['INSTR'][c] if u in t) + D)
            res[c] = r
        def alive(x): return [m for m, cs in O['COND'].items() if not any(c in res and res[c] <= x and not a[c] for c in cs)]
        news = sorted(r for r in res.values() if r <= C)
        after = [r for r in news if r >= K]
        gaps = [b - a_ for a_, b in zip([K] + after, after + [C])]
        two = next((x for x in range(K, C + 1) if len(alive(x)) <= 2), C)
        first_out = next((x for x in range(S, C + 1) if len(alive(x)) < len(O['COND'])), C)
        disc = collections.Counter(v for k, v in t.items() if S <= v <= V)
        dry = max((b - a_ - 1 for a_, b in zip(sorted(disc), sorted(disc)[1:])), default=0)
        fin = [e for e in g['ends'] if e[2] == 'done']; dif = [d_ for d_ in g['diffs'] if S <= d_[0] <= V]
        inst = len({tuple(O['INSTR'][c]) for c in O['INSTR'] if any(u in t and t[u] <= V for u in O['INSTR'][c])})
        rec = dict(w=w, m=g['m'], pre=K - S, theory=C - K, eng=max(0, g['built'] - C), V=V - S, news=len(news), news_after=len(after), silence=max(gaps),
                   to_two=two - K, two_to_cert=C - two, first_out=first_out - S, per_turn=sum(disc.values()) / (V - S + 1), dry=dry,
                   end_th=sum(1 for e in fin if e[0] <= C), end_en=sum(1 for e in fin if e[0] > C), diff=len(dif), inst=inst, alive_K=len(alive(K)))
        for k_, v in rec.items():
            if k_ not in ('w', 'm'): G[k_].append(v)
        per_m[(w, g['m'])].append(rec)
        if example is None and w == 'familiar' and abs(rec['V'] - 42) <= 1 and abs(rec['theory'] - 18) <= 2:
            example = (g, rec, res, O)
n = len(G['V'])
print(f"All agreed rules together (connected; Endeavours 2x with the glimpse; no observation; instruments {D} turns; smarter player). {n} winnable games, {len(G['cannot win'])} not.")
rows = [('Space era opens to unified theory', 'pre'), ('Unified theory to certainty (theory)', 'theory'), ('Certainty to build complete (engineering)', 'eng'),
        ('Space era opens to victory (incl. 9-turn prototype)', 'V'), ('FTL answers received by certainty', 'news'), ('…of which after the unified theory', 'news_after'),
        ('Longest silence between answers in the theory phase', 'silence'), ('Unified theory until two methods remain', 'to_two'), ('Two methods remain until certainty', 'two_to_cert'),
        ('Methods still possible at the unified theory', 'alive_K'), ('Space era opens to first method ruled out', 'first_out'), ('Discoveries per turn, Space era to victory', 'per_turn'),
        ('Longest run of turns with no discovery', 'dry'), ('Endeavours completed during theory', 'end_th'), ('Endeavours completed during engineering', 'end_en'),
        ('Breakthroughs arriving by diffusion in the Space era', 'diff'), ('Instruments built', 'inst')]
for lab, k in rows: print(f"   {lab:58} median {md(G[k]):>5.1f}   middle half {iqr(G[k])}")
print("By world and method: theory / victory medians (turns)")
for (w, m), rs in sorted(per_m.items()): print(f"   {w:9} {m:11} theory {md([r['theory'] for r in rs]):>4.0f}   victory {md([r['V'] for r in rs]):>4.0f}   answers {md([r['news'] for r in rs]):>3.0f}")
if example:
    g, rec, res, O = example; t = g['t']; S = g['space']
    print(f"\nA typical game (atomic, {g['m']} is the working method): turns counted from the Space era opening")
    ev = [(t[O['CLOSE']] - S, 'the unified theory')] + [(r - S, f"answer: {c} {'holds' if g['truth'][c] else 'fails'}") for c, r in res.items() if r <= g['cert']]
    ev += [(e[0] - S, f"Endeavour completes: {e[1]}") for e in g['ends'] if e[2] == 'done'] + [(g['cert'] - S, 'CERTAIN'), (g['built'] - S, 'build complete'), (max(g['cert'], g['built']) + 9 - S, 'prototype flies: victory')]
    for x, s in sorted(ev): print(f"   turn {x:>3}: {s}")
