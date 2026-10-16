"""The sample logs' victory turns as design/simulator/power/victory.py computes them, to check view.js's victory() against.
Run: cd design/simulator/power && bash scratch_run.sh python3 ../../mockups/sim_web/test/check_victory.py"""
import os, sys, json, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '..', 'simulator', 'power')))
import victory as V
for f in sorted(glob.glob(os.path.join(HERE, '..', 'traces', '*.json'))):
    t = json.load(open(f))
    g = dict(cert=t['cert'][0] if t['cert'] else None, built=t['built'], m=t['m'])
    fin = max(g['cert'], g['built'])
    pt = V.prototype_turns(fin, t['econ']); proto = fin + pt
    print(os.path.basename(f), 'victory', V.victory(g, t['econ']), 'proto', pt, 'drive', V.drive_turns(proto, t['econ'], g['m'] in V.EXOTIC))
