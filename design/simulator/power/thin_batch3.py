"""Thinning batch 3: the tree's remaining stepping stones. Apiculture is cut outright; ten rows merge into their hosts."""
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read()
def rep(old, new):
    global t; assert t.count(old) == 1, (old[:80], t.count(old)); t = t.replace(old, new)
def unlocks(rid):
    l = [x for x in t.split('\n') if x.startswith(f'| {rid} |')][0]; return l.split(' | ')[5]
def append(host, text):
    global t
    L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {host} |')]
    cells = L[i].split(' | '); cells[5] = cells[5].rstrip() + ' ' + text; L[i] = ' | '.join(cells); t = '\n'.join(L)
src = {k: unlocks(k) for k in ('TX04', 'MI05B', 'FA08', 'OP05', 'TR07', 'GN01', 'TX07', 'AE06', 'MS04', 'OP06')}
import re
uq = lambda k: '; '.join(re.findall(r'⟨[^⟩]*⟩', src[k]))
L = t.split('\n')
for rid in ('AE06', 'AH09', 'FA08', 'GN01', 'MS04', 'OP05', 'OP06', 'TX04', 'TX07', 'TR07', 'MI05B'):
    (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; del L[i]
t = '\n'.join(L)
append('TX01', f'Wool spun and worn: {uq("TX04")} (Wool Processing, merged here in v3.101).')
append('F03', f'Wood tar, the kiln\'s by-product: {uq("MI05B")} — tarred roads, caulked hulls (Pitch and Tar, merged here in v3.101).')
append('MC03', f'{uq("FA08")} — the seed drill is a geared machine, Han-era in China (Mechanical Seed Drill, merged here in v3.101).')
append('OP02', f'{uq("OP05")} — the projected image, traced (Camera Obscura, merged here in v3.101: the same lenses, the same era).')
append('MA06', f'{uq("TR07")} — risk, priced and pooled (Insurance, merged here in v3.101).')
append('GN02', f'{uq("GN01")} — breeding by rule, not by luck (Mendelian Genetics, merged here in v3.101).')
append('CH11', f'{uq("TX07")} — mass-produced uniforms and kit: nylon is a polymer (Synthetic Fibers, merged here in v3.101).')
append('AE04', f'{uq("AE06")} — past the sound barrier (Supersonic Flight, merged here in v3.101).')
append('MS02', f'{uq("MS04")} — the strongest cable ever spun (Graphene Production, merged here in v3.101).')
append('CP03', f'{uq("OP06")} — prices move at the speed of light, on fibre (Fiber Optics, merged here in v3.101).')
rep('| F03 + MI05B (Pitch and Tar) + MI04 (Sulfur Mining) |', '| F03 (Charcoal Production — wood tar) + MI04 (Sulfur Mining) |')
rep('| TR07 + MA09 (Statistics) |', '| TR05 + MA06 (Probability Theory — insurance) + MA09 (Statistics) |')
rep('| GN01 + CH07 + OP04 (Microscope) |', '| MD05 (Germ Theory validated) + FA03 (Selective Breeding) + CH07 + OP04 (Microscope) |')
rep('| TX07 + CH07 |', '| CH11 (Polymer Science — synthetic fibre) + CH07 |')
rep('| AE06 + TH05 |', '| AE04 (Jet Engine — supersonic) + MS01 (Composite Materials) + TH05 |')
rep('| MS04 + SE02 (Orbital Assembly) |', '| MS02 (Nanotechnology — graphene) + SE02 (Orbital Assembly) |')
rep('trade breakthroughs (TR06, TR07).', 'trade breakthroughs (TR06).')
rep('MS02 (Nanotechnology) and MS04 (Graphene) are reached via', 'MS02 (Nanotechnology, with Graphene merged in) is reached via')
rep('| Total Breakthroughs | ~533 |', '| Total Breakthroughs | ~522 |')
rep('| STANDARD Breakthroughs | ~231 |', '| STANDARD Breakthroughs | ~220 |')
rep('Complete Tech Tree Design Document (v3.100)', 'Complete Tech Tree Design Document (v3.101)')
open(p, 'w', encoding='utf-8').write(t); print('batch 3 applied')
