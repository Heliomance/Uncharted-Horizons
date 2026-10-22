"""The Space-era chains behind each FTL method (Tamsin, 22 Oct 2026: "a visualisation of the space age technologies each method
needs, as a flow through their prereqs ... both in the current system, and with the proposed changes").

For each world kind (atomic: the familiar world; elemental: Process and Substance, whose Space-era rows are identical) and each
method, draws every Space-era breakthrough the method's race needs (its build needs, the tests of its own three conditions and
the unified theory) and the Space-era prerequisites that lead to them, as a left-to-right flow, at the current tree and with a
proposed set of prerequisite changes. A requirement or prerequisite group that an earlier-era breakthrough can meet is left out
and listed under the figure. The badge on each non-CORE breakthrough counts the ideas that must occur one after another up to
and including it, on its quickest route. Writes one HTML page of static inline SVG.

The trees come from the simulator's own reading of the design document (worlds.py, through scratch_run.sh, with SETCELL for
the proposal); the method definitions from ftl_balance.py (the agreed levers: Transformation Media in Wormhole's build, no NP11
in atomic Tachyonic's); price notes from the document's prerequisite cells.

Usage: python3 ftl_chains.py <out.html> [--lag CUR:PROP]
       --lag reads each method's victory median against its world's field from saved results (ftl_sync.py labels, e.g.
       V127:P3) and adds it to the summary table.
       PROPOSAL (environment) replaces the default SETCELL spec of the proposal drawn.
"""
import sys, os, re, json, html, subprocess, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, '..', '..', 'tech_tree.md')
PROPOSAL = os.environ.get('PROPOSAL') or (
    'AE20|4|QM-E19 + AE14;'
    'CP10|4|((QP07 + CP01) or GN10) — **cost ×2**;'
    'MS17|4|(QP11 Exotic Matter Synthesis, validated, or QM-E06 Exotic Matter, validated) + (QP12 or QM-E13) — **cost ×4**')
CHANGES = [   # the proposal in words: (row, before, after, methods)
    ('AE20', 'Current Sail + Aerospace Industry', 'Celestial Current Survey + Aerospace Industry', 'Plenum'),
    ('CP10', '(Quantum Entanglement Mastery + Programmable Computer, or Bio-Quantum Coherence) + Planetary Data Networks',
     'Quantum Entanglement Mastery + Programmable Computer, or Bio-Quantum Coherence', 'Tunnelling'),
    ('MS17', 'Exotic Matter Engineering + (Casimir Effect Amplification or Aetheric Vacuum)',
     'Exotic Matter Synthesis or Exotic Matter, validated, + (Casimir Effect Amplification or Aetheric Vacuum)', 'Wormhole'),
]
COND_WORDS = {'exotic': 'exotic matter', 'extradim': 'extra dimensions', 'discrete': 'discreteness', 'bubble': 'bubble stability',
              'throat': 'throat stability', 'closed': 'closed curves', 'leak': 'leakage', 'dark': 'dark matter',
              'tachDE': 'the tachyonic field', 'coherence': 'coherence', 'hartman': 'the Hartman effect', 'tachyon': 'a tachyonic sector',
              'strata': 'higher strata', 'superlum': 'a superluminal mode', 'catalogue': 'a superluminal form',
              'currents': "the currents' speed", 'coupling': 'riding the currents'}
