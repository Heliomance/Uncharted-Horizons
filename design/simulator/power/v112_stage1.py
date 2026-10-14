"""v3.112, stage 1: the structure of the agreed FTL endgame (rows, prerequisites, tiers, prices) on a fresh copy of v3.111.
Source of truth for structure: scratch_patch.py with the final design's switches (LEVERS=abcrwgpnyhukqvVm), prices from w7f.py,
plus the decisions taken after the last measurement (MS17 as Transformation Media, QM-E08 needing EL07).
Effects of new rows are left as '(effect: stage N)' placeholders; later stages fill them from the direction document.
Writes wip/tt_v112_wip.md (outside the restore scripts' view)."""
import re
SRC = '/home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_v111.md'
OUT = '/home/user/Uncharted-Horizons/design/simulator/outputs/wip/tt_v112_wip.md'
L = open(SRC, encoding='utf-8').read().split('\n')

def row(rid):
    hits = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')]
    assert len(hits) == 1, (rid, len(hits))
    return hits[0]
def cells(rid): return L[row(rid)].split(' | ')
def setcell(rid, col, val):
    i = row(rid); c = L[i].split(' | '); c[col] = val; L[i] = ' | '.join(c)
def getcell(rid, col): return cells(rid)[col]
def add_after(anchor, rid, name, tier, era, pre, eff, note=''):
    assert not any(l.startswith(f'| {rid} |') for l in L), f'{rid} already exists'
    L.insert(row(anchor) + 1, f'| {rid} | **{name}** | {tier} | {era} | {pre} | {eff} | {note} |')
def move_row(rid, after):
    i = row(rid); line = L.pop(i); L.insert(row(after) + 1, line)

S2 = '(effect: stage 2, from the W18 table)'; S3 = '(effect: stage 3)'

