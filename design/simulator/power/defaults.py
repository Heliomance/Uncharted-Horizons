"""Where the simulator finds the tech tree, and the finalised design it simulates by default.

TREE is the design document, design/tech_tree.md, which the tools never modify. scratch_run.sh points UH_TREE at
a patched private copy of it for the length of a run (see scratch_patch.py).

FINAL holds the finalised FTL-endgame decisions (design/notes/ftl_decisions_digest.md, §9): every agreed lever and
Wormhole's MS17 row at 4x; since v3.120, the discovery model's safety net: rediscovery on demand (REDISCOVER=0.1) and no
W16 (W16=0); and the simulated players' Endeavours only for revealed ideas that have not occurred (ENDUNOCC=1; since v3.121
the design also allows them on ideas under study, for needs the game situation creates, which the simulated players do
not have: allowed, they lose 0-6 turns of victory).
Since v3.122 (back to base Civ V's game lengths): development's era boundaries at base Civ V's era timings for a good
economy (DEVENDS: the Atomic era from turn 228, the Space era from 264 to 320) with idea windows following those era
lengths (WINTURNS), while the simulated economy keeps its v3.108 calibration (ledger.ERA_END, the era model); prices per
discovery x1.25 in the Modern and Atomic eras and x2 in the Space era (MODERNPRICE, ATOMICPRICE, SPACEPRICE, against the
v3.108 prices); and rivals replayed from a pool made under these settings (POOLTAG=122; make_pool.sh).
Importing this module applies them to any switch that isn't set, so a run simulates the agreed design unless told
otherwise; set a switch to override it, and LEVERS= (empty) to switch every lever off. Every tool that loads the tree imports this module through reach.py.

Run as a script, it prints shell assignments for scratch_run.sh: CANONICAL, and an export for each switch that isn't set.
"""
import os, shlex

CANONICAL = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tech_tree.md'))
FINAL = {'LEVERS': 'abcrwgpnyhukqvVm', 'WROWX': '4',
         'REDISCOVER': '0.1', 'ENDUNOCC': '1', 'W16': '0',   # the safety-net package and no W16 (v3.120, 15 Oct 2026); ENDUNOCC: see above
         'DEVENDS': 'Modern:66231,Atomic:113629,Space:209676', 'WINTURNS': 'Modern:47,Atomic:36,Space:56',   # v3.122: see above
         'MODERNPRICE': '1.25', 'ATOMICPRICE': '1.25', 'SPACEPRICE': '2', 'POOLTAG': '122'}

if __name__ == '__main__':
    print(f'CANONICAL={shlex.quote(CANONICAL)}')
    for key, value in FINAL.items():
        if key not in os.environ:
            print(f'export {key}={shlex.quote(value)}')
else:
    for key, value in FINAL.items():
        os.environ.setdefault(key, value)

TREE = os.environ.get('UH_TREE') or CANONICAL