COND_WORDS_EL = {'closed': 'closed circuits', 'leak': 'leakage into the strata'}
KINDS = [('atomic', 'The atomic world', 'The familiar world'), ('elemental', 'The elemental worlds', 'Process and Substance, whose Space-era rows are the same')]
ORDER = {'atomic': ['Tunnelling', 'Wormhole', 'Warp', 'Hyperspace', 'Tachyonic'], 'elemental': ['Plenum', 'Wormhole', 'Warp', 'Hyperspace', 'Tachyonic']}
NOTES = {   # what the run lengths mean for each method, in words (checked against the drawn data by the assertions in main)
    ('atomic', 'Tunnelling'): "Quantum Computing waits for Planetary Data Networks, an idea of its own, so the coherence test is the third idea in a row. None of it needs the unified theory, yet at v3.127 the expert finds Planetary Data Networks after the theory (median turn 265, against 251). Without that prerequisite Quantum Computing waits only for its own idea, because Quantum Entanglement Mastery is CORE.",
    ('atomic', 'Wormhole'): "Transformation Media waits for Exotic Matter Engineering: four ideas in a row, from Casimir Effect Amplification to Transformation Media. Casimir needs no theory, but at v3.127 the expert finds it with the theory all the same (median turn 252, against 251). With the change, Transformation Media follows Exotic Matter Synthesis alongside Exotic Matter Engineering: three.",
    ('atomic', 'Warp'): "Three in a row, from Casimir Effect Amplification to Exotic Matter Engineering: the same run as Wormhole's before Transformation Media.",
    ('atomic', 'Hyperspace'): "Two short runs, neither waiting on the theory: Optimisation Theory before Higher-Dimensional Geometry, and Orbital Assembly before the Gravitational Leakage Survey.",
    ('atomic', 'Tachyonic'): "Every test hangs directly off the theory, and the Storage Rings and Orbital Assembly need nothing from the Space era: no idea waits on another.",
    ('elemental', 'Plenum'): "Current Rigging waits for the Current Sail, which waits for the Celestial Current Survey, which waits for the theory: three ideas in a row, all after it. The sail also waits for Aerospace Industry and the Reusable Launch Vehicle. With the change the rigging follows the survey alongside the sail, so the run is two.",
    ('elemental', 'Wormhole'): "Exotic Matter, Exotic Matter Engineering and Transformation Media in a row, all after the theory. With the change, Transformation Media follows Exotic Matter alongside Exotic Matter Engineering: two.",
    ('elemental', 'Warp'): "Exotic Matter before Exotic Matter Engineering, both after the theory: two.",
    ('elemental', 'Hyperspace'): "As in the atomic world, with Higher Strata Theory testing strata straight after the theory.",
    ('elemental', 'Tachyonic'): "The Re-Tempering Reactor before the Boundary Ring (×4), neither waiting on the theory; every test hangs directly off it.",
}


# ---- data: the simulator's reading of the tree --------------------------------------------------------------------------
def dump(path):
    """(Runs under scratch_run.sh.) Each world kind's Space-era rows and each method's requirements, as JSON."""
    sys.path.insert(0, HERE)
    import worlds as W, ftl_balance as FB
    out = {}
    for wname, kind in (('familiar', 'atomic'), ('Process', 'elemental')):
        rows = W.set_world(None if wname == 'familiar' else wname)
        space = lambda k: rows[k]['era'] == 'Space'
        R = {}
        for k, r in rows.items():
            if not space(k): continue
            groups = []
            for grp in r['pre']:
                opts = [[p for p in opt if p in rows] for opt in grp]
                groups.append([[dict(id=p, space=space(p)) for p in o] for o in opts if o])   # an option of absent rows is no route
            R[k] = dict(tier=r['tier'], focus=r['focus'], groups=groups)
        methods = {}
        for m in FB.COND[kind]:
            reqs = [dict(kind='build', alts=[a for a in g if a in rows]) for g in FB.BUILD[kind][m]]
            reqs += [dict(kind='test', cond=c, alts=[a for a in FB.HOST[kind][c] if a in rows]) for c in FB.COND[kind][m]]
            reqs.append(dict(kind='theory', alts=[FB.CLOSE[kind]]))
            methods[m] = reqs
        out[kind] = dict(rows=R, methods=methods, era={k: rows[k]['era'] for k in rows})
    json.dump(out, open(path, 'w'))


def load(setcell):
    path = os.path.join(os.environ.get('TMPDIR', '/tmp'), f'ftl_chains_{os.getpid()}_{bool(setcell)}.json')
    env = dict(os.environ); env.pop('SETCELL', None)
    if setcell: env['SETCELL'] = setcell
    subprocess.run(['bash', os.path.join(HERE, 'scratch_run.sh'), sys.executable, os.path.abspath(__file__), '--dump', path],
                   env=env, check=True, stdout=subprocess.DEVNULL)
    d = json.load(open(path)); os.remove(path)
    return d