# --- the evidence and build rows of the FTL redesign (W1, W4, W14) ---
setcell('QM-E23', 2, 'STANDARD'); setcell('QM-E23', 4, 'QM-E19 + RK07 + AE14')
setcell('QP11', 4, 'QP08 + QP12 (Casimir Effect Amplification) + MS02 (Nanotechnology)')
setcell('QP14', 4, '(QP07 or GN10) + RK16')
setcell('RC05', 4, 'RC02 + RK05 + (QP08 or QM-E27)')
setcell('RC06', 4, 'RC02 + RK05 + (QP08 or QM-E27)')                       # alongside RC05, not behind it
setcell('CP10', 4, '((QP07 + CP01) or GN10) + CP16')
add_after('RC10', 'RC11', 'Gravitational Leakage Survey', 'STANDARD', 'Space', 'RC03 + SE02', S3)
add_after('CP15', 'CP16', 'Planetary Data Networks', 'STANDARD', 'Space', 'CP04 + CP07', S2)
add_after('CP16', 'CP21', 'Macroscopic Quantum Control', 'STANDARD', 'Space', 'CP10', S2)
add_after('AE12', 'AE14', 'Aerospace Industry', 'STANDARD', 'Space', 'AE04 + MS01', S2)
add_after('AE14', 'AE20', 'Current Rigging', 'STANDARD', 'Space', 'QM-E23 + AE14', S2)
setcell('MS02', 2, 'CORE')                                                  # lever b
assert 'QM-E27 (Plenum Gravitation) + (CH21 or CH23)' in L[row('QM-E06')]
setcell('QM-E06', 4, 'QM-E27 (Plenum Gravitation) + (CH21 or CH23 or MS02)')  # lever c
# --- the signature fields' engineering rows (W18) and round two ---
add_after('ES14', 'ES22', 'Smart Grid', 'STANDARD', 'Space', 'EL07 + CP04', S2)
add_after('ES22', 'ES18', 'Superconducting Energy Storage', 'STANDARD', 'Space', 'EL11 + EL07', S2)   # round two: no Smart Grid gate
add_after('MA14', 'MA15', 'Optimisation Theory', 'STANDARD', 'Space', 'MA13 + MA09', S2)
add_after('MA15', 'MA19', 'Higher-Dimensional Geometry', 'STANDARD', 'Space', 'MA15 + MA13', S2)
add_after('NP11', 'NP15', 'Superconducting Storage Rings', 'STANDARD', 'Space', 'EL11 + (ES06 or ES14 or ES08)', S2)  # round two
add_after('TH03', 'TH20', 'Boundary Ring', 'STANDARD', 'Space', 'QM-E05 + EL11', S2)
add_after('MS08', 'MS17', 'Transformation Media', 'STANDARD', 'Space', 'MS08 + (QP12 or QM-E13)', S3)   # replaces Throat Stabilisation
# --- the signature pools (W18), as settled in the direction document ---
P = lambda a, r, n, pre: add_after(a, r, n, 'STANDARD', 'Space', pre, S2)
P('CP16','CP17','AI Advisory Council','CP16'); P('CP17','CP18','Autonomous Logistics','CP16'); P('CP18','CP19','Cyber Operations','CP16 + CP06')
P('CP19','CP20','Digital Twins','CP16'); P('CP20','CP22','Autonomous Economy','CP17 + CP18')
P('ES18','ES17','Grid-Scale Storage','ES22'); P('ES17','ES19','Electrified Industry','ES22'); P('ES19','ES20','Continental Interconnects','ES22 + ES17')
P('ES20','ES21','Global Supergrid','ES20 + ES19'); move_row('QM-E07', 'ES21')
P('MS17','MS10','Structural Nanomaterials','MS02 + MS01'); P('MS10','MS11','Field Repair Systems','MS10'); P('MS11','MS12','Signature Management','MS10')
P('MS12','MS13','Adaptive Armour','MS10'); P('MS13','MS16','Self-Sealing Hulls','MS10'); P('MS16','MS15','Modular Platforms','MS13 + MS11')
P('MA19','MA16','Operations Research','MA15'); P('MA16','MA17','Lifecycle Engineering','MA15'); P('MA17','MA18','Logistics Optimisation','MA15')
P('MA18','MA22','Auction Theory','MA15'); P('MA22','MA23','Post-Quantum Cryptography','MA15 + MA07'); P('MA23','MA20','Computational Proof','MA15 + CP01')
P('MA20','MA21','Automated Mathematics','MA20 + MA19')
P('NP15','NP12','Particle Laboratories','NP02 + QP04'); P('NP12','NP13','Hardened Shelters','NP12'); P('NP13','NP16','Particle-Beam Weapons','NP15')
P('NP16','NP17','Particle-Beam Artillery','NP16 + NP13')
P('TH20','TH15','Waste-Heat Recovery','TH03 + TH05'); P('TH15','TH16','Heat Pump Networks','TH15'); P('TH16','TH17','Supercritical Power Cycles','TH15')
P('TH17','TH18','Deep Cryogenics','TH15 + TH02'); P('TH18','TH21','Atmospheric Heat Management','TH17 + TH18'); P('TH21','TH22','Geoengineering Programme','TH21 + TH16')
P('AE14','AE15','Jet-Stream Navigation','AE14'); P('AE15','AE16','Airborne Assault Doctrine','AE14'); P('AE16','AE17','Air Mobility','AE14')
P('AE17','AE18','Sky Carriers','AE14 + AE12'); P('AE18','AE19','Suborbital Point-to-Point Transport','AE16 + AE15'); move_row('QM-E23', 'AE20')
# --- the theory phase (W17): each unified theory needs its ontology's great instrument, and the instruments are CORE ---
setcell('QP08', 4, 'QP05 + RC02 (General Relativity) + QP04 (Particle Accelerator)')
setcell('QM-E27', 4, 'QM-E04 (Unified Field) + RC02 (General Relativity) + QM-E08 (Boundary Furnace)')
setcell('QP04', 2, 'CORE'); setcell('QM-E08', 2, 'CORE')
pre = getcell('QM-E08', 4)
if 'EL07' not in pre: setcell('QM-E08', 4, pre + ' + EL07 (Power Grid)')   # decided: as its mirror QP04 does
# --- prices (multipliers on the era's base Insight threshold, §1.2), as measured ---
PRICE = {**{k: 2.0 for k in ('CP10',)},
         **{k: 2.5 for k in ('CP17','CP18','CP19','CP20','CP15','CP09','ES22','ES18','ES14','ES08','ES17','ES19','ES20','ES11',
                             'MS10','MS11','MS12','MS13','MS16','MA15','MA16','MA17','MA18','MA20','MA22','MA23',
                             'NP11','NP12','NP13','NP15','NP16','NP-F03','TH15','TH16','TH17','TH18','TH21','AE15','AE16','AE17','AE18','QM-E23')},
         **{k: 4.0 for k in ('CP22','CP12','ES21','ES12','QM-E07','MS15','MS07','MS17','MA21','NP17','NP09','NP-F04','TH20','TH22','AE19')}}
for k, x in PRICE.items():
    c = getcell(k, 4)
    c = re.sub(r'\s*—?\s*\*\*cost ×[0-9.]+\*\*', '', c)
    setcell(k, 4, f'{c} — **cost ×{x:g}**')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print(f'stage 1 written: {OUT}; priced rows {len(PRICE)}')
