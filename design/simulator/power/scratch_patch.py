"""Apply the agreed FTL redesign (as it affects the evidence) to a run's private copy of the tree, $UH_TREE, for
measurement. scratch_run.sh makes the copy from the design document and deletes it afterwards."""
import os, sys
import defaults   # the finalised design's switches, wherever they aren't set
p = os.environ.get('UH_TREE', '')
if not p or os.path.realpath(p) == os.path.realpath(defaults.CANONICAL):
    sys.exit('scratch_patch.py edits a copy of the design document, never the document: run it through scratch_run.sh')
L=open(p,encoding='utf-8').read().split('\n')
LEAK=os.environ.get('LEAK','SE02')   # the leakage survey's Space-era prerequisite (variant switch)
def row(rid):
    (i,)=[n for n,l in enumerate(L) if l.startswith(f'| {rid} |')]; return i
def setcell(rid,col,val):
    i=row(rid); c=L[i].split(' | '); c[col]=val; L[i]=' | '.join(c)
def add_after(anchor, rid, name, tier, era, pre, eff):
    if any(l.startswith(f'| {rid} |') for l in L): return   # v3.112+: the canonical tree already holds the agreed rows
    L.insert(row(anchor)+1, f'| {rid} | **{name}** | {tier} | {era} | {pre} | {eff} | |')
setcell('QM-E23',2,'STANDARD'); setcell('QM-E23',4,'QM-E19 + RK07 + AE14')
setcell('QP11',4,'QP08 + QP12 (Casimir Effect Amplification) + MS02 (Nanotechnology)')
setcell('QM-E27',4,'QM-E04 (Unified Field) + RC02 (General Relativity) + MA13 (Topology)')
setcell('QP14',4,'(QP07 or GN10) + RK16')
setcell('RC05',4,'RC02 + RK05 + (QP08 or QM-E27)')
setcell('CP10',4,'((QP07 + CP01) or GN10) + CP16')
add_after('RC10','RC11','Gravitational Leakage Survey','STANDARD','Space',f'RC03 + {LEAK}','(scratch)')
add_after('CP15','CP16','Planetary Data Networks','STANDARD','Space','CP04 + CP07','(scratch)')
add_after('CP16','CP21','Macroscopic Quantum Control','STANDARD','Space','CP10','(scratch)')
add_after('AE12','AE14','Aerospace Industry','STANDARD','Space','AE04 + MS01','(scratch)')
add_after('AE14','AE20','Current Rigging','STANDARD','Space','QM-E23 + AE14','(scratch)')
LEVERS=os.environ.get('LEVERS','')   # variant switches: b = MS02 becomes CORE; c = QM-E06 also accepts MS02 (a lives in w7c.py)
if 'b' in LEVERS: setcell('MS02',2,'CORE')
if 'c' in LEVERS:
    setcell('QM-E06',4,'QM-E27 (Plenum Gravitation) + (CH21 or CH23 or MS02)')
# the signature foci's engineering rows (W18)
add_after('ES14','ES22','Smart Grid','STANDARD','Space','EL07 + CP04','(scratch)')
add_after('ES22','ES18','Superconducting Energy Storage','STANDARD','Space','ES22 + EL11','(scratch)')
add_after('MA14','MA15','Optimisation Theory','STANDARD','Space','MA13 + MA09','(scratch)')
add_after('MA15','MA19','Higher-Dimensional Geometry','STANDARD','Space','MA15 + MA13','(scratch)')
add_after('NP11','NP15','Superconducting Storage Rings','STANDARD','Space','NP11 + EL11','(scratch)')
add_after('TH03','TH20','Boundary Ring','STANDARD','Space','QM-E05 + EL11','(scratch)')
# levers (variant switch LEVERS): b = MS02 becomes CORE; c = QM-E06 also accepts MS02
LEVERS=os.environ.get('LEVERS','')
if 'b' in LEVERS: setcell('MS02',2,'CORE')
if 'c' in LEVERS: setcell('QM-E06',4,'QM-E27 (Plenum Gravitation) + (CH21 or CH23 or MS02)')
if 'r' in LEVERS: setcell('RC06',4,'RC02 + RK05 + (QP08 or QM-E27)')
if 'w' in LEVERS: add_after('MS08','MS17','Transformation Media','STANDARD','Space','MS08 + (QP12 or QM-E13)','(scratch)')   # Wormhole's engineering row
if 'g' in LEVERS: setcell('ES18',4,'EL11 + EL07')                                  # Warp: no Smart Grid gate
if 'n' in LEVERS: setcell('NP15',4,'EL11 + (ES06 or ES14 or ES08)')
def move_row(rid, after):   # move an existing row into another field's section
    i = [n for n, l in enumerate(L) if l.startswith(f'| {rid} |')][0]; line = L.pop(i)
    j = [n for n, l in enumerate(L) if l.startswith(f'| {after} |')][0]; L.insert(j + 1, line)