def doc_names():
    """Each row's name and the price note of its prerequisite cell, from the design document itself."""
    name, note = {}, {}
    for l in open(DOC, encoding='utf-8'):
        m = re.match(r'^\| ([A-Z]{1,3}\d+[A-Z]?(?:-W)?|ME-B|NP-F\d+|QM-E\d+|MI05B|MI06B|[A-Z]{2}-[A-Z]\d+) \| \*\*(.+?)\*\* \| \S+ \| [^|]+? \| ([^|]*?) \|', l)
        if m and m.group(1) not in name:
            name[m.group(1)] = m.group(2)
            c = re.search(r'cost ×([\d.]+)', m.group(3))
            if c: note[m.group(1)] = c.group(1)
    version = next((v.group(1) for l in open(DOC, encoding='utf-8') if (v := re.match(r'^### (v\d+\.\d+) ', l))), '')
    return name, note, version


def short(name):
    """The name drawn on a node: the first of a row's world names (the full name stays in its tooltip)."""
    return re.split(r' \(| / ', name)[0]


# ---- one method's graph ---------------------------------------------------------------------------------------------------
def graph(d, m):
    R, E = d['rows'], d['era']
    roles, conds, either, earlier, roots = collections.defaultdict(list), collections.defaultdict(list), [], [], []
    for r in d['methods'][m]:
        alts = r['alts']
        if any(E[a] != 'Space' for a in alts):            # met by an earlier-era breakthrough: not drawn
            earlier.append((r['kind'], r.get('cond'), [a for a in alts if E[a] != 'Space'])); continue
        for a in alts:
            if r['kind'] not in roles[a]: roles[a].append(r['kind'])
            if r.get('cond'): conds[a].append(r['cond'])
            if a not in roots: roots.append(a)
        if len(alts) > 1: either.append(list(alts))
    nodes, edges, ors = [], [], {}                         # edges: (src, dst, or-group id or None)
    def walk(k):
        if k in nodes: return
        nodes.append(k)
        for gi, grp in enumerate(R[k]['groups']):
            if any(all(not p['space'] for p in opt) for opt in grp): continue   # an earlier-era option meets the group
            gid = f'{k}#{gi}' if len(grp) > 1 else None
            if gid: ors[gid] = k
            for opt in grp:
                for p in opt:
                    if p['space'] and (p['id'], k, gid) not in edges: edges.append((p['id'], k, gid)); walk(p['id'])
    for a in roots: walk(a)
    memo = {}
    def run(k):   # ideas that must occur one after another up to and including k, on its quickest route
        if k not in memo:
            best = 0
            for grp in R[k]['groups']:
                if any(all(not p['space'] for p in opt) for opt in grp): continue
                best = max(best, min(max((run(p['id']) for p in opt if p['space']), default=0) for opt in grp))
            memo[k] = best + (0 if R[k]['tier'] == 'CORE' else 1)
        return memo[k]
    return dict(nodes=nodes, edges=edges, ors=ors, roles=dict(roles), conds=dict(conds), either=either, earlier=earlier,
                run={k: run(k) for k in nodes}, longest=max(run(k) for k in roots))


# ---- layout and drawing -----------------------------------------------------------------------------------------------------
NW, GX, GY, GD, PAD, PADR = 176, 60, 30, 18, 24, 56   # node width; gaps between layers, between nodes and beside an arrow's
LINE, FLINE, TOP = 15, 13, 9                        # pass-through; margins (the right one leaves room for 'either')


def wrap(text, n=22):
    words, lines = text.split(), ['']
    for w in words:
        if lines[-1] and len(lines[-1]) + 1 + len(w) > n: lines.append(w)
        else: lines[-1] = (lines[-1] + ' ' + w).strip()
    return lines


def node_h(g, k, label):
    return TOP + LINE * len(wrap(label[k])) + FLINE + (17 if k in g['roles'] else 10)


def pava(vals):
    """the non-decreasing sequence nearest vals (least squares): pool adjacent violators"""
    blocks = []
    for v in vals:
        blocks.append([v, 1])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1]:
            s, c = blocks.pop(); blocks[-1][0] += s; blocks[-1][1] += c
    return [s / c for s, c in blocks for _ in range(c)]


