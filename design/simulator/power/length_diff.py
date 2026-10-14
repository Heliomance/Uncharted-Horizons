"""Why methods and ontologies differ in length. Reads results/w7f_<world>_ALL.json (full records, truth; instruments at D turns).
For each game: the answer that completed certainty (and whether an instrument was the delay), and the build requirement that finished last."""
import sys, json, statistics as st, collections
D = 5; R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
A = dict(HOST={'exotic': ['QP11'], 'extradim': ['QP09', 'QP10'], 'discrete': ['QP09', 'QP10'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'], 'leak': ['RC11'], 'dark': ['RC05'], 'coherence': ['CP21'], 'hartman': ['QP14'], 'tachDE': ['RC06'], 'tachyon': ['QP06']},
         COND={'Warp': ['exotic', 'extradim', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['extradim', 'leak', 'dark'], 'Tunnelling': ['coherence', 'discrete', 'hartman'], 'Tachyonic': ['tachDE', 'closed', 'tachyon']},
         INSTR={'coherence': ['CP21'], 'leak': ['RC11'], 'dark': ['RC05', 'RC06'], 'tachDE': ['RC05', 'RC06']}, CLOSE='QP08',
         BUILD={'Warp': [['RC02'], ['QP08'], ['QP11'], ['MS08'], ['ES06', 'ES07', 'ES14', 'ES08'], ['ES18']], 'Wormhole': [['RC02'], ['QP08'], ['QP11'], ['MS08'], ['RC04'], ['QP12'], ['MA13']],
                'Hyperspace': [['QP08'], ['MA13'], ['ES06', 'ES07', 'ES14', 'ES08'], ['MA19']], 'Tunnelling': [['QP02'], ['CP10'], ['MS02', 'GN05'], ['QP14'], ['CP21']],
                'Tachyonic': [['QP06'], ['QP08'], ['NP11'], ['SE02'], ['ES06', 'ES07', 'ES14', 'ES08'], ['NP15']]})
E = dict(HOST={'exotic': ['QM-E06'], 'strata': ['QM-E12'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'], 'leak': ['RC11'], 'dark': ['RC05'], 'superlum': ['RC06'], 'catalogue': ['QM-E17'], 'currents': ['QM-E19'], 'coupling': ['AE20']},
         COND={'Warp': ['exotic', 'strata', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['strata', 'leak', 'dark'], 'Tachyonic': ['superlum', 'closed', 'catalogue'], 'Plenum': ['currents', 'superlum', 'coupling']},
         INSTR={'leak': ['RC11'], 'dark': ['RC05', 'RC06'], 'superlum': ['RC05', 'RC06']}, CLOSE='QM-E27',
         BUILD={'Warp': [['RC02'], ['QM-E27'], ['QM-E06'], ['MS08'], ['ES07', 'ES15', 'QM-E05'], ['ES18']], 'Wormhole': [['RC02'], ['QM-E27'], ['QM-E06'], ['MS08'], ['RC04'], ['QM-E13'], ['MA13']],
                'Hyperspace': [['QM-E27'], ['MA13'], ['ES07', 'ES15', 'QM-E05'], ['MA19']], 'Tachyonic': [['QM-E17'], ['QM-E27'], ['ES07', 'ES15', 'QM-E05'], ['SE02'], ['TH20']],
                'Plenum': [['QM-E27'], ['MS02'], ['QM-E19'], ['QM-E23'], ['AE20']]})
md = lambda x: st.median(x) if x else float('nan')
stats = collections.defaultdict(lambda: collections.defaultdict(list)); last_ans = collections.defaultdict(collections.Counter); last_build = collections.defaultdict(collections.Counter)
over = collections.defaultdict(list); host_wait = collections.defaultdict(list)
for w in ('familiar', 'Substance', 'Process'):
    O = A if w == 'familiar' else E; ont = 'atomic' if w == 'familiar' else 'elemental'
    for g in json.load(open(f'{R}w7f_{w}_ALL.json')):
        if not (g['cert'] and g['built'] and g['t']): continue
        t, a, m, K, C, B = g['t'], g['truth'], g['m'], g['close'], g['cert'], g['built']
        key = (ont, m); S = stats[key]
        S['theory'].append(C - K); S['eng'].append(max(0, B - C)); S['victory'].append(max(C, B) + 9 - g['space'])
        res = {}; via = {}
        for c, hosts in O['HOST'].items():
            hs = [t[h] for h in hosts if h in t]
            if not hs or (hosts == ['MS08'] and not a['exotic']): continue
            r0 = min(hs); r = r0
            if c in O['INSTR']: r = max(r0, min(t[u] for u in O['INSTR'][c] if u in t) + D)
            res[c] = r; via[c] = 'instrument' if r > r0 else 'discovery'
        done = [c for c, r in res.items() if r == C]
        for c in (done or ['the unified theory']):
            last_ans[key][f"{c} ({via.get(c, '')})" if c in via else c] += 1
            if c in res: host_wait[(ont, c)].append(min(t[h] for h in O['HOST'][c] if h in t) - K)
        gt = {'/'.join(gr): min(t.get(o, 10 ** 6) for o in gr) for gr in O['BUILD'][m]}
        lg = max(gt, key=gt.get)
        if gt[lg] > C: last_build[key][lg] += 1; over[key].append(gt[lg] - C)
        else: last_build[key]['(built before certainty)'] += 1
print("Median turns: theory (unified theory to certainty), engineering after certainty, victory (from the Space era opening)")
for key in sorted(stats):
    S = stats[key]; n = len(S['theory'])
    print(f"\n{key[0]:9} {key[1]:11} n={n:<3} theory {md(S['theory']):>4.0f}  engineering after certainty {md(S['eng']):>3.0f}  victory {md(S['victory']):>4.0f}")
    print(f"   certainty completed by: {', '.join(f'{c} {k/n:.0%}' for c, k in last_ans[key].most_common(4))}")
    print(f"   build finished last: {', '.join(f'{c} {k/n:.0%}' for c, k in last_build[key].most_common(4))};"
          f" when after certainty, by a median of {md(over[key]):.0f} turns")
print("\nHost discovered, turns after the unified theory (median), by ontology and condition:")
for ont in ('atomic', 'elemental'):
    print(f"   {ont:9}: " + ', '.join(f"{c} {md(v):.0f}" for (o, c), v in sorted(host_wait.items()) if o == ont))
