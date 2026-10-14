"""Ledger v5 = v4 + folds ('[stats] from all [X] buildings' / 'from every [X]', counted once per city)
and grid plants grouped by name as well as by tag."""
import ledger as Lg, ledger2 as L2, ledger3 as L3, ledger4 as L4, re
from collections import defaultdict
from defaults import TREE   # the design document, or a run's patched copy
t=open(TREE,encoding='utf-8').read(); body=t[:t.index('\n## 4.')]
PLANTS=set()
for l in body.split('\n'):
    if '⟨Power Plant⟩' in l:
        for bm in re.finditer(r'\*\*([^*]+)\*\*ⁿ\s*\[',l):
            seg=l[bm.start():bm.start()+900]
            if '⟨Power Plant⟩' in seg[:seg.find('**',5) if seg.find('**',5)>0 else 900] or re.search(r'⟨Remove \[\{Power Plant\}',seg[:600]): PLANTS.add(bm.group(1))
for n in PLANTS: L4.GROUP[n]='Power Plant'
FOLD=re.compile(r'⟨\[\+(\d+) (Production|Science|Food|Gold|Culture|Happiness|Faith)\] from (?:all \[[^\]]+\] buildings|every \[[^\]]+\])⟩')
ALT=r"Substance only|Process only|Only in (?:Substance-|Process-)?Elemental worlds|Only in Caloric worlds|Caloric worlds only|Only in Miasma worlds|Only in Humoral worlds|Only in Vitalist worlds|Vitalist worlds only|Gravitic worlds only"
folds=[]
for l in body.split('\n'):
    m=re.match(r'^\| ([A-Z]{1,3}(?:-[A-Z])?\d+[A-Z]?(?:-W|-V\d+)?|ME-B) \| \*\*([^*]+)\*\* \| (\w+) \| ([A-Za-z ]+?) \| [^|]*\| ([^|]*)\|',l)
    if not m or m.group(1).startswith('QM-E') or re.search(ALT,l): continue
    for amt,st in FOLD.findall(m.group(5)): folds.append((Lg.ERA_END[m.group(4)] if m.group(4) in Lg.ERA_END else 10**9,st,int(amt)*Lg.LIK[m.group(3)],m.group(1)))
def ledger(level,side):
    f,p,m=L4.ledger(level,side)
    if side=='fork':
        for lv,st,x,rid in folds:
            if lv<=level: f[st]+=x
    return f,p,m
if __name__=='__main__':
    print("grid plants recognised:",len(PLANTS),sorted(PLANTS))
    print("folds counted:",[(rid,st,round(x,2)) for lv,st,x,rid in folds])
    print(f"\n{'era end':13} {'Prod base':>9} {'fork':>7} {'×':>5} {'% base':>7} {'fork %':>7} | {'Sci base':>8} {'fork':>6} {'×':>5}")
    for era in Lg.EO:
        L=Lg.ERA_END[era]; (bf,bp,_),(ff,fp,_)=ledger(L,'base'),ledger(L,'fork')
        print(f"{era:13} {bf['Production']:>9.1f} {ff['Production']:>7.1f} {ff['Production']/max(bf['Production'],1):>5.2f} {bp['Production']:>7.0f} {fp['Production']:>7.0f} | {bf['Science']:>8.1f} {ff['Science']:>6.1f} {(ff['Science']/bf['Science'] if bf['Science'] else 0):>5.2f}")
