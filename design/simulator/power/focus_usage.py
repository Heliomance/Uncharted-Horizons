"""How many breakthroughs from each field players end up with, by method and world (round-two balance, full records).
Windows: the investigation (unified theory to certainty) and after certainty (certainty to build complete). Signature fields from W18.
Run inside scratch_run.sh with the round-two LEVERS, so fields come from the patched tree."""
import sys, json, collections, statistics as st; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import worlds as WD
FOC = {w: {k: r['focus'] for k, r in WD.set_world(None if w == 'familiar' else w).items()} for w in ('familiar', 'Substance', 'Process')}   # each world's own rows
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
SIG = {('familiar', 'Warp'): 'Energy Systems', ('familiar', 'Wormhole'): 'Materials Science', ('familiar', 'Hyperspace'): 'Mathematics', ('familiar', 'Tunnelling'): 'Computing', ('familiar', 'Tachyonic'): 'Nuclear Physics'}
for w in ('Substance', 'Process'):
    SIG.update({(w, 'Warp'): 'Energy Systems', (w, 'Wormhole'): 'Materials Science', (w, 'Hyperspace'): 'Mathematics', (w, 'Tachyonic'): 'Thermodynamics', (w, 'Plenum'): 'Aeronautics'})
NAME = {'familiar': 'atomic', 'Substance': 'Substance', 'Process': 'Process'}
SUF = sys.argv[1] if len(sys.argv) > 1 else ''
for lab, tag in (('expert', 'TPX' + SUF), ('novice', 'TPN' + SUF), ('average', 'TPA' + SUF)):
    cnt = {}   # (world, method) -> {'inv': [Counter per game], 'post': [...]}
    for w in ('familiar', 'Substance', 'Process'):
        for g in json.load(open(f'{R}w7f_{w}_{tag}.json')):
            if not (g['cert'] and g['built'] and g['t']): continue
            U, C, B = g['close'], g['cert'], g['built']; d = cnt.setdefault((w, g['m']), {'inv': [], 'post': [], 'all': []})
            d['inv'].append(collections.Counter(FOC[w].get(k, '?') for k, v in g['t'].items() if U < v <= C))
            d['post'].append(collections.Counter(FOC[w].get(k, '?') for k, v in g['t'].items() if C < v <= B))
            d['all'].append(collections.Counter(FOC[w].get(k, '?') for k, v in g['t'].items() if U < v <= B))
    mean = lambda cs, f: st.mean([c[f] for c in cs]) if cs else 0
    print(f"\n== {lab.upper()}: breakthroughs per game. sig = the method's signature field, own games vs the other methods' games in the same world")
    print(f"   {'':20} {'investigation':>13} {'after cert.':>11} | {'signature field':18} {'own':>4} {'others':>6} | {'mix differs from others':>23} | top fields, whole endgame")
    lifts, tvds = [], []
    for (w, m), d in sorted(cnt.items()):
        f = SIG[(w, m)]; others = [x for (w2, m2), dd in cnt.items() if w2 == w and m2 != m for x in dd['all']]
        own_sig = mean(d['all'], f); oth_sig = mean(others, f); lifts.append(own_sig - oth_sig)
        tot_own = collections.Counter(); [tot_own.update(c) for c in d['all']]; tot_oth = collections.Counter(); [tot_oth.update(c) for c in others]
        so, sx = sum(tot_own.values()), sum(tot_oth.values()); fields = set(tot_own) | set(tot_oth)
        tvd = 0.5 * sum(abs(tot_own[x] / so - tot_oth[x] / sx) for x in fields); tvds.append(tvd)
        top = ', '.join(f"{x} {tot_own[x] / len(d['all']):.1f}" for x, _ in tot_own.most_common(3))
        print(f"   {NAME[w]:9} {m:10} {st.mean([sum(c.values()) for c in d['inv']]):>13.1f} {st.mean([sum(c.values()) for c in d['post']]):>11.1f} | {f:18} {own_sig:>4.1f} {oth_sig:>6.1f} | {tvd:>23.0%} | {top}")
    print(f"   average: signature field +{st.mean(lifts):.1f} breakthroughs over other methods' games; mixes differ by {st.mean(tvds):.0%} on average")
