import re, json
t=open('tt.md',encoding='utf-8').read()
t=t.replace('(v3.80)','(v3.81)',1)
def find_spec(s,name):
    i=s.find(f'**{name}**ⁿ')
    if i<0: return None
    j=s.find('[',i)
    if j<0 or j-i>len(name)+8: return None
    d=0
    for k in range(j,len(s)):
        if s[k]=='[': d+=1
        elif s[k]==']':
            d-=1
            if d==0: return i,j,k,s[j+1:k]
def split_top(spec):
    parts=[]; cur=''; d=0; u=0
    for ch in spec:
        if ch=='[': d+=1
        elif ch==']': d-=1
        elif ch=='⟨': u+=1
        elif ch=='⟩': u-=1
        if ch==';' and d==0 and u==0: parts.append(cur); cur=''
        else: cur+=ch
    return parts+[cur]
PROD_TOK=re.compile(r'^\s*\+\d+ Production\s*$')
def strip_prod(spec,strip_tiles=True):
    out=[]
    for p in split_top(spec):
        q=p.strip()
        if re.fullmatch(r'Production \+\d+%',q): continue
        if re.fullmatch(r'⟨\[\+\d+\]% \[Production\] \[in this city\]⟩',q): continue
        if strip_tiles and re.fullmatch(r'⟨\[\+\d+ Production\] from (?:\[[^\]]+\] tiles \[in this city\]|all \[[^\]]+\] buildings)⟩',q): continue
        m=re.match(r'(.*?)(\s+—\s+.*)$',p,re.S); body,desc=(m.group(1),m.group(2)) if m else (p,'')
        toks=body.split(',')
        if toks and all(re.fullmatch(r'\s*[+-]\d+ \w+\s*',x) for x in toks if x.strip()) and any(x.strip() for x in toks):
            kept=[x.strip() for x in toks if x.strip() and not PROD_TOK.match(x)]
            if kept: out.append(' '+', '.join(kept)+desc)
            elif desc.strip(): out.append(' '+desc.strip().lstrip('—').strip())
            continue
        out.append(p)
    return ';'.join(x for x in out if x.strip())
def set_prod(spec,flat,pct):
    s=strip_prod(spec,strip_tiles=False); parts=split_top(s)
    ins=[]; 
    if flat: ins.append(f' +{flat} Production')
    if pct: ins.append(f' ⟨[+{pct}]% [Production] [in this city]⟩')
    # after the cost part (and any leading "a grid plant"/tag/Remove parts)
    k=0
    for i,p in enumerate(parts):
        if re.match(r'\s*(a grid plant|⟨Power Plant⟩|⟨Remove|\d+(/\d+)?$|\d+/\d+|maintenance \d|1000|national wonder|world wonder)',p.strip()) or re.fullmatch(r'\s*\d+(/\d+)?\s*',p): k=i+1
    return ';'.join(parts[:k]+ins+parts[k:])
STRUCT=r'Must |Only available|Can only be built|Destroyed when|⟨Remove|\(tag\)|Consumes|requires \*\*|needs \*\*no|no \*\*|Unavailable|no fuel|no resource'
def meaningful(spec):
    for p in split_top(spec):
        q=p.strip()
        if not q or re.match(r'^(\d+(/\d+)?|a grid plant.*|maintenance \d+|—.*)$',q): continue
        if re.search(STRUCT,q) and not re.search(r'[+-]\d+ (Food|Production|Gold|Science|Culture|Happiness|Faith)|×\d|%',q): continue
        if re.search(r'[+-]\d+|×\d|⟨|Great \w+ points|cityStrength|carryover',q): return True
    return False
def edit_building(rid,name,fn):
    global t
    L=t.split('\n'); i=[n for n,l in enumerate(L) if l.startswith(f'| {rid} |')]; assert len(i)==1,rid
    line=L[i[0]]; r=find_spec(line,name); assert r,(rid,name)
    a,j,k,spec=r; new=fn(spec)
    if new is None or not meaningful(new):
        end=k+1; m=re.match(r'\s+—\s+[^.;|]*[.;]?',line[end:])
        if m: end+=m.end()
        start=a; pre=re.search(r'(;\s*|,\s*)$',line[:a])
        if pre: start=a-len(pre.group(0))
        line=line[:start]+line[end:]; status='removed'
    else:
        line=line[:j+1]+new+line[k:]; status='edited'
    line=re.sub(r'(\| )[.;,]\s*',r'\1',line); line=re.sub(r'  +',' ',line)
    L[i[0]]=line; t='\n'.join(L); return status