def layout(g, label, seed=None):
    """Layers by longest path; an arrow that skips a layer runs through a pass-through point in each layer it crosses, so it
    keeps to the gaps; order within layers by barycentre sweeps (or the given order); heights placed nearest their neighbours."""
    nodes, edges = g['nodes'], g['edges']
    preds0 = {k: [s for s, t, _ in edges if t == k] for k in nodes}
    layer = {}
    def L(k):
        if k not in layer: layer[k] = 1 + max((L(p) for p in preds0[k]), default=-1)
        return layer[k]
    for k in nodes: L(k)
    chains, adj = {}, collections.defaultdict(list)   # each arrow's waypoints; neighbours in the next layer
    for s, t, gid in edges:
        pts = [s] + [f'~{s}>{t}>{gid}>{i}' for i in range(layer[s] + 1, layer[t])] + [t]
        for i, p in enumerate(pts[1:-1], layer[s] + 1): layer[p] = i
        chains[(s, t, gid)] = pts
        for a, b in zip(pts, pts[1:]): adj[a].append(b)
    allk = list(layer)
    preds = {k: [a for a in allk if k in adj[a]] for k in allk}
    succs = {k: adj[k] for k in allk}
    nl = max(layer.values()) + 1
    group = {k: i for i, grp in enumerate(g['either']) for k in grp}
    lay = [[k for k in allk if layer[k] == i] for i in range(nl)]
    pos = {}
    def settle(lst, key):
        keyed = {k: key(k) for k in lst}
        for i in set(group.get(k) for k in lst) - {None}:   # keep an 'either' pair together
            mem = [k for k in lst if group.get(k) == i]; mean = sum(keyed[k] for k in mem) / len(mem)
            for k in mem: keyed[k] = mean
        lst.sort(key=lambda k: (keyed[k], group.get(k, -1), k))
        for i, k in enumerate(lst): pos[k] = i
    for lst in lay:   # first order: the given one (seed), else leaves last, then by name
        init = {k: j for j, k in enumerate(sorted(lst, key=lambda k: (not succs[k], label.get(k, k))))}
        settle(lst, (lambda k: seed.get(k, 1000 + init[k])) if seed else (lambda k: init[k]))
    bary = lambda nb, k: sum(pos[n] for n in nb[k]) / len(nb[k]) if nb[k] else pos[k]
    for _ in range(0 if seed else 8):
        for lst in lay[1:]: settle(lst, lambda k: bary(preds, k))
        for lst in reversed(lay[:-1]): settle(lst, lambda k: bary(succs, k))
    if seed:   # a dummy follows its arrow's ends
        for _ in range(3):
            for lst in lay[1:]: settle(lst, lambda k: seed[k] if k in seed else bary(preds, k))
    h = {k: (node_h(g, k, label) if not k.startswith('~') else 2) for k in allk}
    gap = lambda a, b: GY if not (a.startswith('~') or b.startswith('~')) else GD
    y = {}
    for lst in lay:
        c = 0.0
        for i, k in enumerate(lst): y[k] = c; c += h[k] + (gap(k, lst[i + 1]) if i + 1 < len(lst) else 0)
    def place(lst, nb):
        off, c = [], 0.0
        for i, k in enumerate(lst): off.append(c); c += h[k] + (gap(k, lst[i + 1]) if i + 1 < len(lst) else 0)
        want = [(sum(y[n] + h[n] / 2 for n in nb[k]) / len(nb[k]) - h[k] / 2) if nb[k] else y[k] for k in lst]
        z = pava([w - o for w, o in zip(want, off)])
        for k, zz, o in zip(lst, z, off): y[k] = zz + o
    for _ in range(12):
        for lst in lay[1:]: place(lst, preds)
        for lst in reversed(lay[:-1]): place(lst, succs)
    top = min(y.values()); y = {k: v - top for k, v in y.items()}
    H = max(y[k] + h[k] for k in allk)
    xy = {k: (layer[k] * (NW + GX), y[k]) for k in allk}
    return xy, h, nl, H, {k: pos[k] for k in allk if not k.startswith('~')}, chains


def esc(s): return html.escape(str(s), quote=True)


def bez(x1, y1, x2, y2):
    dx = max(18.0, (x2 - x1) * 0.5)
    return f'C{x1 + dx:.1f},{y1:.1f} {x2 - dx:.1f},{y2:.1f} {x2:.1f},{y2:.1f}'


