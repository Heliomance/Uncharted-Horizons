"""What a civilisation discovers on its way to the science victory: FTL-related against non-FTL-related breakthroughs
(Tamsin, 16 Oct 2026: how does letting FTL ideas occur as soon as their focus is funded change the ratio?).

FTL-related means every breakthrough the FTL screen names in the world (w7f.py's FTL_ROWS): each method's build needs, the
breakthroughs that test its conditions, the instruments' breakthroughs and the unified theory. "Own" is the subset the world's
working method needs (its build, tests and instruments, and the theory); "other" is the rest, the other hypotheses' needs.
Everything else is non-FTL, split into the Space era (the W18 pools' reward content and the ship fields) and earlier eras.

Counts are of breakthroughs held at the race's finish (certainty and the build complete), and, for games played on to the
launch (w7f.py TOVICTORY=1: the prototype from the funded share, then the SS FTL Drive), at the launch turn: the whole path to
victory. Those received from rivals count too, and are also shown on their own. Each is also given for what was discovered
after the FTL screen opened (Relativity, RC01). Reads results saved with SAVE_T=1.
Usage: python3 ftl_share.py <label>[@dir][%turn] ...   e.g.  python3 ftl_share.py V125@/path/to/full/results FO V125%276
       (labels as compare_settings.sh writes them: results/w7f_<world>_cmp<label><X|N|A>_<method>.json). %turn counts what is
       held by that turn instead of the race's finish (for the expert; the novice's and average player's cuts follow with
       %turn,turn,turn), to compare two settings at the same moment of the game.
       python3 ftl_share.py --rows <label> <label> [X|N|A]: each breakthrough's share of games holding it at the race's finish
       under both settings, the largest differences first, FTL-related and non-FTL Space-era rows separately.
"""
import sys, os, json, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ftl_balance as B, gen_data as G

PLAYERS = [('X', 'expert'), ('N', 'novice'), ('A', 'average')]
try:   # breakthroughs' names, from the web mockups' bundle (gen_data keeps only ids)
    NAMES = {k: r['name'] for k, r in json.load(open(os.path.join(HERE, '..', '..', 'mockups', 'sim_web', 'bundle.json')))['rows'].items()}
except (OSError, ValueError, KeyError): NAMES = {}


def ftl_rows(ont, m=None):
    ms = [m] if m else list(B.BUILD[ont])
    rows = {o for x in ms for g in B.BUILD[ont][x] for o in g}
    for x in ms:
        for c in B.COND[ont][x]:
            rows |= set(B.HOST[ont][c]) | set(B.INSTR.get(c, []))
    return rows | {B.CLOSE[ont]}


def classify(g, ont, at=None):
    t = g.get('t') or {}
    cert = g['cert'][0] if isinstance(g['cert'], list) else g['cert']
    if not (cert and g.get('built')): return None
    fin = max(cert, g['built']) if at is None else at; own, allf = ftl_rows(ont, g['m']), ftl_rows(ont)
    diffused = {k for _, k in (g.get('diffs') or [])}
    opened = t.get('RC01')
    out = dict(fin=fin, theory=t.get(B.CLOSE[ont]))
    vt = g.get('vt') if at is None else None   # played on to the launch (w7f.py TOVICTORY=1): the whole path to victory
    scopes = [('all', lambda k: t[k] <= fin), ('screen', lambda k: opened is not None and opened < t[k] <= fin)]
    if vt: scopes += [('launch', lambda k: t[k] <= vt), ('launchscreen', lambda k: opened is not None and opened < t[k] <= vt)]
    out['vt'] = vt
    for scope, keep in scopes:
        ks = [k for k in t if keep(k)]
        out[scope] = dict(own=sum(k in own for k in ks), other=sum(k in allf and k not in own for k in ks),
                          ftlspace=sum(k in allf and G.ROWS.get(k, {}).get('era') == 'Space' for k in ks),
                          space=sum(k not in allf and G.ROWS[k]['era'] == 'Space' for k in ks if k in G.ROWS),
                          early=sum(k not in allf and G.ROWS[k]['era'] != 'Space' for k in ks if k in G.ROWS),
                          diffused=sum(k in diffused for k in ks))
    return out


