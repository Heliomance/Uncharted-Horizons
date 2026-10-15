"""Per-row survey data (Tamsin, 15 Oct 2026: "draft merge candidates, survey for technologies that don't earn their place,
and ones that can be demoted to UNCOMMON").

For every row of the design document, one line of tab-separated data:
  id, name, focus, tier, era, world (the World Truth branch it belongs to, or blank), whether it sits in a Competing
  Solution, and the counts of what its Unlocks column grants: base-game objects (bold names), new objects (bold names
  marked n), uniques (in angle brackets), focus unlocks and resource reveals;
  its direct dependents (rows naming it among their prerequisites) and its guaranteed descendants (rows that cannot be
  discovered without it, reach.sure);
  victory: the victory rows it is a guaranteed ancestor of (or is): each FTL method's build and test rows, the unified
  theory and the FTL screen (w7f.py's tables, atomic and elemental), the canonical spaceship rows (Multi-Stage Rocket,
  Orbital Mechanics, Satellite Technology) and the Generation Ship; and whether it speeds the ship (the Spaceship
  Factory, launch complexes, the Orbital Shipyard, propulsion, exotic components);
  from benchmark results saved with SAVE_T=1 on all 15 victory conditions: for each player (expert, novice, average), the
  share of games in which it is discovered by the race's finish, in the worlds where it exists (familiar, Process,
  Substance), the share of those discoveries that came by diffusion, and the median turn.
Rows of World Truth branches no benchmark world uses (Miasma, Humoral, Caloric, Vitalist, Gravitic) have no measurements.
Usage: python3 row_survey.py [label, default cmpV124] > results/row_survey_<label>.tsv
"""
import sys, os, re, json, collections, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen_data as G, reach as R, worlds as WD

label = sys.argv[1] if len(sys.argv) > 1 else 'cmpV124'
WORLDS = {'familiar': None, 'Process': 'Process', 'Substance': 'Substance'}
METHODS = {'familiar': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling'],
           'Process': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum'], 'Substance': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum']}
PLAYERS = ['X', 'N', 'A']

# The victory's rows, as w7f.py has them (atomic world, then elemental): each method's build (groups of alternatives), the
# hosts of the conditions it is tested on, and the unified theory.
BUILD = {'atomic': {'Warp': [['RC01'], ['QP08'], ['QP11'], ['MS08'], ['ES06', 'ES07', 'ES14', 'ES08'], ['ES18']],
                    'Wormhole': [['RC01'], ['QP08'], ['QP11'], ['MS08'], ['RC04'], ['QP12'], ['MA13'], ['MS17']],
                    'Hyperspace': [['QP08'], ['MA13'], ['ES06', 'ES07', 'ES14', 'ES08'], ['MA19']],
                    'Tunnelling': [['QP02'], ['CP10'], ['MS02', 'GN05'], ['QP14'], ['CP21']],
                    'Tachyonic': [['QP06'], ['QP08'], ['NP11'], ['SE02'], ['ES06', 'ES07', 'ES14', 'ES08'], ['NP15']]},
         'elemental': {'Warp': [['RC01'], ['QM-E27'], ['QM-E06'], ['MS08'], ['ES07', 'ES15', 'QM-E05'], ['ES18']],
                       'Wormhole': [['RC01'], ['QM-E27'], ['QM-E06'], ['MS08'], ['RC04'], ['QM-E13'], ['MA13'], ['MS17']],
                       'Hyperspace': [['QM-E27'], ['MA13'], ['ES07', 'ES15', 'QM-E05'], ['MA19']],
                       'Tachyonic': [['QM-E17'], ['QM-E27'], ['ES07', 'ES15', 'QM-E05'], ['SE02'], ['TH20']],
                       'Plenum': [['QM-E27'], ['MS02'], ['QM-E19'], ['QM-E23'], ['AE20']]}}
HOSTS = {'atomic': [['QP11'], ['QP09', 'QP10'], ['MS08'], ['RC07'], ['RC11'], ['RC05'], ['CP21'], ['QP14'], ['RC06'], ['QP15']],
         'elemental': [['QM-E06'], ['QM-E12'], ['MS08'], ['RC07'], ['RC11'], ['RC05'], ['RC06'], ['QM-E28'], ['QM-E19'], ['AE20']]}
CLOSE = {'atomic': 'QP08', 'elemental': 'QM-E27'}
SHIP = ['RC01', 'RK03', 'RK04', 'RK05']          # the FTL screen; SS Boosters, the Apollo Program, the SS Cockpit
GENSHIP = 'SE11'                                  # the Generation Ship
SPEED = {'MC12': 'Spaceship Factory', 'RK07': 'Space Port', 'RK15': 'Mass Driver', 'RC10': 'Gravitic Platform', 'RK12': 'Space Elevator',
         'SE02': 'Orbital Shipyard'}             # the ship's construction bonuses (§4, How the Victories Are Built); propulsion and exotic components from their tags