def svg(g, d, info, fid, label, seed=None, changed=None, kind='atomic'):
    """One figure's SVG. changed: dict(drop=set of (src, dst) arrows drawn as dropped, new=set drawn as new, gone=set of
    breakthroughs drawn as leaving the route)."""
    R = d['rows']; name, note = info
    xy, hh, nl, H, order, chains = layout(g, label, seed)
    changed = changed or dict(drop=set(), new=set(), gone=set())
    W = PAD + nl * NW + (nl - 1) * GX + PADR; HT = H + 2 * PAD + 14
    ox, oy = PAD, PAD + 10
    P = lambda k: (xy[k][0] + ox, xy[k][1] + oy)
    cy = lambda k: P(k)[1] + hh[k] / 2
    # what enters each breakthrough: an arrow, or one 'or' junction per group of alternatives; ports spread down its sides
    entries = collections.defaultdict(list)
    for (s, t, gid), pts in chains.items():
        e = ('e', s) if gid is None else ('o', gid)
        if e not in entries[t]: entries[t].append(e)
    last = {key: pts[-2] for key, pts in chains.items()}   # the waypoint just before the target
    def ent_y(t, e):
        ks = [key for key in chains if key[1] == t and ((e[0] == 'e' and key[0] == e[1] and key[2] is None) or (e[0] == 'o' and key[2] == e[1]))]
        return sum(cy(last[k_]) for k_ in ks) / len(ks)
    port_in = {}
    for t, ent in entries.items():
        ent.sort(key=lambda e: ent_y(t, e))
        for i, e in enumerate(ent): port_in[(t, e)] = P(t)[1] + 15 + (hh[t] - 27) * (i + 1) / (len(ent) + 1)   # (clear of the badge and the pills)
    outs = collections.defaultdict(list)
    for key, pts in chains.items(): outs[key[0]].append(key)
    port_out = {}
    for s, keys in outs.items():
        keys.sort(key=lambda key: (cy(chains[key][1]) if len(chains[key]) > 2 else port_in[(key[1], ('e', s) if key[2] is None else ('o', key[2]))]))
        for i, key in enumerate(keys): port_out[key] = P(s)[1] + 12 + (hh[s] - 24) * (i + 1) / (len(keys) + 1)
    junction = {}
    for (t, e), py in port_in.items():
        if e[0] == 'o': junction[e[1]] = (P(t)[0] - 22, py)
    m_ = lambda kind_: f'url(#{kind_}-{fid[0]})'
    out = [f'<svg class="flow" viewBox="0 0 {W:.0f} {HT:.0f}" width="{W:.0f}" height="{HT:.0f}" role="img" aria-label="{esc(fid[1])}"><defs>']
    for mk, cls in (('a', 'mk'), ('d', 'mk mk-drop'), ('n', 'mk mk-new')):
        out.append(f'<marker id="{mk}-{fid[0]}" class="{cls}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z"/></marker>')
    out.append('</defs>')
    for grp in g['either']:   # 'either' outlines, behind everything
        x0 = min(P(k)[0] for k in grp) - 7; y0 = min(P(k)[1] for k in grp) - 8
        x1 = max(P(k)[0] + NW for k in grp) + 7; y1 = max(P(k)[1] + hh[k] for k in grp) + 10
        out.append(f'<rect class="either" x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="10"/>'
                   f'<text class="either-t" x="{x1 + 6:.1f}" y="{(y0 + y1) / 2 + 4:.1f}">either</text>')
    tags = []
    for key, pts in chains.items():
        s, t, gid = key
        cls = 'e-drop' if (s, t) in changed['drop'] else 'e-new' if (s, t) in changed['new'] else 'e'
        x, y_ = P(s)[0] + NW, port_out[key]; d_ = f'M{x:.1f},{y_:.1f}'
        for p in pts[1:-1]:   # through each pass-through point, level across its column
            px, py = P(p)[0], P(p)[1] + 1
            d_ += f' {bez(x, y_, px, py)} L{px + NW:.1f},{py:.1f}'; x, y_ = px + NW, py
        if gid is None:
            x2, y2 = P(t)[0] - 1, port_in[(t, ('e', s))]
            out.append(f'<path class="{cls}" d="{d_} {bez(x, y_, x2, y2)}" marker-end="{m_({"e": "a", "e-drop": "d", "e-new": "n"}[cls])}"/>')
        else:
            x2, y2 = junction[gid][0] - 7.5, junction[gid][1]
            out.append(f'<path class="{cls}" d="{d_} {bez(x, y_, x2, y2)}"/>')
        if cls != 'e': tags.append((cls, (x + x2) / 2, (y_ + y2) / 2 - 11))
    for gid, (jx, jy) in junction.items():
        t = g['ors'][gid]
        out.append(f'<path class="e" d="M{jx + 7.5:.1f},{jy:.1f} L{P(t)[0] - 1:.1f},{jy:.1f}" marker-end="{m_("a")}"/>'
                   f'<circle class="or" cx="{jx:.1f}" cy="{jy:.1f}" r="7.5"/><text class="or-t" x="{jx:.1f}" y="{jy + 3:.1f}">or</text>')
    for cls, mx, my in tags:
        word = 'dropped' if cls == 'e-drop' else 'new'; w = 8 + len(word) * 5.6
        out.append(f'<rect class="tagbg" x="{mx - w / 2:.1f}" y="{my - 8:.1f}" width="{w:.1f}" height="15" rx="7.5"/>'
                   f'<text class="tag {cls}-t" x="{mx:.1f}" y="{my + 3.4:.1f}">{word}</text>')
    cw = COND_WORDS_EL if kind == 'elemental' else {}
    for k in g['nodes']:
        x, y = P(k); h = hh[k]; r = R[k]; core = r['tier'] == 'CORE'
        roles = g['roles'].get(k, [])
        cls = 'node ' + ('core' if core else 'idea') + (' req' if roles else '') + (' gone' if k in changed['gone'] else '')
        tip = [f"{name.get(k, k)} ({k})", r['focus'], 'CORE: studied as soon as its prerequisites are met' if core else f"{r['tier']} idea: it must occur before it can be studied"]
        if k in note: tip.append(f'price ×{note[k]}')
        for role in roles:
            tip.append({'build': 'a build need', 'theory': 'the unified theory',
                        'test': 'tests ' + ' and '.join(cw.get(c, COND_WORDS[c]) for c in g['conds'].get(k, []))}[role])
        if not core: tip.append(f"idea {g['run'][k]} in a row on its quickest route")
        if k in changed['gone']: tip.append('leaves the route with the proposal')
        out.append(f'<g class="{cls}"><title>{esc(" · ".join(tip))}</title>'
                   f'<rect class="box" x="{x:.1f}" y="{y:.1f}" width="{NW}" height="{h}" rx="6"/>')
        lines = wrap(label[k])
        for i, ln in enumerate(lines):
            out.append(f'<text class="nm" x="{x + 11:.1f}" y="{y + TOP + 11 + i * LINE:.1f}">{esc(ln)}</text>')
        out.append(f'<text class="fd" x="{x + 11:.1f}" y="{y + TOP + 11 + len(lines) * LINE:.1f}">{esc(r["focus"])}</text>')
        if k in note:
            t = f'×{note[k]}'; w = 9 + 6.2 * len(t)
            out.append(f'<rect class="price" x="{x + NW - w - 8:.1f}" y="{y - 7:.1f}" width="{w:.1f}" height="14" rx="7"/>'
                       f'<text class="price-t" x="{x + NW - 8 - w / 2:.1f}" y="{y + 3.3:.1f}">{esc(t)}</text>')
        if not core:
            mx = ' max' if g['run'][k] == g['longest'] and g['longest'] > 1 else ''
            out.append(f'<circle class="run{mx}" cx="{x:.1f}" cy="{y + 2:.1f}" r="9"/><text class="run-t{mx}" x="{x:.1f}" y="{y + 5.6:.1f}">{g["run"][k]}</text>')
        px = x + 10
        for role in roles:
            t = role.upper(); w = 10 + 6.1 * len(t)
            out.append(f'<rect class="pill p-{role}" x="{px:.1f}" y="{y + h - 7:.1f}" width="{w:.1f}" height="14" rx="3"/>'
                       f'<text class="pill-t t-{role}" x="{px + w / 2:.1f}" y="{y + h + 3.2:.1f}">{t}</text>')
            px += w + 5
        out.append('</g>')
    out.append('</svg>')
    return '\n'.join(out), order


