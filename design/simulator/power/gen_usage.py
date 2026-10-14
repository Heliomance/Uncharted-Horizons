"""What a civilisation NOT chasing FTL ends up with in the Space era, once every agreed field has a Space-era pool (assumed sizes).
Reads results/w7f_<world>_<tag>.json (generalist, full records). Run inside scratch_run.sh with LEVERS including q and z."""
import sys, json, collections, statistics as st; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import worlds as WD
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
FTL = {'Computing', 'Energy Systems', 'Materials Science', 'Mathematics', 'Nuclear Physics', 'Thermodynamics', 'Aeronautics', 'Quantum Physics', 'Relativity & Cosmology', 'Quintessic Physics', 'Rocketry', 'Space Engineering'}
SETS = [a.split(':') for a in sys.argv[1:]] or [['GEN', '300', 'good economy, by turn 300'], ['GENA', '380', 'average economy, by turn 380']]
for tag, T, lab in SETS:
    T = int(T); eras = collections.Counter(); cycled = []
    per_field = collections.defaultdict(list); totals, n1, n3, n5, ftl_share, starts, space_rows = [], [], [], [], [], [], collections.Counter()
    for w in ('familiar', 'Substance', 'Process'):
        rows = WD.set_world(None if w == 'familiar' else w)
        sp_fields = {r['focus'] for r in rows.values() if r['era'] == 'Space'}
        for f in sp_fields: space_rows[f] = max(space_rows[f], sum(1 for r in rows.values() if r['era'] == 'Space' and r['focus'] == f))
        for g in json.load(open(f'{R}w7f_{w}_{tag}.json')):
            t = g['t']; got = collections.Counter(rows[k]['focus'] for k, v in t.items() if k in rows and rows[k]['era'] == 'Space' and v <= T)
            for f in sp_fields: per_field[f].append(got[f])
            tot = sum(got.values()); totals.append(tot); n1.append(sum(1 for v in got.values() if v >= 1)); n3.append(sum(1 for v in got.values() if v >= 3)); n5.append(sum(1 for v in got.values() if v >= 5))
            ftl_share.append(sum(v for f, v in got.items() if f in FTL) / tot if tot else 0)
            starts.append(g['space'] if g['space'] else T)
            S0 = g['space'] or T
            for k, v in t.items():
                if k in rows and S0 <= v <= T: eras[rows[k]['era']] += 1
            if g.get('seq'): cycled.append(len({f for tt, f in g['seq'] if tt <= T}))
    md = st.median
    print(f"\n== Generalist, {lab}: Space era opens at a median turn {md(starts):.0f}")
    print(f"   Space-era breakthroughs: median {md(totals):.0f} (middle half {st.quantiles(totals, n=4)[0]:.0f}–{st.quantiles(totals, n=4)[2]:.0f}), "
          f"{md(ftl_share):.0%} of them in FTL-related fields")
    ng = len(totals)
    print('   all breakthroughs per game from the Space era opening, by era: ' + ', '.join(f'{e} {eras[e] / ng:.1f}' for e in ('Early Modern', 'Modern', 'Atomic', 'Space') if eras[e]) + (f'; fields funded over the whole game: median {md(cycled):.0f}' if cycled else ''))
    print(f"   fields with at least 1 / 3 / 5 Space-era breakthroughs: {md(n1):.0f} / {md(n3):.0f} / {md(n5):.0f}  (of {len(per_field)} fields with Space-era content)")
    print("   per field, mean breakthroughs (of rows available):")
    for f, v in sorted(per_field.items(), key=lambda kv: -st.mean(kv[1]))[:12]:
        print(f"      {f:26} {st.mean(v):>4.1f} of {space_rows[f]:>2}  {'(FTL)' if f in FTL else ''}")