def sure_group(g):
    """rows certainly discovered before any member of the group of alternatives g is (including a member common to all)"""
    per = [{a} | set(R.sure(a)) for a in g if a in R.rows]
    return set.intersection(*per) if per else set()


victory = collections.defaultdict(set)   # row -> victory goals it is certain to precede (or is)
for ont in ('atomic', 'elemental'):
    for m, groups in BUILD[ont].items():
        for g in groups:
            for k in sure_group(g): victory[k].add(f'{m} build ({ont})')
    for g in HOSTS[ont]:
        for k in sure_group(g): victory[k].add(f'a test ({ont})')
    for k in sure_group([CLOSE[ont]]): victory[k].add('unified theory')
for s in SHIP:
    for k in sure_group([s]): victory[k].add('the ship' if s != 'RC01' else 'FTL screen')
for k in sure_group([GENSHIP]): victory[k].add('Generation Ship')

body = R.t[:R.t.index('\n## 4.')]
competing = set()
sec6 = R.t[R.t.index('### Competing Solutions Reference'):R.t.index('### Dual-Path Discovery')]
for l in sec6.split('\n'):
    if l.startswith('| ') and '(' in l: competing |= set(re.findall(R.IDRX, l))

deps = collections.defaultdict(set)
for k, r in G.ROWS.items():
    for grp in r['pre']:
        for opt in grp:
            for p in opt:
                if p != k: deps[p].add(k)
desc = collections.Counter()
for k in R.rows:
    for p in R.sure(k): desc[p] += 1


def grants(u):
    bold = re.findall(r'\*\*([^*]+)\*\*(ⁿ?)', u)
    focus = len(re.findall(r'[Uu]nlocks\*?\s*\*\*[^*]+\*\*\s*focus', u))
    return dict(base=sum(1 for _, n in bold if not n) - focus, new=sum(1 for _, n in bold if n), uniques=u.count('⟨'), focus=focus,
                reveals=len(re.findall(r'\*Reveals\*', u)), propulsion='⟨Propulsion⟩' in u, exotic=bool(re.search(r'\+15% .*FTL Drive|exotic component', u)))


# measurements: who discovers each row, in the worlds where it exists
exists = {w: set(WD.world_rows(a)) for w, a in WORLDS.items()}
got = {p: collections.Counter() for p in PLAYERS}; dif = {p: collections.Counter() for p in PLAYERS}; when = {p: collections.defaultdict(list) for p in PLAYERS}
games = {p: collections.Counter() for p in PLAYERS}   # games played in worlds where the row exists
measured = False
for w, ms in METHODS.items():
    for m in ms:
        for p in PLAYERS:
            path = os.path.join(HERE, 'results', f'w7f_{w}_{label}{p}_{m}.json')
            if not os.path.exists(path): continue
            for g in json.load(open(path)):
                if not g.get('t') or not (g['cert'] and g['built']): continue
                measured = True; fin = max(g['cert'], g['built']); d = {k for _, k in (g.get('diffs') or [])}
                for k in exists[w]: games[p][k] += 1
                for k, t in g['t'].items():
                    if 0 < t <= fin:
                        got[p][k] += 1; dif[p][k] += k in d; when[p][k].append(t)

cols = ['id', 'name', 'focus', 'tier', 'era', 'world', 'competing', 'base_objects', 'new_objects', 'uniques', 'focus_unlocks', 'reveals',
        'dependents', 'sure_descendants', 'victory', 'speeds_ship'] + [f'{p}_{x}' for p in PLAYERS for x in ('share', 'diffused', 'turn')]
print('\t'.join(cols))
for k, c in R.rows.items():
    r = G.ROWS[k]; gr = grants(c[5])
    speeds = SPEED.get(k) or ('propulsion' if gr['propulsion'] else '') or ('exotic component' if gr['exotic'] else '')
    line = [k, c[1].strip('*'), r['focus'], r['tier'], r['era'], r['world'] or '', 'yes' if k in competing else '',
            gr['base'], gr['new'], gr['uniques'], gr['focus'], gr['reveals'], len(deps[k]), desc[k], '; '.join(sorted(victory[k])), speeds]
    for p in PLAYERS:
        n = games[p][k]
        if not measured or not n: line += ['', '', '']; continue
        line += [f'{got[p][k] / n:.2f}', f'{dif[p][k] / got[p][k]:.2f}' if got[p][k] else '', f'{st.median(when[p][k]):.0f}' if when[p][k] else '']
    print('\t'.join(str(x) for x in line))