# ---- the page -----------------------------------------------------------------------------------------------------------------
def notes_html(g, d, name, kind):
    E = d['era']; cw = COND_WORDS_EL if kind == 'elemental' else {}
    pre = []
    for k_, c, alts in g['earlier']:
        nm = ' or '.join(short(name.get(a, a)) for a in alts)
        pre.append(f'{esc(nm)} ({"tests " + cw.get(c, COND_WORDS[c]) if k_ == "test" else "build"})' if len(alts) == 1 or k_ == 'test'
                   else f'{esc(nm)} (build, any one)')
    tests = collections.OrderedDict()
    for k in g['nodes']:
        for c in g['conds'].get(k, []): tests.setdefault(c, []).append(short(name.get(k, k)))
    t = '; '.join(f'{esc(cw.get(c, COND_WORDS[c]))}: {esc(" or ".join(v))}' for c, v in tests.items())
    parts = []
    if t: parts.append(f'<p class="meta"><span class="k">Tests</span> {t}</p>')
    if pre: parts.append(f'<p class="meta"><span class="k">From earlier eras, not drawn</span> {"; ".join(pre)}</p>')
    return '\n'.join(parts)


def lag_cell(lagset, world, m):
    """'expert / novice / average' turns behind the world's field, from one setting's table"""
    v = lagset.get(world, {}).get(m)
    f = lambda x: '0' if round(x) == 0 else f'{x:+.0f}'.replace('-', '−')
    return ' / '.join(f(x) for x in (v['expert'], v['novice'], v['average'])) if v else ''