if 'q' in LEVERS:   # the W18 signature pools, as settled in the direction document
    S = lambda a, r, n, pre, t='STANDARD': add_after(a, r, n, t, 'Space', pre, '(scratch pool)')
    S('CP16','CP17','AI Advisory Council','CP16'); S('CP17','CP18','Autonomous Logistics','CP16'); S('CP18','CP19','Cyber Operations','CP16 + CP06')
    S('CP19','CP20','Digital Twins','CP16'); S('CP20','CP22','Autonomous Economy','CP17 + CP18')
    S('ES18','ES17','Grid-Scale Storage','ES22'); S('ES17','ES19','Electrified Industry','ES22'); S('ES19','ES20','Continental Interconnects','ES22 + ES17')
    S('ES20','ES21','Global Supergrid','ES20 + ES19'); move_row('QM-E07','ES21')
    S('MS08','MS10','Structural Nanomaterials','MS02 + MS01'); S('MS10','MS11','Field Repair Systems','MS10'); S('MS11','MS12','Signature Management','MS10')
    S('MS12','MS13','Adaptive Armour','MS10'); S('MS13','MS16','Self-Sealing Hulls','MS10'); S('MS16','MS15','Modular Platforms','MS13 + MS11')
    S('MA19','MA16','Operations Research','MA15'); S('MA16','MA17','Lifecycle Engineering','MA15'); S('MA17','MA18','Logistics Optimisation','MA15')
    S('MA18','MA22','Auction Theory','MA15'); S('MA22','MA23','Post-Quantum Cryptography','MA15 + MA07'); S('MA23','MA20','Computational Proof','MA15 + CP01')
    S('MA20','MA21','Automated Mathematics','MA20 + MA19')
    S('NP15','NP12','Particle Laboratories','NP02 + QP04'); S('NP12','NP13','Hardened Shelters','NP12'); S('NP13','NP16','Particle-Beam Weapons','NP15')
    S('NP16','NP17','Particle-Beam Artillery','NP16 + NP13')
    S('TH20','TH15','Waste-Heat Recovery','TH03 + TH05'); S('TH15','TH16','Heat Pump Networks','TH15'); S('TH16','TH17','Supercritical Power Cycles','TH15')
    S('TH17','TH18','Deep Cryogenics','TH15 + TH02'); S('TH18','TH21','Atmospheric Heat Management','TH17 + TH18'); S('TH21','TH22','Geoengineering Programme','TH21 + TH16')
    S('AE14','AE15','Jet-Stream Navigation','AE14'); S('AE15','AE16','Airborne Assault Doctrine','AE14'); S('AE16','AE17','Air Mobility','AE14')
    S('AE17','AE18','Sky Carriers','AE14 + AE12'); S('AE18','AE19','Suborbital Point-to-Point Transport','AE16 + AE15'); move_row('QM-E23','AE20')
if 'v' in LEVERS:   # each unified theory also needs its ontology's big instrument
    setcell('QP08',4,'QP05 + RC02 (General Relativity) + QP04 (Particle Accelerator)')
    setcell('QM-E27',4,'QM-E04 (Unified Field) + RC02 (General Relativity) + MA13 (Topology) + QM-E08 (Boundary Furnace)')   # W6 keeps MA13 (v3.112)