def load(label, code):
    label, _, cut = label.partition('%'); lab, _, d = label.partition('@'); d = d or os.path.join(HERE, 'results')
    at = int(cut.split(',')['XNA'.index(code)] if ',' in cut else cut) if cut else None
    games = []
    for w, ont in B.WORLDS.items():
        for m in B.BUILD[ont]:
            p = os.path.join(d, f'w7f_{w}_cmp{lab}{code}_{m}.json')
            for g in json.load(open(p)):
                if not g.get('t'): raise SystemExit(f'{p} has no discovery turns: run with SAVE_T=1')
                c = classify(g, ont, at)
                games.append(c if c else dict(fin=None))
    return games


def rows(a, b, code):
    """each breakthrough's share of games holding it at the race's finish, under settings a and b"""
    out = {}
    for lab in (a, b):
        name, _, d = lab.partition('@'); d = d or os.path.join(HERE, 'results'); n = 0; held = {}
        for w, ont in B.WORLDS.items():
            for m in B.BUILD[ont]:
                for g in json.load(open(os.path.join(d, f'w7f_{w}_cmp{name}{code}_{m}.json'))):
                    n += 1; t = g.get('t') or {}
                    for k in t: held[k] = held.get(k, 0) + 1
        out[lab] = {k: v / n for k, v in held.items()}
    allf = ftl_rows('atomic') | ftl_rows('elemental')
    keys = set(out[a]) | set(out[b])
    for title, sel in (('FTL-related', lambda k: k in allf), ('non-FTL, Space era', lambda k: k not in allf and G.ROWS.get(k, {}).get('era') == 'Space'),
                       ('non-FTL, earlier eras', lambda k: k not in allf and G.ROWS.get(k, {}).get('era') not in (None, 'Space'))):
        ks = sorted((k for k in keys if sel(k)), key=lambda k: out[b].get(k, 0) - out[a].get(k, 0))
        print(f'\n== {title}: share of all games holding each at the race\'s finish, {a.partition("@")[0]} -> {b.partition("@")[0]} (largest falls, then largest rises)')
        for k in ks[:12] + ['...'] + ks[-8:]:
            if k == '...': print('   ...'); continue
            print(f"   {k:7} {NAMES.get(k, k)[:38]:38} {G.ROWS[k]['focus'][:20]:20} {out[a].get(k, 0):5.0%} -> {out[b].get(k, 0):5.0%}")


def main():
    if sys.argv[1] == '--rows': return rows(sys.argv[2], sys.argv[3], (sys.argv[4:] or ['X'])[0])
    labels = sys.argv[1:]
    print('Breakthroughs held at the race\'s finish, mean a game (all 15 conditions, 900 games a player and setting).')
    print('FTL own = the working method\'s needs and tests; FTL other = the other hypotheses\'; non-FTL split Space / earlier eras.\n')
    for code, name in PLAYERS:
        print(f'=== {name}')
        for label in labels:
            gs = load(label, code); ok = [g for g in gs if g['fin'] is not None]
            sc = [('all', 'to the race\'s finish'), ('screen', '  of which after the screen')]
            if all(g.get('vt') for g in ok): sc += [('launch', 'to the launch'), ('launchscreen', '  of which after the screen')]
            for scope, title in sc:
                mean = lambda f: st.mean(f(g[scope]) for g in ok)
                turn = st.median(g['vt'] if scope.startswith('launch') else g['fin'] for g in ok)
                own, oth, sp, ea, dif, fsp = (mean(lambda x, k=k: x[k]) for k in ('own', 'other', 'space', 'early', 'diffused', 'ftlspace'))
                ftl, non = own + oth, sp + ea
                print(f'  {label.partition("%")[0].partition("@")[0] + ("@" + label.partition("%")[2] if "%" in label else ""):16} {title:28} turn {turn:5.0f} | FTL {ftl:5.1f} (own {own:4.1f}, other {oth:4.1f})'
                      f' | non-FTL {non:5.1f} (Space {sp:4.1f}, earlier {ea:5.1f}) | FTL share {ftl / (ftl + non):5.1%}, FTL:non-FTL 1:{non / ftl:4.1f}'
                      f' | Space era: FTL {fsp:4.1f}, non-FTL {sp:4.1f} ({fsp / (fsp + sp):4.0%} FTL)'
                      f' | from rivals {dif:4.1f}' + (f' | unfinished {len(gs) - len(ok)}' if len(gs) > len(ok) else ''))
        print()


if __name__ == '__main__':
    main()
