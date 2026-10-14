import re,json,html
V=json.load(open('unciv/vocab.json')); KW={k:set(v) for k,v in V['kw'].items()}; N={k:set(v) for k,v in V['names'].items()}
t=open('tt.md',encoding='utf-8').read()
STATS={'Food','Production','Gold','Science','Culture','Happiness','Faith'}
# ---- objects this document defines (**Name**ⁿ), classified by the spec that follows ----
ours={'building':set(),'unit':set(),'improvement':set(),'promotion':set(),'resource':set(),'specialist':set()}
for m in re.finditer(r'\*\*([^*]+?)\*\*ⁿ(?=(.{0,160}))',t):
    n,ctx=m.group(1).strip(),m.group(2)
    if re.search(r'stockpiled\* resource|new (strategic|luxury) resource|a new \*stockpiled\*',ctx): ours['resource'].add(n)
    elif re.match(r'\s*\((new )?specialist',ctx): ours['specialist'].add(n)
    elif re.match(r'\s*[:(]\s*⟨',ctx) or re.search(r'promotion',t[max(0,m.start()-60):m.start()]): ours['promotion'].add(n)
    elif re.match(r'\s*\[unit|\s*\[spaceship part|\s*\(new Great Person|\s*\(unit',ctx): ours['unit'].add(n)
    elif re.match(r'\s*[\[(]\s*improvement|\s*\(improvement|\s*\(improvements',ctx) or 'Great Improvement' in ctx[:120]: ours['improvement'].add(n)
    else: ours['building'].add(n)
for m in re.finditer(r'receive the \[([^\]]+)\] promotion',t): ours['promotion'].add(m.group(1))
ours['resource']|={'Saltpeter','Rare Earths','Obsidian','Prima Materia','Caloric','Voyage'}
ours['building'].add('Power Plant'); TERR_EXTRA={'Volcanic'}
decl_rows={}
for line in t.split('\n'):
    for n in re.findall(r'\*\*([^*]+?)\*\*ⁿ',line): decl_rows.setdefault(n.strip(),line)
ours['improvement']|={n for n,row in decl_rows.items() if re.search(r'improvement',row,re.I) and n not in ours['unit'] and n not in ours['resource']}
ALL_B=N['building']|ours['building']; ALL_U=N['unit']|ours['unit']; ALL_I=N['improvement']|ours['improvement']
ALL_R=N['resource']|ours['resource']; ALL_P=N['promotion']|ours['promotion']
TERRAIN=N['terrain']|TERR_EXTRA|ALL_R|ALL_I|KW['terrainFilter']|KW['tileFilter']|{'Land','Water','River','Fresh Water','Fresh water','Coastal','Rough terrain','Open terrain','Water resource','Strategic resource','Luxury resource','Bonus resource','Natural Wonder','Improvement','All','all'}
UNITF={'Spaceship part'}|ALL_U|N['unittype']|KW['baseUnitFilter']|KW['mapUnitFilter']|ALL_P|{'All','Military','Civilian','Land','Water','Air','Melee','Ranged','Embarked','Wounded'}
CITY=set(KW['cityFilter'])
def atoms(v):
    v=v.strip()
    if v.startswith('non-[') and v.endswith(']'): return atoms(v[5:-1])
    if v.startswith('{'):
        out=[]; d=0; cur=''
        for ch in v:
            if ch=='{': d+=1
            if d>0: cur+=ch
            if ch=='}':
                d-=1
                if d==0: out+=atoms(cur[1:-1]); cur=''
        return out
    return [v]
def ok_stats(v): return all(re.fullmatch(r'[+-]\d+ ('+'|'.join(STATS)+')',p.strip()) for p in v.split(','))
def vocab(ptype):
    p=ptype
    if p in ('tileFilter','terrainFilter'): return TERRAIN
    if 'buildingFilter' in p or 'buildingName' in p:
        s=ALL_B|KW['buildingFilter']|STATS|{'Power Plant','Regimen Hall'}
        if 'tileFilter' in p or 'improvementFilter' in p: s|=TERRAIN|ALL_I|KW['improvementFilter']
        if 'specialist' in p: s|=N['specialist']|ours['specialist']
        return s
    if 'improvementFilter' in p: return ALL_I|KW['improvementFilter']|(TERRAIN if 'terrainFilter' in p else set())
    if p in ('baseUnitFilter','mapUnitFilter','unitFilter'): return UNITF
    if p=='cityFilter': return CITY
    if p in ('resource','stockpiledResource'): return ALL_R
    if p=='stockpile': return ALL_R|STATS|{'Stored Food','Golden Age points'}
    if p=='promotion': return ALL_P
    if p=='unit': return ALL_U
    if p=='specialist': return N['specialist']|ours['specialist']
    if p=='populationFilter': return KW['populationFilter']|N['specialist']|ours['specialist']|{'Population','Specialists','Unemployed'}
    return None
def split(s):
    lits=[]; params=[]; d=0; cur=''; lit=''
    for ch in s:
        if ch=='[':
            if d==0: lits.append(lit); lit=''
            else: cur+=ch
            d+=1; continue
        if ch==']':
            d-=1
            if d==0: params.append(cur); cur=''; continue
            cur+=ch; continue
        if d>0: cur+=ch
        else: lit+=ch
    lits.append(lit); return tuple(x.strip() for x in lits),params
TPL={}
for f in ('unciv/unique_templates.txt','unciv/conditionals.txt'):
    for l in open(f,encoding='utf-8'):
        l=html.unescape(l.strip())
        if not l: continue
        lits,ps=split(l); TPL.setdefault(lits,[]).append(ps)
def check(text,where,report):
    lits,vals=split(text)
    cands=TPL.get(lits)
    if not cands: return
    best=None
    for ps in cands:
        errs=[]
        for p,v in zip(ps,vals):
            if p=='stats':
                if not ok_stats(v): errs.append((p,v))
                continue
            if re.fullmatch(r'(relativeAmount|amount|positiveAmount|nonNegativeAmount)',p):
                if not re.fullmatch(r'[+-]?\d+',v.strip()): errs.append((p,v))
                continue
            voc=vocab(p)
            if voc is None: continue
            for a in atoms(v):
                if a not in voc: errs.append((p,a))
        if best is None or len(errs)<len(best): best=errs
    for p,a in best or []: report.append((where,p,a,text))
report=[]
cur=None
for line in t.split('\n'):
    m=re.match(r'^\| ([A-Z]{1,3}-?[A-Z]?\d{1,2}[A-Z]?(-W|-V\d+)?|ME-B) \|',line); where=m.group(1) if m else '§'
    if line.startswith(('- ','### v','*Version')): continue
    for u in re.findall(r'⟨([^⟩]+)⟩',line):
        if u=='…': continue
        u=re.sub(r'\s*\([^)]*\)\s*$','',u).split(' — ')[0]
        base=re.sub(r'<[^<>]*(?:<[^<>]*>[^<>]*)*>','',u).strip()
        check(base,where,report)
        for c in re.findall(r'<[^<>]*(?:\[[^\]]*\][^<>]*)*>',u): check(c,where,report)
