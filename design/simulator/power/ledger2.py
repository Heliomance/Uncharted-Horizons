import ledger as Lg, re, json
def bspecs(s):
    """every **Name**ⁿ [spec] in s, with the spec read bracket-balanced"""
    out=[]; i=0
    while True:
        m=re.compile(r'\*\*([^*]+)\*\*ⁿ\s*\[').search(s,i)
        if not m: return out
        d=0; j=m.end()-1
        for k in range(j,len(s)):
            if s[k]=='[': d+=1
            elif s[k]==']':
                d-=1
                if d==0: out.append((m.group(1),s[j+1:k],m.start(),k)); break
        i=m.end()

from collections import defaultdict
CAT=['Food','Production','Gold','Science','Culture','Happiness','Faith']
def base_cat(level):
    f=defaultdict(float); p=defaultdict(float); m=0.0
    for b in Lg.B:
        if not Lg.regular(b): continue
        lv=Lg.colcum[Lg.tcol[b['requiredTech']]] if b.get('requiredTech') in Lg.tcol else 0
        if lv>level: continue
        for c in CAT: f[c]+=b.get(c.lower(),0)
        for k,v in b.get('percentStatBonus',{}).items(): p[k.capitalize()]+=v
        for u in b.get('uniques',[]):
            mm=re.match(r'\[\+(\d+)\]% \[(\w+)\] \[in this city\]',u)
            if mm: p[mm.group(2)]+=int(mm.group(1))
        m+=b.get('maintenance',0)
    return f,p,m
canon={b['name']:b for b in Lg.B}
from defaults import TREE   # the design document, or a run's patched copy
t=open(TREE,encoding='utf-8').read(); body=t[:t.index('\n## 4.')]
s=t.index('## 7. BASE-GAME OBJECT ASSIGNMENTS'); e=t.index('\n## 8.',s)
assign={}; kind=None; wonders=set()
for l in t[s:e].split('\n'):
    h=re.match(r'^### (World Wonders|National Wonders|Buildings|Tile Improvements|Units)',l)
    if h: kind=h.group(1)
    mm=re.match(r'^\| ([^|]+?) \| [^|]+ \| \*\*([A-Z]{1,3}(?:-[A-Z])?\d+[A-Z]?(?:-W)?)',l)
    if mm: assign.setdefault(mm.group(1).strip(),(mm.group(2),kind))
rows={}; newb=[]
for l in body.split('\n'):
    mm=re.match(r'^\| ([A-Z]{1,3}(?:-[A-Z])?\d+[A-Z]?(?:-W|-V\d+)?|ME-B) \| \*\*([^*]+)\*\* \| (\w+) \| ([A-Za-z ]+?) \| [^|]*\| ([^|]*)\|',l)
    if not mm: continue
    rid,name,tier,era,unl=mm.groups(); rows[rid]=(name,tier,era,unl,l)
    if rid.startswith('QM-E') or re.search(r'Substance only|Process only|Only in (?:Substance-|Process-)?Elemental worlds|Only in Caloric worlds|Caloric worlds only|Only in Miasma worlds|Only in Humoral worlds|Only in Vitalist worlds|Vitalist worlds only|Gravitic worlds only',l): continue
    for _bn,spec,_a,_b in bspecs(unl):
        bm=type('M',(),{'group':lambda self,i,_n=_bn,_s=spec: _n if i==1 else _s})()
        if re.search(r'wonder|Unbuildable|buy-only|Can only be built',spec,re.I): continue
        plain=re.sub(r'⟨[^⟩]*⟩','',spec)
        f={c:sum(int(x) for x in re.findall(rf'(?<![\w\[])\+(\d+) {c}\b',plain)) for c in CAT}
        p={c:sum(int(x) for x in re.findall(rf'⟨\[\+(\d+)\]% \[{c}\] \[in this city\]⟩',spec)) for c in CAT}
        mt=re.match(r'\s*(\d+)/(\d+)',spec); m=int(mt.group(2)) if mt else 0
        newb.append((era,tier,rid,bm.group(1),f,p,m))
def fork_cat(level,extra_moves=None):
    f=defaultdict(float); p=defaultdict(float); m=0.0
    for name,(rid,kd) in assign.items():
        b=canon.get(name)
        if not b or not Lg.regular(b) or rid not in rows or Lg.ERA_END[rows[rid][2]]>level: continue
        for c in CAT: f[c]+=b.get(c.lower(),0)
        for k,v in b.get('percentStatBonus',{}).items(): p[k.capitalize()]+=v
        m+=b.get('maintenance',0)
    for era,tier,rid,name,ff,pp,mm in newb:
        if Lg.ERA_END[era]>level: continue
        w=Lg.LIK[tier]
        for c in CAT: f[c]+=ff[c]*w; p[c]+=pp[c]*w
        m+=mm*w
    return f,p,m
if __name__=='__main__':
    print("Flat yields per city from buildings, by the end of each era: base → fork   (maintenance in Gold)")
    print(f"{'era end':13}"+''.join(f"{c[:5]:>13}" for c in CAT)+f"{'upkeep':>13}")
    for era in Lg.EO:
        L=Lg.ERA_END[era]; bf,bp,bm=base_cat(L); ff,fp,fm=fork_cat(L)
        print(f"{era:13}"+''.join(f"{bf[c]:>6.0f}→{ff[c]:<6.0f}" for c in CAT)+f"{bm:>6.0f}→{fm:<6.0f}")
    print("\nPercentage bonuses per city: base → fork")
    print(f"{'era end':13}"+''.join(f"{c[:5]:>13}" for c in CAT))
    for era in Lg.EO:
        L=Lg.ERA_END[era]; bf,bp,bm=base_cat(L); ff,fp,fm=fork_cat(L)
        print(f"{era:13}"+''.join(f"{bp[c]:>6.0f}→{fp[c]:<6.0f}" for c in CAT))
    # wonder-only audit: rows whose every granted object is a world wonder and that grant nothing else
    print("\nRows whose only grants are world wonders:")
    byrow=defaultdict(list)
    for name,(rid,kd) in assign.items(): byrow[rid].append((name,kd))
    for rid,(name,tier,era,unl,l) in rows.items():
        objs=byrow.get(rid,[])
        newobj=re.findall(r'\*\*([^*]+)\*\*ⁿ\s*\[([^\]]{0,40})',unl)
        rest=re.sub(r'\*\*[^*]+\*\*(?:ⁿ)?(?:\s*\[(?:[^\[\]]|\[[^\]]*\])*\]|\s*\((?:[^()]|\([^)]*\))*\))?','',unl)
        other=re.findall(r'⟨[^⟩]+⟩',rest)
        allw=objs and all(kd=='World Wonders' for _,kd in objs) and all('world wonder' in s for _,s in newobj)
        onlynew=not objs and newobj and all('world wonder' in s for _,s in newobj)
        if (allw or onlynew) and not other: print(f"  {rid:7} {name:32} {tier:9} {era:12} {[o for o,_ in objs]+[n for n,_ in newobj]}")
