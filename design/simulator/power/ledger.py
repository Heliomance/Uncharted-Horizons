"""Power ledger: per-city building power available by cumulative Insight, base Civ V vs the fork."""
import re,json
U='/home/user/Uncharted-Horizons/design/simulator/unciv/'
strip=lambda s: re.sub(r'//[^\n]*','',s)
TECH=json.loads(strip(open(U+'Techs.json',encoding='utf-8').read()))
tcol={}; colcum={}; cum=0
for col in TECH:
    cum+=sum(t.get('cost',col['techCost']) for t in col['techs']); colcum[col['columnNumber']]=cum
    for t in col['techs']: tcol[t['name']]=col['columnNumber']
B=json.loads(strip(open(U+'Buildings.json',encoding='utf-8').read()))
STATS=('food','production','gold','science','culture','happiness','faith')
def bpower(b):
    flat=sum(b.get(s,0) for s in STATS); pct=sum(b.get('percentStatBonus',{}).values())
    for u in b.get('uniques',[]):
        m=re.match(r'\[\+(\d+)\]% \[(\w+)\] \[in this city\]',u)
        if m: pct+=int(m.group(1))
    return flat,pct
canon={b['name']:b for b in B}
regular=lambda b: not b.get('isWonder') and not b.get('isNationalWonder') and not b.get('uniqueTo') and not b.get('replaces')
# ---- base Civ V: a building is available once its tech's column is researched
base=[(colcum[tcol[b['requiredTech']]] if b.get('requiredTech') in tcol else 0,)+bpower(b)+(b['name'],) for b in B if regular(b)]
# ---- the fork: canonical buildings at their §7 breakthrough, plus the fork's own new buildings
t=open('/home/user/Uncharted-Horizons/design/simulator/tt.md',encoding='utf-8').read()
body=t[:t.index('\n## 4.')]
BASE_END={'Primitive':160,'Ancient':545,'Classical':1820,'Medieval':5720,'Early Modern':24970,'Modern':66270,'Atomic':112270,'Space':202470}   # base Civ V's eras: its tech-column costs
ERA_END={'Primitive':149,'Ancient':721,'Classical':2259,'Medieval':6528,'Early Modern':23569,'Modern':75161,'Atomic':143768,'Space':195610}   # the fork's eras, redrawn in v3.108 for an even pace
def bounds(side): return ERA_END if side == 'fork' else BASE_END
EO=list(ERA_END)
rowera={}; newb=[]; civwide=[]
for l in body.split('\n'):
    m=re.match(r'^\| ([A-Z]{1,3}(?:-[A-Z])?\d+[A-Z]?(?:-W|-V\d+)?|ME-B) \| \*\*([^*]+)\*\* \| (\w+) \| ([A-Za-z ]+?) \| [^|]*\| ([^|]*)\|',l)
    if not m: continue
    rid,name,tier,era,unl=m.groups(); rowera[rid]=(era,tier)
    if rid.startswith('QM-E') or re.search(r'Substance only|Process only|Only in (?:Substance-|Process-)?Elemental worlds|Only in Caloric worlds|Caloric worlds only|Only in Miasma worlds|Only in Humoral worlds|Only in Vitalist worlds|Vitalist worlds only|Gravitic worlds only',l): continue          # familiar world only
    for bm in re.finditer(r'\*\*([^*]+)\*\*ⁿ\s*\[((?:[^\[\]]|\[[^\]]*\])*)\]',unl):
        spec=bm.group(2)
        if re.search(r'wonder|national wonder|Unbuildable|buy-only|Can only be built',spec,re.I): continue
        flat=sum(int(x) for x in re.findall(r'(?<![\w\[])\+(\d+) (?:Food|Production|Gold|Science|Culture|Happiness|Faith)(?![^⟨]*⟩)',re.sub(r'⟨[^⟩]*⟩','',spec)))
        pct=sum(int(x) for x in re.findall(r'⟨\[\+(\d+)\]% \[(?:Food|Production|Gold|Science|Culture|Faith)\] \[in this city\]⟩',spec))
        newb.append((era,tier,rid,bm.group(1),flat,pct))
    outside=re.sub(r'\*\*[^*]+\*\*ⁿ\s*\[(?:[^\[\]]|\[[^\]]*\])*\]','',unl)
    for x in re.findall(r'⟨\[\+(\d+)\]% \[(?:Food|Production|Gold|Science|Culture|Faith)\] \[in all cities\]',outside): civwide.append((era,tier,rid,int(x)))
s=t.index('## 7. BASE-GAME OBJECT ASSIGNMENTS'); e=t.index('\n## 8.',s)
assign={}
for l in t[s:e].split('\n'):
    m=re.match(r'^\| ([^|]+?) \| [^|]+ \| \*\*([A-Z]{1,3}(?:-[A-Z])?\d+[A-Z]?(?:-W)?)',l)
    if m: assign.setdefault(m.group(1).strip(),m.group(2))
fork=[]
for name,b in canon.items():
    if not regular(b) or name not in assign or assign[name] not in rowera: continue
    fork.append((ERA_END[rowera[assign[name]][0]],)+bpower(b)+(name,))
LIK={'CORE':1,'STANDARD':.85,'UNCOMMON':.4,'RARE':.1,'UNIQUE':0}
def fork_new(level):
    f=p=0.0; n=0
    for era,tier,rid,name,flat,pct in newb:
        if ERA_END[era]<=level: f+=flat*LIK[tier]; p+=pct*LIK[tier]; n+=LIK[tier]
    return f,p,n
def civ(level): return sum(x*LIK[tier] for era,tier,rid,x in civwide if ERA_END[era]<=level)
def upto(rows,level): return (sum(r[1] for r in rows if r[0]<=level), sum(r[2] for r in rows if r[0]<=level), sum(1 for r in rows if r[0]<=level))
if __name__=='__main__':
    print("Per-city power available by the end of each fork era (likelihood-weighted for the fork's own buildings and bonuses)\n")
    print(f"{'era end':13} {'Insight':>8} | {'base: flat':>10} {'% bonus':>8} {'bldgs':>6} | {'fork: flat':>10} {'% bonus':>8} {'bldgs':>6} {'civ-wide %':>11} | {'flat ratio':>10} {'% ratio':>8}")
    for era in EO:
        L=ERA_END[era]; bf,bp,bn=upto(base,L); cf,cp,cn=upto(fork,L); nf,np_,nn=fork_new(L); cw=civ(L)
        ff,fp,fn=cf+nf,cp+np_+cw,cn+nn
        print(f"{era:13} {L:>8,} | {bf:>10.0f} {bp:>8.0f} {bn:>6} | {ff:>10.1f} {fp:>8.0f} {fn:>6.1f} {cw:>11.0f} | {ff/bf if bf else 0:>10.2f} {fp/bp if bp else 0:>8.2f}")
