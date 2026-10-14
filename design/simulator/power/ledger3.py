import ledger as Lg, ledger2 as L2, re
from collections import defaultdict
CAT=L2.CAT
POP={'Primitive':3,'Ancient':4,'Classical':6,'Medieval':8,'Early Modern':10,'Modern':14,'Atomic':18,'Space':20}   # assumed typical city
TILES={'Farm':3,'Mine':2,'Pasture':1,'Camp':1,'Plantation':1,'Quarry':1,'Water resource':1,'Ocean':2,'Coast':1,'Sea':1,
       'River':2,'Forest':1,'Jungle':0.5,'Desert':0.5,'Mountain':0.3,'Hill':1,'Lake':0.3,'Marsh':0.2,'Strategic resource':1,
       'Luxury resource':1,'Bonus resource':1,'Fresh water':2,'Grassland':2,'Plains':2,'Tundra':0.5,'Snow':0.1,'Oasis':0.1}
def extra(uniques,era):
    """flat-equivalent yields from per-population and tile uniques, for a typical city of that era"""
    out=defaultdict(float)
    for u in uniques:
        m=re.match(r'\[([^\]]+)\] per \[(\d+)\] population \[in this city\]',u)
        if m:
            for amt,st in re.findall(r'([+-]\d+) (\w+)',m.group(1)): out[st]+=int(amt)*POP[era]/int(m.group(2))
        m=re.match(r'\[([^\]]+)\] from \[([^\]]+)\] tiles \[in this city\]',u)
        if m:
            n=TILES.get(m.group(2).replace('{','').replace('}',''),0.5)
            for amt,st in re.findall(r'([+-]\d+) (\w+)',m.group(1)): out[st]+=int(amt)*n
    return out
# canonical buildings: base-game availability and fork availability (ungated counted from the start)
from defaults import TREE   # the design document, or a run's patched copy
t=open(TREE,encoding='utf-8').read()
s=t.index('## 7. BASE-GAME OBJECT ASSIGNMENTS'); e=t.index('\n## 8.',s)
ungated=set(); mode=False
for l in t[s:e].split('\n'):
    if l.startswith('### '): mode=l.startswith('### Ungated')
    elif mode and l.startswith('| ') and not l.startswith('| ---') : ungated.add(l.split('|')[1].strip().strip('*'))
def era_at(level, side='fork'): return next((e for e in Lg.EO if Lg.bounds(side)[e]>=level), Lg.EO[-1])
def canonical_yields(b,era):
    f=defaultdict(float)
    for c in CAT: f[c]+=b.get(c.lower(),0)
    for k,v in extra(b.get('uniques',[]),era).items(): f[k]+=v
    return f
def ledger(level,side):
    era=era_at(level, side); f=defaultdict(float); p=defaultdict(float); m=0.0; n=0.0
    for b in Lg.B:
        if not Lg.regular(b): continue
        if side=='base':
            lv=Lg.colcum[Lg.tcol[b['requiredTech']]] if b.get('requiredTech') in Lg.tcol else 0
            if lv>level: continue
        else:
            if b['name'] in ungated: pass
            elif b['name'] in L2.assign and L2.assign[b['name']][0] in L2.rows:
                if Lg.ERA_END[L2.rows[L2.assign[b['name']][0]][2]]>level: continue
            else: continue
        for k,v in canonical_yields(b,era).items(): f[k]+=v
        for k,v in b.get('percentStatBonus',{}).items(): p[k.capitalize()]+=v
        m+=b.get('maintenance',0); n+=1
    if side=='fork':
        for er,tier,rid,name,ff,pp,mm in L2.newb:
            if Lg.ERA_END[er]>level: continue
            w=Lg.LIK[tier]
            spec=[x for x in re.findall(r'\*\*'+re.escape(name)+r'\*\*ⁿ\s*\[((?:[^\[\]]|\[[^\]]*\])*)\]',L2.rows[rid][3])]
            us=re.findall(r'⟨([^⟩]+)⟩',spec[0]) if spec else []
            ex=extra([re.sub(r'\s*<[^>]*>','',u) for u in us],era)
            for c in CAT: f[c]+=(ff[c]+ex.get(c,0))*w; p[c]+=pp[c]*w
            m+=mm*w; n+=w
    return f,p,m,n
if __name__=='__main__':
    print("Per-city yields from buildings, including per-population and tile uniques (typical city): base → fork\n")
    print(f"{'era end':13}"+''.join(f"{c[:5]:>12}" for c in CAT)+f"{'upkeep':>12}{'bldgs':>12}")
    for era in Lg.EO:
        L=Lg.ERA_END[era]; bf,bp,bm,bn=ledger(L,'base'); ff,fp,fm,fn=ledger(L,'fork')
        print(f"{era:13}"+''.join(f"{bf[c]:>5.0f}→{ff[c]:<5.0f}" for c in CAT)+f"{bm:>5.0f}→{fm:<5.0f}{bn:>5.0f}→{fn:<5.0f}")