if 'V' in LEVERS:   # ...and the two instruments become CORE, so a CORE theory never waits on a missable idea
    setcell('QP04',2,'CORE'); setcell('QM-E08',2,'CORE')
if 'z' in LEVERS:   # ASSUMED Space-era pools for the agreed non-FTL fields (deferred entry 24): sizes and shape only, for measurement
    import re as _re
    EO_ = ['Primitive', 'Ancient', 'Classical', 'Medieval', 'Early Modern', 'Modern', 'Atomic', 'Space']
    def field_rows(fname):
        out, cur = [], None
        for l in L:
            if l.startswith('### FOCUS:'): cur = l.lower()
            elif cur and fname.lower() in cur and _re.match(r'^\| [A-Z]{2,3}(?:-[A-Z]+)?\d+[A-Z]? \|', l):
                c = [s.strip() for s in l.split('|')[1:-1]]; out.append((c[0], c[2], c[3]))
        return out
    PLAN = [('Warfare', 8), ('Optics', 8), ('Philosophy', 8), ('Social Organization', 8), ('Trade', 8), ('Genetics', 8), ('Medicine', 8), ('Seafaring', 8),
            ('Water Management', 8), ('Mechanics', 8), ('Farming', 3), ('Mining', 3), ('Construction', 3)]
    for fi, (fname, target) in enumerate(PLAN, start=1):
        rows = field_rows(fname); n = target - sum(1 for r in rows if r[2] == 'Space')
        if n <= 0 or not rows: continue
        gate = max((r for r in rows if r[1] in ('CORE', 'STANDARD') and r[2] in EO_[:7]), key=lambda r: EO_.index(r[2]))[0]
        ids = [f'ZZ{fi}{j:02d}' + ('C' if (j == n and n >= 3) else '') for j in range(1, n + 1)]
        add_after(rows[-1][0], ids[0], f'{fname} Space entry (assumed)', 'STANDARD', 'Space', f'{gate} + RK03', '(assumed pool)')
        prev = ids[0]
        for j, rid in enumerate(ids[1:], start=2):
            pre = (f'{ids[1]} + {ids[2]}' if n >= 4 else f'{ids[0]} + {ids[1]}') if rid.endswith('C') else ids[0]
            add_after(prev, rid, f'{fname} Space {j} (assumed)', 'STANDARD', 'Space', pre, '(assumed pool)'); prev = rid
                # atomic Tachyonic shaped like its elemental mirror   # dark energy waits on expansion surveys, not on RC05
# EARLYFIX=1: the prerequisites proposed by the review of rows available two or more eras early
# (design/notes/early_rows_review.md), for measurement; each goes in before any commentary after a dash
EARLY = {'ME08': ['WM05'], 'MI08': ['CH01'], 'F07': ['MI08'], 'MC04': ['WM05'], 'MI07': ['MC08'], 'O07': ['O06'],
         'AE09': ['AE01'], 'WM11': ['TR06'], 'MD04': ['PH04'], 'TR05': ['SO11'], 'MA05': ['PH04'], 'MA06': ['SO11'],
         'PH04': ['CU06'], 'PH09': ['PH14'], 'PH10': ['EN01'], 'MA11': ['CP01'], 'MD07': ['CH05'], 'FA11': ['EN06'],
         'MA15': ['CP01'], 'WA14': ['WA27']}
if os.environ.get('EARLYFIX') == '1':
    for rid, adds in EARLY.items():
        i = row(rid); c = L[i].split(' | '); pre = c[4]; d = 0; cut = len(pre)
        for j, ch in enumerate(pre):
            d += ch == '('; d -= ch == ')'
            if d == 0 and pre.startswith(' — ', j): cut = j; break
        c[4] = pre[:cut] + ''.join(f' + {a}' for a in adds) + pre[cut:]; L[i] = ' | '.join(c)
open(p,'w',encoding='utf-8').write('\n'.join(L)); print("scratch redesign in place")
