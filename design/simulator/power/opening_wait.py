"""What the first FTL answers wait on after the unified theory (full design, baseline records). For each game: the first answer's
host row, then its binding prerequisite chain back to the unified theory -- the groundwork discovered after the theory. Run inside
scratch_run.sh with the full design's LEVERS (fields and prerequisites from the patched tree)."""
import sys, json, collections, statistics as st; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import worlds as WD, gen_data as G
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
HOSTS = {'familiar': {'QP11': 'exotic matter', 'QP09': 'extra dimensions', 'QP10': 'discreteness', 'MS08': 'bubble/throat', 'RC07': 'closed curves', 'RC11': 'leakage', 'RC05': 'dark matter', 'CP21': 'coherence', 'QP14': 'Hartman effect', 'RC06': 'dark energy', 'QP06': 'tachyonic sector'},
         'elemental': {'QM-E06': 'exotic matter', 'QM-E12': 'strata', 'MS08': 'bubble/throat', 'RC07': 'closed circuits', 'RC11': 'leakage', 'RC05': 'dark matter', 'RC06': 'superluminal mode', 'QM-E17': 'catalogue', 'QM-E19': 'currents', 'AE20': 'coupling'}}
for lab, tag in (('novice', 'TBN'), ('average', 'TBA'), ('expert', 'TBX')):
    for ont, worlds in (('atomic', ('familiar',)), ('elemental', ('Substance', 'Process'))):
        first_host = collections.Counter(); ground = collections.Counter(); waits = []; n = 0
        for w in worlds:
            rows = WD.set_world(None if w == 'familiar' else w); groups = {k: G.prereq_groups(k) for k in rows}
            H = HOSTS['familiar' if w == 'familiar' else 'elemental']; CLOSE = 'QP08' if w == 'familiar' else 'QM-E27'
            for g in json.load(open(f'{R}w7f_{w}_{tag}.json')):
                t = g['t']
                if not t or CLOSE not in t: continue
                U = t[CLOSE]; hs = sorted((t[h], h) for h in H if h in t and t[h] >= U)
                if not hs: continue
                n += 1; T1, h1 = hs[0]; first_host[H[h1]] += 1; waits.append(T1 - U)
                k, seen = h1, set()
                while k and k not in seen:          # walk the binding chain back while its rows arrived after the theory
                    seen.add(k); best = None
                    for grp in groups.get(k, []):
                        opts = [max(((t.get(p, 10 ** 6), p) for p in o if p in rows), default=None) for o in grp]
                        opts = [o for o in opts if o]
                        if opts:
                            o = min(opts)
                            if best is None or o[0] > best[0]: best = o
                    if not best or best[0] <= U or best[1] == CLOSE: break
                    ground[f"{best[1]} ({rows[best[1]]['focus']}, {rows[best[1]]['era']})"] += 1; k = best[1]
        print(f"\n{lab} / {ont}: {n} games; first answer {st.median(waits):.0f} turns after the unified theory (middle half {st.quantiles(waits, n=4)[0]:.0f}-{st.quantiles(waits, n=4)[2]:.0f})")
        print("   first answer comes from: " + ', '.join(f"{h} {c / n:.0%}" for h, c in first_host.most_common(5)))
        print("   groundwork it waited on (share of games): " + ', '.join(f"{r} {c / n:.0%}" for r, c in ground.most_common(7)))
