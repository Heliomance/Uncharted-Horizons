"""World sets for the thinning pass: the familiar world, and one alternative world per axis branch."""
import sys; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import gen_data as G
from collections import Counter
TAGS = Counter(r['world'] for r in G.ROWS.values())
# the familiar branch each alternative replaces (None = it adds to the familiar world rather than replacing)
AXIS = {'Substance': 'Atomic', 'Process': 'Atomic', 'Miasma': 'Germ', 'Humoral': 'Germ',
        'Caloric': None, 'Vitalist': None, 'Gravitic': None}
ELEMENTAL = {'Substance', 'Process'}   # the two flavours of elemental world: each takes the elemental rows and its own branch
def world_rows(alt=None):
    keep = {None, 'Germ', 'Atomic'}
    if alt:
        keep.add(alt)
        if alt in ELEMENTAL: keep.add('Elemental')
        if AXIS.get(alt): keep.discard(AXIS[alt])
    return {k: r for k, r in G.ROWS.items() if r['world'] in keep}
def set_world(alt=None):
    """point the harness at a world's rows"""
    import harness as H1, harness2 as H2
    rows = world_rows(alt); ids = sorted(rows)
    for mod in (H1, H2):
        mod.ROWS = rows; mod.IDS = ids; mod.FOCUS = {k: rows[k]['focus'] for k in ids}; mod.ERA_I = {k: H1.EO.index(rows[k]['era']) for k in ids}
    H1.ROWS, H1.IDS = rows, ids
    import generator as GN; GN._DEP.clear(); GN._ANC.clear()
    return rows
