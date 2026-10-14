"""Thinning batch 1 (Chemistry): Electrochemistry → Voltaic Pile, Portland Cement → Reinforced Concrete, Crystallography → Periodic Table."""
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read()
def rep(old, new):
    global t; assert t.count(old) == 1, (old[:70], t.count(old)); t = t.replace(old, new)
L = t.split('\n')
for rid in ('CH10', 'CH16', 'CH17'):
    (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; del L[i]
t = '\n'.join(L)
# Electrochemistry → Voltaic Pile
rep('— electroplating makes precious metal go further. Prerequisite for the Telegraph (EL04) and Electrochemistry (CH10).',
    '— electroplating makes precious metal go further; ⟨[+1 Gold] from [Luxury resource] tiles [in all cities]⟩ — every luxury dressed in gold (Electrochemistry, merged here in v3.99: Davy\'s electrolysis was the pile put to work). Prerequisite for the Telegraph (EL04), Cold Fusion (NP10) and Electric Aviation (AE11).')
rep('<after discovering [Electrochemistry]>⟩ (direct current is what electroplating and aluminium smelting run on)',
    '<after discovering [Aluminium Extraction]>⟩ (direct current is what aluminium smelting runs on — the Hall–Héroult cell is electrolysis)')
rep('| NP02 + CH10 (Electrochemistry) |', '| NP02 + EL02 (Voltaic Pile — electrochemistry) |')
rep('| AE03 + EL12 (Room Temp Superconductor) or CH10 (Electrochemistry) + EN10 (Miniaturization) |', '| AE03 + EL12 (Room Temp Superconductor) or EL02 (Voltaic Pile — batteries) + EN10 (Miniaturization) |')
# Portland Cement → Reinforced Concrete
rep('Cast Iron (ME10), Portland Cement (CH16) and Geopolymer Concrete (S09)', 'Cast Iron (ME10) and Geopolymer Concrete (S09)')
rep('| CO04 (Roman Concrete) or CH16 (Portland Cement) + ME12 (Bessemer) | ⟨[+10]% Production when constructing [All] buildings [in all cities]⟩ — steel and concrete build fast and stand hard.',
    '| (CO04 or CH05) + ME12 — Roman Concrete, or the chemistry of Portland cement; and Bessemer steel | ⟨[+10]% Production when constructing [All] buildings [in all cities]⟩ — steel and concrete build fast and stand hard; ⟨Improves movement speed on roads⟩ — the canonical Machinery unique, for cement roads (Portland Cement, merged here in v3.99: reinforced concrete was Portland cement and steel).')
# Crystallography → Periodic Table
rep('**Research Lab**; ⟨[+1 Science] from [Strategic resource] tiles [in all cities]⟩ (you finally know what you are looking at);',
    '**Research Lab**; ⟨[+1 Science] from [Strategic resource] tiles [in all cities]⟩ (you finally know what you are looking at); ⟨[+1 Gold] from [Gems] tiles [in all cities]⟩ — precision cutting, from knowing the crystal (Crystallography, merged here in v3.99);')
rep('| EL03 + CH17 (Crystallography) |', '| EL03 + CH06 (Periodic Table — crystallography) |')
rep('+ CH17 (Crystallography) | Two faces, unequal', '+ CH06 (Periodic Table — crystallography) | Two faces, unequal')
rep('| Total Breakthroughs | ~548 |', '| Total Breakthroughs | ~545 |')
rep('| STANDARD Breakthroughs | ~244 |', '| STANDARD Breakthroughs | ~241 |')
rep('Complete Tech Tree Design Document (v3.98)', 'Complete Tech Tree Design Document (v3.99)')
open(p, 'w', encoding='utf-8').write(t); print('batch 1 applied')
