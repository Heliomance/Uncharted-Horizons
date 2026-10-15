"""Where the simulator finds the tech tree, and the finalised design it simulates by default.

TREE is the design document, design/tech_tree.md, which the tools never modify. scratch_run.sh points UH_TREE at
a patched private copy of it for the length of a run (see scratch_patch.py).

FINAL holds the finalised FTL-endgame decisions (design/notes/ftl_decisions_digest.md, §9): every agreed lever and
Wormhole's MS17 row at 4x; since v3.120, the discovery model's safety net: rediscovery on demand (REDISCOVER=0.1) and no
W16 (W16=0); and the simulated players' Endeavours only for revealed ideas that have not occurred (ENDUNOCC=1; since v3.121
the design also allows them on ideas under study, for needs the game situation creates, which the simulated players do
not have: allowed, they lose 0-6 turns of victory).
Since v3.122 (back to base Civ V's game lengths): development's late era boundaries at base Civ V's era timings for a
good economy (DEVENDS: the Atomic era from turn 228, the Space era from 264 to 320) with idea windows following the era
lengths (WINTURNS), while the simulated economy keeps its v3.108 calibration (ledger.ERA_END, the era model).
Since v3.123 (parity with base Civ V's science victory, and a smoother early pace): the Modern, Atomic and Space prices back
at their v3.108 values (MODERNPRICE, ATOMICPRICE, SPACEPRICE 1; v3.122 had 1.25, 1.25 and 2, which lengthened the science
victory by 22-32 turns); the Ancient era's price x1.5 with its span to match (ERAPRICE), and the Primitive span x1.3 at its
old price, so that development enters the Ancient era about when civilisations do (smooth.py Ancient=1.5
span.Primitive=1.3, which also gives DEVENDS and WINTURNS for every era); and rivals replayed from a pool made under these
settings (POOLTAG=123; make_pool.sh).
Since v3.124 (three merges, two cuts, five demotions to UNCOMMON): Competing Solutions modelled (COMPETE=1, competing.py):
an alternative costs its x1.5 detour margin while its primary exists in the world, and a civilisation that discovers the
primary first never develops the alternative; the Space era's price x1.05, which re-centres the science victory on base
Civ V's after the merges shortened it (all 15 conditions: 305 / 307 / 379; at x1, 301 / 305 / 378); rivals made under
these settings (POOLTAG=124). Since v3.125 (Ring Fortress merged into Reinforced Concrete): rivals made under v3.125's tree
(POOLTAG=125); all 15 conditions 304 / 307 / 381.
Importing this module applies them to any switch that isn't set, so a run simulates the agreed design unless told
otherwise; set a switch to override it, and LEVERS= (empty) to switch every lever off. Every tool that loads the tree imports this module through reach.py.

Run as a script, it prints shell assignments for scratch_run.sh: CANONICAL, and an export for each switch that isn't set.
"""
import os, shlex

CANONICAL = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tech_tree.md'))
FINAL = {'LEVERS': 'abcrwgpnyhukqvVm', 'WROWX': '4',
         'REDISCOVER': '0.1', 'ENDUNOCC': '1', 'W16': '0',   # the safety-net package and no W16 (v3.120, 15 Oct 2026); ENDUNOCC: see above
         'DEVENDS': 'Primitive:194,Ancient:1052,Classical:2590,Medieval:6859,Early_Modern:23900,Modern:66231,Atomic:113629,Space:209676',
         'WINTURNS': 'Primitive:33,Ancient:36,Classical:28,Medieval:36,Early_Modern:49,Modern:46,Atomic:36,Space:56',   # v3.122, v3.123: see above
         'ERAPRICE': 'Ancient:1.5', 'MODERNPRICE': '1', 'ATOMICPRICE': '1', 'SPACEPRICE': '1.05', 'POOLTAG': '125',
         'COMPETE': '1'}   # v3.124: Competing Solutions' margins and lock-outs (competing.py)

if __name__ == '__main__':
    print(f'CANONICAL={shlex.quote(CANONICAL)}')
    for key, value in FINAL.items():
        if key not in os.environ:
            print(f'export {key}={shlex.quote(value)}')
else:
    for key, value in FINAL.items():
        os.environ.setdefault(key, value)

TREE = os.environ.get('UH_TREE') or CANONICAL
