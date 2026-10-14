"""Thinning batch 5: Modern-era skeleton merges — eight rows into their natural partners."""
p = '/home/user/Uncharted-Horizons/design/simulator/tt.md'; t = open(p, encoding='utf-8').read()
def rep(old, new):
    global t; assert t.count(old) == 1, (old[:80], t.count(old)); t = t.replace(old, new)
def append(host, text):
    global t
    L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {host} |')]
    cells = L[i].split(' | '); cells[5] = cells[5].rstrip() + ' ' + text; L[i] = ' | '.join(cells); t = '\n'.join(L)
def set_pre(host, new):
    global t
    L = t.split('\n'); (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {host} |')]
    cells = L[i].split(' | '); cells[4] = new; L[i] = ' | '.join(cells); t = '\n'.join(L)
L = t.split('\n')
for rid in ('EL05', 'EL13', 'EN05', 'TH04', 'TH06', 'MA10', 'RK01', 'ES04'):
    (i,) = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]; del L[i]
t = '\n'.join(L)
# Electric Motor → Electric Generator
append('EL06', '⟨[-25]% construction time for [Railroad] improvements⟩ — electric traction: the motor is the generator run backwards (Electric Motor, merged here in v3.103).')
set_pre('AE02', 'AE01 + MC09 or EL06 (Electric Generator — the motor)')
rep('| RK02 + EL05 + (QP03 Quantum Electrodynamics,', '| RK02 + EL06 (Electric Generator — the motor) + (QP03 Quantum Electrodynamics,')
rep('Electromagnetism (EL03) reveals the Telegraph, Electric Motor, and Generator.', 'Electromagnetism (EL03) reveals the Telegraph and the Generator (with its motor).')
# Telephone → Wireless Transmission
append('EL09', '**Telephone Exchange**ⁿ [375/2; +2 Gold; ⟨[+1 Gold] from each Trade Route⟩] — Bell and Marconi: telecommunication by wire and without (Telephone, merged here in v3.103).')
set_pre('EL09', 'EL03 + MA05 (Calculus) + MC10 (Precision Machining)')
# Television → Radio
append('EN11', '⟨[+2 Gold] from all [Broadcast Tower] buildings⟩ — advertising revenue; **Sydney Opera House**, **CN Tower** (world wonders); ⟨Resting point for Influence with City-States is increased by [10]⟩ — soft power, broadcast by sound and then by picture (Television, merged here in v3.103, with Mass Media merged into it in v3.100).')
set_pre('EN11', 'EN01 + EL09 + OP02 (Lens Grinding)')
rep('| Sydney Opera House | Ecology | **EN05** |', '| Sydney Opera House | Ecology | **EN11** |')
rep('| CN Tower | Telecommunications | **EN05** |', '| CN Tower | Telecommunications | **EN11** |')
rep('Prerequisite for Radar (EN04), Television (EN05) and Radio (EN11).', 'Prerequisite for Radar (EN04) and Radio (EN11, with television).')
# Heat Exchanger → Turbine Design
append('TH03', '⟨[+1 Happiness] in cities on [Snow] tiles⟩ (district heating) — turbines and heat exchangers, the steam plant\'s two halves; prerequisite for reactors (Heat Exchanger, merged here in v3.103).')
set_pre('TH03', 'TH01 + MC03 (Gearing) + ME12 (Bessemer)')
rep('| NP03 + TH04 |', '| NP03 + TH03 (Turbine Design — the heat exchanger) |')
rep('| NP04 + EL11 + TH04 |', '| NP04 + EL11 + TH03 (Turbine Design — the heat exchanger) |')
rep('| QM-E02 (Bound-Energy Release) + TH04 |', '| QM-E02 (Bound-Energy Release) + TH03 (Turbine Design — the heat exchanger) |')
# Cryogenics → Refrigeration
append('TH02', '⟨[+1 Gold] from all [Factory] buildings⟩ — industrial gases, liquefied and sold: Linde built the refrigerator and then liquefied air. Liquid gases: rocket oxidiser (RK02), the superconductor path (EL11), cold storage (MD13) (Cryogenics, merged here in v3.103).')
set_pre('TH02', 'TH01 + CH02 (Acid/Base) + CH06 (Periodic Table)')
rep('| TH06 (Cryogenics) + EL03 |', '| TH02 (Refrigeration — cryogenics) + EL03 |')
rep('| MD11 + TH06 (Cryogenics) |', '| MD11 + TH02 (Refrigeration — cryogenics) |')
rep('Liquid helium also opened low-temperature physics: Cryogenics (TH06) and', 'Liquid helium also opened low-temperature physics: Refrigeration (TH02, which now holds Cryogenics) and')
# Set Theory → Topology
append('MA13', '⟨[-10]% maintenance cost for [All] buildings [in all cities]⟩ — administration by set and rule: Cantor and Poincaré, the new mathematics of the same decades (Set Theory / Formal Logic, merged here in v3.103).')
set_pre('MA13', 'MA08 + MA03 (Basic Algebra) + PH01 (Formal Logic)')
rep('| CP02 + MA10 (Set Theory) |', '| CP02 + MA13 (Topology — set theory) |')
rep('| QP01 + MA05 + MA10 |', '| QP01 + MA05 + MA13 (Topology — set theory) |')
rep('+ MA10 (Set Theory / Formal Logic) |', '+ MA13 (Topology — set theory) |')
# Solid Fuel Rocket → Rocket Propellant
append('CH13', '**Rocket Artillery**, **Mobile SAM** (units — canonical Rocketry; Rocket Artillery requires **Aluminum**). The first rockets are weapons, made from the propellant itself (Solid Fuel Rocket, merged here in v3.103).')
rep('| RK01 + TH01 + (CH09 or CH09-W) |', '| CH13 (Rocket Propellant — solid-fuel rockets) + TH01 + (CH09 or CH09-W) |')
rep('| Rocket Artillery | Rocketry | **RK01** |', '| Rocket Artillery | Rocketry | **CH13** |')
rep('| Mobile SAM | Rocketry | **RK01** |', '| Mobile SAM | Rocketry | **CH13** |')
# Hydroelectric Dam → Dam Construction
rep('Prerequisite for the Hydro Plant (ES04).', '**Hydro Plant** (canonical — requires **Aluminum**, must be on a River, +1 Production from River tiles; not a grid plant, so it stands beside one, as in Civ V) — the dam and its turbines (Hydroelectric Dam, merged here in v3.103).')
set_pre('WM06', 'WM02 (Aqueduct — flood control) + CO11 (Reinforced Concrete) + EL06 (Electric Generator)')
rep('| Hydro Plant | Electricity | **ES04** |', '| Hydro Plant | Electricity | **WM06** |')
rep('| Total Breakthroughs | ~514 |', '| Total Breakthroughs | ~506 |')
rep('| CORE Breakthroughs | ~147 |', '| CORE Breakthroughs | ~144 |')
rep('| STANDARD Breakthroughs | ~215 |', '| STANDARD Breakthroughs | ~210 |')
rep('Complete Tech Tree Design Document (v3.102)', 'Complete Tech Tree Design Document (v3.103)')
open(p, 'w', encoding='utf-8').write(t); print('batch 5 applied')
