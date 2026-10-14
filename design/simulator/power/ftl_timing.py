"""When does a civilisation hold each FTL method's whole prerequisite set? Harness runs per world; one chunk per call."""
import sys, json, os, importlib; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
METHODS = {
 'atomic': {
  'A Warp':        [['RC02'], ['QP08'], ['QP11'], ['MS08'], ['ES08', 'ES06', 'ES12', 'ES14']],
  'B Wormhole':    [['RC02'], ['QP08'], ['QP11'], ['RC04'], ['RC07'], ['MS08'], ['QP12'], ['MA13']],
  'C Hyperspace':  [['QP09'], ['QP08'], ['MA13'], ['ES08', 'ES06', 'ES12', 'ES14']],
  'D Tunnelling':  [['QP02'], ['CP10'], ['MS02'], ['QP07', 'GN10']],
  'E Tachyonic':   [['RC01'], ['RC03'], ['QP05'], ['QP06'], ['QP04']]},
 'elemental': {   # §4's prerequisite table, v3.110
  'A Warp':        [['RC02'], ['QM-E27'], ['QM-E06'], ['MS08'], ['QM-E05', 'ES15']],
  'B Wormhole':    [['RC02'], ['QM-E27'], ['QM-E06'], ['RC04'], ['RC07'], ['MS08'], ['QM-E13'], ['MA13']],
  'C Hyperspace':  [['QM-E12'], ['QM-E27'], ['MA13'], ['QM-E05', 'ES15']],
  'E Tachyonic':   [['RC01'], ['RC03'], ['QM-E04'], ['QM-E17'], ['QM-E08']],
  'F Plenum':      [['QM-E27'], ['MS02'], ['QM-E19'], ['QM-E05', 'ES15']]}}   # v3.111: the sail is Fine Structuring
def run_chunk(alt, seeds, out):
    import gen_data as G, harness as H1, harness2 as H, worlds as W
    W.set_world(alt)
    sc = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/premium_sweep.json'))['4.0']['scale']
    cfg = dict(model='Pmom', routing='spill', spread_floor=0.0, compress=4.0, window={'STANDARD': 0.5, 'UNCOMMON': 1.0, 'RARE': 1.0, 'UNIQUE': 1.0}, premium=4.0, scale=sc)
    kind = 'atomic' if alt is None else 'elemental'
    res = json.load(open(out)) if os.path.exists(out) else {}
    for s in seeds:
        have, log = H.run(H.P(**cfg), 5000 + s)
        turn = {k: t for k, (t, d) in have.items()}
        row = {}
        for m, req in METHODS[kind].items():
            ts = [min((turn[o] for o in grp if o in turn), default=None) for grp in req]
            row[m] = None if any(x is None for x in ts) else max(ts)
        res[str(s)] = row
    json.dump(res, open(out, 'w'))
    return len(res)
if __name__ == '__main__':
    alt = None if sys.argv[1] == 'familiar' else sys.argv[1]
    a, b = int(sys.argv[2]), int(sys.argv[3])
    print(sys.argv[1], 'runs stored:', run_chunk(alt, range(a, b), f'/home/user/Uncharted-Horizons/design/simulator/power/ftl_timing_{sys.argv[1]}.json'))