def main():
    if sys.argv[1] == '--dump': return dump(sys.argv[2])
    outp = sys.argv[1]
    lag = None
    if '--lag' in sys.argv:
        cur, prop = sys.argv[sys.argv.index('--lag') + 1].split(':')
        sys.path.insert(0, HERE); import ftl_sync as S
        lag = {}
        for lab in (cur, prop):
            T = S.table(lab); lag[lab] = {}
            for code, pname, econ, ref in S.PLAYERS:
                for w in S.WORLDS:
                    for m, dv in T[(pname, w)]['dev'].items(): lag[lab].setdefault(w, {}).setdefault(m, {})[pname] = dv
        lag = dict(cur=lag[cur], prop=lag[prop], labels=(cur, prop))
    name, note, version = doc_names()
    D = {'cur': load(None), 'prop': load(PROPOSAL)}
    label = {k: short(n) for k, n in name.items()}
    sections, summary = [], []
    for kind, title, sub in KINDS:
        blocks_changed, blocks_same = [], []
        for m in ORDER[kind]:
            gc, gp = graph(D['cur'][kind], m), graph(D['prop'][kind], m)
            ec, ep = {(s, t) for s, t, _ in gc['edges']}, {(s, t) for s, t, _ in gp['edges']}
            same = ec == ep and gc['nodes'] == gp['nodes']
            fid = f'{kind[:2]}-{m.lower()}'
            claim = f"{m}, {title.lower()}: the Space-era breakthroughs its race needs; at most {gc['longest']} ideas must occur in a row"
            sc, order = svg(gc, D['cur'][kind], (name, note), (fid + '-c', claim), label, kind=kind,
                            changed=dict(drop=ec - ep, new=set(), gone=set(gc['nodes']) - set(gp['nodes'])))
            head = (f'<div class="mhead"><h3 id="{fid}">{m}</h3><span class="runs">'
                    + (f'<b>{gc["longest"]}</b> in a row' if same else f'<b>{gc["longest"]}</b> <span class="arr">→</span> <b class="to">{gp["longest"]}</b> in a row')
                    + '</span></div>')
            note_p = f'<p class="lead">{esc(NOTES[(kind, m)])}</p>'
            if same:
                blocks_same.append(f'<section class="method same">{head}{note_p}<figure><div class="scroll">{sc}</div></figure>'
                                   f'{notes_html(gc, D["cur"][kind], name, kind)}</section>')
            else:
                claim_p = f"{m}, {title.lower()}, with the proposed changes: at most {gp['longest']} ideas must occur in a row"
                sp, _ = svg(gp, D['prop'][kind], (name, note), (fid + '-p', claim_p), label, seed=dict(order), kind=kind,
                            changed=dict(drop=set(), new=ep - ec, gone=set()))
                blocks_changed.append(
                    f'<section class="method">{head}{note_p}'
                    f'<figure><figcaption class="ver"><span class="vtag">{esc(version)}</span> today</figcaption><div class="scroll">{sc}</div></figure>'
                    f'<figure><figcaption class="ver"><span class="vtag prop">Proposed</span> with the changes above</figcaption><div class="scroll">{sp}</div></figure>'
                    f'{notes_html(gp, D["prop"][kind], name, kind)}</section>')
            worlds = ['familiar'] if kind == 'atomic' else ['Process', 'Substance']
            summary.append(dict(kind=kind, m=m, fid=fid, cur=gc['longest'], prop=gp['longest'], same=same,
                                lag_c='<br>'.join(lag_cell(lag['cur'], w, m) for w in worlds) if lag else '',
                                lag_p='<br>'.join(lag_cell(lag['prop'], w, m) for w in worlds) if lag else '',
                                worlds=worlds))
        sections.append(f'<section class="world"><h2 id="{kind}">{esc(title)}</h2><p class="sub">{esc(sub)}</p>'
                        + '\n'.join(blocks_changed)
                        + '<h4 class="same-h">Unchanged by the proposal</h4>' + '\n'.join(blocks_same) + '</section>')
    # assertions: the words in NOTES must agree with the drawn data
    run = {(s['kind'], s['m']): (s['cur'], s['prop']) for s in summary}
    assert run[('elemental', 'Plenum')] == (3, 2) and run[('atomic', 'Tunnelling')] == (3, 2), run
    assert run[('atomic', 'Wormhole')] == (4, 3) and run[('elemental', 'Wormhole')] == (3, 2), run
    assert run[('atomic', 'Warp')] == (3, 3) and run[('atomic', 'Tachyonic')] == (1, 1) and run[('elemental', 'Tachyonic')] == (2, 2), run
    rows = []
    for s in sorted(summary, key=lambda s: (['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Plenum'].index(s['m']), s['kind'])):
        r = f'<b>{s["cur"]}</b>' if s['same'] else f'<b>{s["cur"]}</b> <span class="arr">→</span> <b class="to">{s["prop"]}</b>'
        w = 'atomic' if s['kind'] == 'atomic' else 'elemental'
        lagc = (f'<td class="num">{s["lag_c"]}</td><td class="num">{s["lag_p"]}</td>' if lag else '')
        rows.append(f'<tr><th scope="row"><a href="#{s["fid"]}">{s["m"]}</a></th><td>{w}</td><td class="num">{r}</td>{lagc}</tr>')
    lag_head = (f'<th scope="col">Turns behind its world’s field, {esc(version)}<br><span class="th-sub">expert / novice / average</span></th>'
                f'<th scope="col">With the changes<br><span class="th-sub">today’s players</span></th>') if lag else ''
    table = (f'<table class="sum"><thead><tr><th scope="col">Method</th><th scope="col">World</th><th scope="col">Ideas in a row<br><span class="th-sub">today → proposed</span></th>{lag_head}</tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table>')
    changes = ''.join(f'<li><b>{esc(short(name[k]))}</b> <span class="who">{esc(ms)}</span><div class="was"><span>now</span> {esc(b)}</div>'
                      f'<div class="will"><span>proposed</span> {esc(a)}</div></li>' for k, b, a, ms in CHANGES)
    page = open(os.path.join(HERE, 'ftl_chains_template.html'), encoding='utf-8').read()
    page = (page.replace('{{VERSION}}', esc(version)).replace('{{TABLE}}', table).replace('{{CHANGES}}', changes)
                .replace('{{SECTIONS}}', '\n'.join(sections)).replace('{{LAGNOTE}}', (
                    f'<p class="small">Turns behind the field: each method’s median victory against the median of all its world’s games, from the saved runs '
                    f'<code>{esc(lag["labels"][0])}</code> and <code>{esc(lag["labels"][1])}</code> (60 games a cell, every game finished; '
                    f'<code>design/simulator/power/results/plenum_tunnelling_20261017.txt</code>). Two rows for the elemental worlds: Process, then Substance.</p>') if lag else ''))
    open(outp, 'w', encoding='utf-8').write(page)
    print('written', outp)


if __name__ == '__main__':
    main()
