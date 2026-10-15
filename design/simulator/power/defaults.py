"""Where the simulator finds the tech tree, and the finalised design it simulates by default.

TREE is the design document, design/tech_tree.md, which the tools never modify. scratch_run.sh points UH_TREE at
a patched private copy of it for the length of a run (see scratch_patch.py).

FINAL holds the finalised FTL-endgame decisions (design/notes/ftl_decisions_digest.md, §9): every agreed lever,
Wormhole's MS17 row at 4x and the Space era's price per discovery at 0.8; and, since v3.120, the discovery model's
safety net: rediscovery on demand (REDISCOVER=0.1), Endeavours only for revealed ideas that have not occurred
(ENDUNOCC=1), and no W16 (W16=0). Importing this module applies them to any
switch that isn't set, so a run simulates the agreed design unless told otherwise; set a switch to override it, and
LEVERS= (empty) to switch every lever off. Every tool that loads the tree imports this module through reach.py.

Run as a script, it prints shell assignments for scratch_run.sh: CANONICAL, and an export for each switch that isn't set.
"""
import os, shlex

CANONICAL = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tech_tree.md'))
FINAL = {'LEVERS': 'abcrwgpnyhukqvVm', 'WROWX': '4', 'SPACEPRICE': '0.8',
         'REDISCOVER': '0.1', 'ENDUNOCC': '1', 'W16': '0'}   # the safety-net package and no W16 (v3.120, 15 Oct 2026)

if __name__ == '__main__':
    print(f'CANONICAL={shlex.quote(CANONICAL)}')
    for key, value in FINAL.items():
        if key not in os.environ:
            print(f'export {key}={shlex.quote(value)}')
else:
    for key, value in FINAL.items():
        os.environ.setdefault(key, value)

TREE = os.environ.get('UH_TREE') or CANONICAL
