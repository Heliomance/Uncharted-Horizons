"""The theory phase (unified theory to certainty) as each benchmark player experiences it, on the round-two balance.
Reads results/w7f_<world>_<tag>.json with full records (SAVE_T=1) and world truth; instruments delay their answers by D turns."""
import json, statistics as st, collections
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
A = dict(HOST={'exotic': ['QP11'], 'extradim': ['QP09', 'QP10'], 'discrete': ['QP09', 'QP10'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'], 'leak': ['RC11'], 'dark': ['RC05'], 'coherence': ['CP21'], 'hartman': ['QP14'], 'tachDE': ['RC06'], 'tachyon': ['QP06']},
         COND={'Warp': ['exotic', 'extradim', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['extradim', 'leak', 'dark'], 'Tunnelling': ['coherence', 'discrete', 'hartman'], 'Tachyonic': ['tachDE', 'closed', 'tachyon']},
         INSTR={'coherence': ['CP21'], 'leak': ['RC11'], 'dark': ['RC05', 'RC06'], 'tachDE': ['RC05', 'RC06']})
E = dict(HOST={'exotic': ['QM-E06'], 'strata': ['QM-E12'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'], 'leak': ['RC11'], 'dark': ['RC05'], 'superlum': ['RC06'], 'catalogue': ['QM-E17'], 'currents': ['QM-E19'], 'coupling': ['AE20']},
         COND={'Warp': ['exotic', 'strata', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['strata', 'leak', 'dark'], 'Tachyonic': ['superlum', 'closed', 'catalogue'], 'Plenum': ['currents', 'superlum', 'coupling']},
         INSTR={'leak': ['RC11'], 'dark': ['RC05', 'RC06'], 'superlum': ['RC05', 'RC06']})
import sys
PLAYERS = [(a.split(':')[0], a.split(':')[1], int(a.split(':')[2]), int(a.split(':')[3])) for a in sys.argv[1:]] or [('expert', 'TPX', 5, 9), ('novice', 'TPN', 5, 9), ('average', 'TPA', 6, 11)]
DRIVE = {9: 4, 5: 4, 11: 5, 6: 5}; EXO = {'Warp', 'Wormhole', 'Plenum'}
md = lambda x: st.median(x)
def iqr(x): q = st.quantiles(x, n=4); return f"{q[0]:.0f}–{q[2]:.0f}"
print("The theory phase on the round-two balance: 300 games per player (20 per method and world). Turns counted from the unified theory.")
rows = [('Unified theory, game turn', 'U'), ('Theory phase: unified theory to certainty', 'T'), ('Unified theory to victory', 'E'), ('Theory as a share of that stretch', 'share'),
        ('First answer arrives', 'first'), ('First method ruled out', 'out1'), ('Two methods left', 'two'), ('Two left until certainty', 'gap2'),
        ('Answers during the theory phase', 'n'), ('Victory with the ship, game turn', 'vic'), ('Longest silence between answers', 'sil'), ('Theory within 15 turns (share of games)', 'le15'), ('Theory within a third of the stretch (share)', 'third')]
res = {}
for lab, tag, D, proto in PLAYERS:
    S = collections.defaultdict(list); perw = collections.defaultdict(list)
    for w in ('familiar', 'Substance', 'Process'):
        O = A if w == 'familiar' else E
        for g in json.load(open(f'{R}w7f_{w}_{tag}.json')):
            if not (g['cert'] and g['built'] and g['t']): continue
            t, a, U, C = g['t'], g['truth'], g['close'], g['cert']; V = max(C, g['built']) + proto
            res_t = {}
            for c, hosts in O['HOST'].items():
                hs = [t[h] for h in hosts if h in t]
                if not hs or (hosts == ['MS08'] and not a['exotic']): continue
                r = min(hs)
                if c in O['INSTR']: r = max(r, min(t[u] for u in O['INSTR'][c] if u in t) + D)
                res_t[c] = r
            alive = lambda x: sum(1 for m, cs in O['COND'].items() if not any(c in res_t and res_t[c] <= x and not a[c] for c in cs))
            ans = sorted(r for r in res_t.values() if U <= r <= C)
            gaps = [b - a_ for a_, b in zip([U] + ans, ans + [C])]
            out1 = next((x for x in range(U, C + 1) if alive(x) < 5), C); two = next((x for x in range(U, C + 1) if alive(x) <= 2), C)
            T = C - U; Ev = V - U; Vs = max(C, g['built']) + proto + (DRIVE.get(proto, 4) - (1 if g['m'] in EXO else 0)) + 1
            for k, v in (('U', U), ('T', T), ('E', Ev), ('share', T / Ev if Ev else 1), ('first', (ans[0] - U) if ans else T), ('out1', out1 - U), ('two', two - U), ('gap2', C - two),
                         ('n', len(ans)), ('sil', max(gaps)), ('vic', Vs), ('le15', 1.0 if T <= 15 else 0.0), ('third', 1.0 if Ev and T / Ev <= 1 / 3 else 0.0)):
                S[k].append(v)
            perw[w].append(T)
    res[lab] = (S, perw)
print(f"{'':48}" + ''.join(f"{lab:>18}" for lab, *_ in PLAYERS))
for name, k in rows:
    cells = []
    for lab, *_ in PLAYERS:
        v = res[lab][0][k]
        cells.append(f"{st.mean(v):.0%}" if k in ('le15', 'third') else (f"{md(v):.0%}" if k == 'share' else f"{md(v):.0f} ({iqr(v)})"))
    print(f"{name:48}" + ''.join(f"{c:>18}" for c in cells))
print("Theory phase by world (median turns): " + '; '.join(f"{lab}: " + ', '.join(f"{w[:3]} {md(res[lab][1][w]):.0f}" for w in ('familiar', 'Substance', 'Process')) for lab, *_ in PLAYERS))