def edit_row_text(rid,old,new):
    global t
    L=t.split('\n'); i=[n for n,l in enumerate(L) if l.startswith(f'| {rid} |')]; assert len(i)==1,rid
    assert L[i[0]].count(old)==1,(rid,old[:70]); L[i[0]]=L[i[0]].replace(old,new); t='\n'.join(L)
log=[]
S=lambda rid,n: log.append((rid,n,edit_building(rid,n,lambda s: strip_prod(s))))
P=lambda rid,n,f,p: log.append((rid,n,edit_building(rid,n,lambda s: set_prod(s,f,p))))
# ---- grid plants: the slot never exceeds Unciv's Nuclear Plant (+5, +15%); Space-era plants one step beyond
P('TH08','Stirling Works',1,0)
for rid,n in [('EL14','Generating Station'),('ES03','Coal Plant'),('ES03-W','Biomass Plant'),('ES05','Oil Plant'),('ES05-W','Bio-Fuel Plant'),
              ('ES13','Biogas Plant'),('ES16','Caloric Plant'),('ES10','Tidal Plant')]: P(rid,n,2,5)
log.append(('ES09','Geothermal Plant',edit_building('ES09','Geothermal Plant',lambda s: set_prod(s,2,5).replace('⟨[+2 Production] from [Volcanic] tiles','⟨[+1 Production] from [Volcanic] tiles'))))
for rid,n in [('ES08','Fusion Plant'),('ES15','Quintessic Plant'),('QM-E05','Great Work Reactor'),('NP08','Thorium Reactor'),('NP-F02','Micro-Reactor')]: P(rid,n,5,15)
for rid,n in [('ES14','Advanced Fission Plant'),('NP09','Compact Fusion Plant'),('NP-F04','Cascade Reactor'),('QM-E21','Compact Athanor')]: P(rid,n,6,20)
# ---- mechanism and pair buildings, calibrated
log.append(('MC08','Steam Works',edit_building('MC08','Steam Works',lambda s: set_prod(s,2,0).replace('⟨Remove [Engine House] [in this city]⟩','⟨Remove [Engine House] [in this city]⟩; ⟨[+100]% Production when constructing [Factory] buildings [in this city]⟩'))))
P('CH23','Cycle Forge',2,0); P('CP14','Perceptron Laboratory',2,0); P('TH11','Heat Exchange',2,0); P('NP10','Cold Fusion Cell',3,0)
log.append(('CH09','Refinery',edit_building('CH09','Refinery',lambda s: set_prod(s,2,0).replace('⟨[+2 Production] from [Oil] tiles','⟨[+1 Production] from [Oil] tiles'))))
P('CH09-W','Bio-Refinery',1,0); P('CO15','Orbital Platform',2,10)
# ---- generic industry: Production stripped; removed if nothing is left
for rid,n in [('F02','Kiln'),('F03','Charcoal Burner'),('S02','Stonecutter'),('TX01','Weaver'),('CO04','Concrete Works'),('ME10','Cast Iron Works'),
              ('MC05','Clock Tower'),('ME08-W','Managed Forest'),('CH26','Calorimetry Hall'),('EL02','Battery Works'),('MI13','Gasworks'),('TX05','Textile Mill'),
              ('CH13','Propellant Works'),('CO17','Clean Room'),('EL05','Tramway'),('EN01','Valve Works'),('MD08','Prosthetics Workshop'),('TH03','Turbine Hall'),
              ('WM06','Dam'),('EN03','Microchip Foundry'),('MS01','Composites Factory'),('MS02','Nanofab'),('MS04','Graphene Works'),('OP07','Laser Lab'),
              ('GN05','Bio-Factory'),('MI12','Asteroid Mining Station'),('MS08','Exotic Matter Foundry'),('QM-E13','Vacuum Tap'),('QP12','Casimir Generator'),
              ('SE02','Orbital Shipyard'),('SE06','Orbital Depot')]: S(rid,n)
log.append(('QM-E22','Medium Cell',edit_building('QM-E22','Medium Cell',lambda s: None)))
json.dump(log,open('power/prod_log.json','w'))
open('tt.md','w',encoding='utf-8').write(t)
from collections import Counter
print(Counter(s for _,_,s in log)); print("removed:",[n for r,n,s in log if s=='removed'])
