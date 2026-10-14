"""Thinning inventory: one focus's rows with what they grant, what needs them, and any structural role."""
import sys, re, json; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import reach as R, gen_data as G, json5
P = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/thin_baseline.json'))['row_p']
CANON = {b['name'] for b in json5.load(open('/home/user/Uncharted-Horizons/design/simulator/unciv/Buildings.json', encoding='utf-8'))}
CANON |= {u['name'] for u in json5.load(open('/home/user/Uncharted-Horizons/design/simulator/unciv/Units.json', encoding='utf-8'))}
t = R.t; body = t[:t.index('## Changelog')]
comp = set(re.findall(r'\(([A-Z]{1,3}\d+[A-Z]?(?:-W)?)\)', body[body.find('| Goal | Primary | Alternative |'):body.find('| Goal | Primary | Alternative |') + 4000]))
def deps(k): return sorted(d for d, c in R.rows.items() if re.search(rf'\b{re.escape(k)}\b', c[4]) and d != k)
def inventory(focus):
    out = []
    for k, c in R.rows.items():
        if G.ROWS.get(k, {}).get('focus') != focus: continue
        u = c[5]
        canon = [n for n in re.findall(r'\*\*([^*]+)\*\*(?!ⁿ)', re.sub(r'requires an? \*\*[^*]+\*\* in this city', '', u)) if n in CANON]
        fork = re.findall(r'\*\*([^*]+)\*\*ⁿ', u)
        uniq = len(re.findall(r'⟨', re.sub(r'\*\*[^*]+\*\*ⁿ\s*\[[^\]]*\]', '', u)))
        flags = []
        if canon: flags.append('canon-home')
        if k in comp: flags.append('competing')
        if G.ROWS[k]['world']: flags.append(G.ROWS[k]['world'])
        if re.search(r'FTL|Method [A-F]', u + c[6]): flags.append('FTL')
        d = deps(k); core_deps = [x for x in d if R.rows[x][2] == 'CORE']
        out.append(dict(id=k, name=re.sub(r'\*', '', c[1]), tier=c[2], era=c[3], p=P.get(k), canon=canon, fork=fork, uniques=uniq,
                        deps=d, core_deps=core_deps, flags=flags, pre=c[4], text=u))
    EO = G.EO if hasattr(G, 'EO') else ['Primitive','Ancient','Classical','Medieval','Early Modern','Modern','Atomic','Space']
    return sorted(out, key=lambda x: (EO.index(x['era']) if x['era'] in EO else 9, x['id']))
if __name__ == '__main__':
    for r in inventory(sys.argv[1]):
        p = f"{r['p']:.2f}" if r['p'] is not None else ' — '
        print(f"{r['id']:7} {r['era'][:5]:5} {r['tier'][:4]:4} p={p}  {r['name'][:30]:30} grants {(r['canon']+[x+'ⁿ' for x in r['fork']])[:4]} +{r['uniques']}u  needed by {r['deps'][:5]}{'…' if len(r['deps'])>5 else ''}  {' '.join(r['flags'])}")
        print(f"        pre[{r['pre'][:90]}]")
