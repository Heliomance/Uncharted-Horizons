"""Category ledger v4: per-population and tile uniques, ungated objects, faith-purchase buildings excluded,
and every exclusive group (grid plants, Regimen Halls, launch complexes, reservoirs, pairs) counted once."""
import ledger as Lg, ledger2 as L2, ledger3 as L3, re
from collections import defaultdict
CAT=L2.CAT
def buildable(b): return Lg.regular(b) and not any('Unbuildable' in u or 'Can only be purchased' in u for u in b.get('uniques',[]))
t=open('/home/user/Uncharted-Horizons/design/simulator/tt.md',encoding='utf-8').read(); body=t[:t.index('\n## 4.')]
GROUP={}
for l in body.split('\n'):
    for bm in re.finditer(r'\*\*([^*]+)\*\*ⁿ\s*\[((?:[^\[\]]|\[[^\]]*\])*)\]',l):
        for tag in ('Power Plant','Regimen Hall','Launch Complex','Caloric Reservoir'):
            if f'⟨{tag}⟩' in bm.group(2): GROUP[bm.group(1)]=tag
        m=re.search(r'⟨Remove \[([A-Z][\w\- ]+)\] \[in this city\]⟩',bm.group(2))
        if m and bm.group(1) not in GROUP: GROUP.setdefault(bm.group(1),'pair:'+min(bm.group(1),m.group(1))); GROUP.setdefault(m.group(1),'pair:'+min(bm.group(1),m.group(1)))
for n in ('Nuclear Plant','Solar Plant'): GROUP[n]='Power Plant'
def items(side,era):
    out=[]   # (level, yields, pct, upkeep, weight, group)
    for b in Lg.B:
        if not buildable(b): continue
        if side=='base':
            lv=Lg.colcum[Lg.tcol[b['requiredTech']]] if b.get('requiredTech') in Lg.tcol else 0
            grp='NS' if b['name'] in ('Nuclear Plant','Solar Plant') else None
        else:
            if b['name'] in L3.ungated: lv=0
            elif b['name'] in L2.assign and L2.assign[b['name']][0] in L2.rows: lv=Lg.ERA_END[L2.rows[L2.assign[b['name']][0]][2]]
            else: continue
            grp=GROUP.get(b['name'])
        pct=defaultdict(float)
        for k,v in b.get('percentStatBonus',{}).items(): pct[k.capitalize()]+=v
        out.append((lv,L3.canonical_yields(b,era),pct,b.get('maintenance',0),1.0,grp))
    if side=='fork':
        for er,tier,rid,name,ff,pp,mm in L2.newb:
            spec=[sp for n_,sp,_a,_b in L2.bspecs(L2.rows[rid][3]) if n_==name]
            us=re.findall(r'⟨([^⟩]+)⟩',spec[0]) if spec else []
            ex=L3.extra([re.sub(r'\s*<[^>]*>','',u) for u in us],era)
            y=defaultdict(float,{c:ff[c]+ex.get(c,0) for c in CAT})
            out.append((Lg.ERA_END[er],y,defaultdict(float,pp),mm,Lg.LIK[tier],GROUP.get(name)))
    return out
def ledger(level,side):
    era=L3.era_at(level, side); f=defaultdict(float); p=defaultdict(float); m=0.0; best={}
    for lv,y,pc,up,w,g in items(side,era):
        if lv>level: continue
        if g:
            score=sum(y.values())+sum(pc.values())/10
            if g not in best or score*w>best[g][0]: best[g]=(score*w,y,pc,up,w)
            continue
        for c in CAT: f[c]+=y.get(c,0)*w; p[c]+=pc.get(c,0)*w
        m+=up*w
    for s,y,pc,up,w in best.values():
        for c in CAT: f[c]+=y.get(c,0)*w; p[c]+=pc.get(c,0)*w
        m+=up*w
    return f,p,m
def table():
    R={}
    for era in Lg.EO:
        L=Lg.ERA_END[era]; R[era]=(ledger(L,'base'),ledger(L,'fork'))
    return R
if __name__=='__main__':
    R=table()
    print(f"{'era end':13}"+''.join(f"{c[:5]:>12}" for c in CAT)+f"{'upkeep':>12}")
    for era,((bf,bp,bm),(ff,fp,fm)) in R.items():
        print(f"{era:13}"+''.join(f"{bf[c]:>5.0f}→{ff[c]:<5.0f}" for c in CAT)+f"{bm:>5.0f}→{fm:<5.0f}")
    print(f"\nflat ratio fork/base (— where base < 2):\n{'era end':13}"+''.join(f"{c[:5]:>8}" for c in CAT)+f"{'upkeep':>8}")
    for era,((bf,bp,bm),(ff,fp,fm)) in R.items():
        print(f"{era:13}"+''.join(f"{(f'{ff[c]/bf[c]:.1f}' if bf[c]>=2 else '—'):>8}" for c in CAT)+f"{fm/bm:>8.1f}")
