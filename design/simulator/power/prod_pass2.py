import re
src=open('power/prod_pass.py').read()
exec(src[src.index('def find_spec'):src.index('log=[]')].replace("global t\n","global t\n"))
t=open('tt.md',encoding='utf-8').read()
def spec_edit(rid,name,fn):
    global t
    L=t.split('\n'); i=[n for n,l in enumerate(L) if l.startswith(f'| {rid} |')]; assert len(i)==1,rid
    line=L[i[0]]; a,j,k,spec=find_spec(line,name); new=fn(spec)
    if new is None:
        end=k+1; m=re.match(r'\s+—\s+[^.;|]*[.;]?',line[end:]); end+=m.end() if m else 0
        pre=re.search(r'(;\s*|,\s*)$',line[:a]); start=a-len(pre.group(0)) if pre else a
        line=line[:start]+line[end:]
    else: line=line[:j+1]+new+line[k:]
    line=re.sub(r'(\| )[.;,]\s*',r'\1',line); line=re.sub(r'  +',' ',line); L[i[0]]=line; t='\n'.join(L)
def tidy(spec):
    """move trailing stat parts next to the cost part"""
    parts=split_top(spec); stats=[]; rest=[]
    for p in parts:
        if re.fullmatch(r'\s*\+\d+ Production\s*',p) or re.fullmatch(r'\s*⟨\[\+\d+\]% \[Production\] \[in this city\]⟩\s*',p): stats.append(p)
        else: rest.append(p)
    if not stats: return spec
    k=0
    for i,p in enumerate(rest):
        if re.fullmatch(r'\s*(a grid plant: ⟨Power Plant⟩ \(tag\)|\d+(/\d+)?|maintenance \d+|1000|⟨Costs \[\d+\] \[Caloric\]⟩(\s+—.*)?)\s*',p): k=i+1
    return ';'.join(rest[:k]+[' '+s.strip() for s in stats]+rest[k:])
# 1. placement: tidy every building the first pass calibrated
import json
for rid,name,st in json.load(open('power/prod_log.json')):
    if st=='edited': spec_edit(rid,name,tidy)
# 2. the misses
spec_edit('CO15','Orbital Platform',lambda s: s.replace('⟨[+10]% [Production] [in this city]⟩; ⟨[+10]% [Production] [in this city]⟩ — orbital industry','⟨[+10]% [Production] [in this city]⟩ — orbital industry'))
spec_edit('CH26','Calorimetry Hall',lambda s: s.replace('⟨[+2 Production] from all [Cycle Forge] buildings⟩','⟨[+1 Production] from all [Cycle Forge] buildings⟩'))
spec_edit('OP07','Laser Lab',lambda s: None)
spec_edit('CO04','Concrete Works',lambda s: s.replace('; ⟨[+1 Production] from [Water resource] tiles [in this city]⟩',''))
spec_edit('MD08','Prosthetics Workshop',lambda s: None)
spec_edit('MC06','Printing House',lambda s: s.replace('+1 Science, +2 Culture','+2 Culture'))
# 3. folds: about one per era survives, at +1
def fold(rid,old,new):
    global t
    L=t.split('\n'); i=[n for n,l in enumerate(L) if l.startswith(f'| {rid} |')]; assert len(i)==1,rid
    line=L[i[0]]
    if new is None:
        m=re.search(r'(;\s*|,\s*)?'+re.escape(old)+r'(\s*\([^()]*\))?(;\s*)?',line); assert m,(rid,old)
        rep='; ' if (m.group(1) and m.group(3)) else ''
        line=line[:m.start()]+rep+line[m.end():]
    else:
        assert line.count(old)==1,(rid,old); line=line.replace(old,new)
    line=re.sub(r'(\| )[.;,]\s*',r'\1',line); line=re.sub(r'  +',' ',line); L[i[0]]=line; t='\n'.join(L)
KEEP1={('TH01','Steam Works'),('TH09','Steam Works'),('RC02','Observatory'),('OP02','Scientist')}
STRIP=[('TX06','Factory'),('MC11','Factory'),('TH04','Factory'),('CH11','Factory'),('QP03','Factory'),('CH05','Forge'),('EL06','Turbine Hall'),
       ('QP05','Nuclear Plant'),('NP-F01','Nuclear Plant'),('TH07','Coal Plant'),('TH07','Nuclear Plant'),('TH07','Geothermal Plant'),('TH05','Engineer'),
       ('GN10','Biogas Plant'),('GN10','Biomass Plant'),('MC01','Kiln'),('QM-E04','Quintessic Plant'),
       ('TX10','Library'),('OP04','Medical School'),('OP04','Laboratory'),('EN02','Research Lab'),('EN02','Public School'),('RC04','Computer Centre'),('MD21','Phage Institute')]
body=t
for rid,tgt in KEEP1:
    for form in (f'⟨[+2 Production] from all [{tgt}] buildings⟩',f'⟨[+2 Science] from all [{tgt}] buildings⟩',f'⟨[+1 Science] from every [{tgt}]⟩'):
        line=[l for l in t.split('\n') if l.startswith(f'| {rid} |')][0]
        if form in line: fold(rid,form,form.replace('[+2 ','[+1 '))
for rid,tgt in STRIP:
    line=[l for l in t.split('\n') if l.startswith(f'| {rid} |')][0]
    m=re.search(r'⟨\[\+\d+ (?:Production|Science)\] from (?:all \['+re.escape(tgt)+r'\] buildings|every \['+re.escape(tgt)+r'\])⟩',line)
    assert m,(rid,tgt); fold(rid,m.group(0),None)
# the Telecom Exchange's in-building Science fold
spec_edit('OP06','Telecom Exchange',lambda s: s.replace('; ⟨[+2 Science] from all [Research Lab] buildings⟩',''))
# 4. the canonical Factory converts the Steam Works
L=[l for l in t.split('\n') if l.startswith('| CO10 |')][0]
assert L.count('|')==8
cells=L.split('|'); cells[6]=cells[6].rstrip()+" The ruleset derivation gives the canonical Factory ⟨Remove [Steam Works] [in this city]⟩: a Factory built where Steam Works stand converts them, twice as fast (the Steam Works' own clause), as a Steam Works converts an Engine House. "
t=t.replace(L,'|'.join(cells),1)
open('tt.md','w',encoding='utf-8').write(t); print("placement tidied; misses fixed; folds kept at +1 or stripped; Factory converts the Steam Works")
