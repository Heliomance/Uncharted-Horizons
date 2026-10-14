"""Ledger v6 = v5 + conversions (a building retired by a later one stops counting once its successor is available)
and RARE-chain follow-ups weighted by their gateway's rarity."""
import ledger as Lg, ledger2 as L2, ledger3 as L3, ledger4 as L4, ledger5 as L5, re
from collections import defaultdict
CONVERT={'Engine House':'Steam Works','Steam Works':'Factory','Tide Computer':'Seaport'}
RARECHAIN={'TH13','TH14','MC16','MC17','MC18','O13','O14','O15','GN09','GN10','GN11'}
avail={}
def when(name):
    for er,tier,rid,n,ff,pp,mm in L2.newb:
        if n==name: return Lg.ERA_END[er]
    if name in L2.assign and L2.assign[name][0] in L2.rows: return Lg.ERA_END[L2.rows[L2.assign[name][0]][2]]
    return None
orig_newb=list(L2.newb)
def ledger(level,side):
    if side=='fork':
        keep=[]
        for x in orig_newb:
            er,tier,rid,n,ff,pp,mm=x
            succ=CONVERT.get(n); sw=when(succ) if succ else None
            if sw is not None and sw<=level: continue          # converted away by now
            if rid in RARECHAIN: x=(er,'RARE',rid,n,ff,pp,mm)   # reachable only through a RARE gateway
            keep.append(x)
        L2.newb=keep
        folds=[f for f in L5.folds if not any(tgt in CONVERT and when(CONVERT[tgt]) and when(CONVERT[tgt])<=level for tgt in [f[3]])]
        saved=L5.folds; L5.folds=[(lv,st,x*(0.1/Lg.LIK.get('STANDARD',0.85) if rid in RARECHAIN else 1),rid) for lv,st,x,rid in saved]
        try: out=L5.ledger(level,side)
        finally: L2.newb=orig_newb; L5.folds=saved
        return out
    return L5.ledger(level,side)
# folds whose target is a converted building stop counting once it converts
FOLD_TARGET={}
from defaults import TREE   # the design document, or a run's patched copy
for l in open(TREE,encoding='utf-8').read().split('\n'):
    m=re.match(r'^\| ([A-Z]{1,3}(?:-[A-Z])?\d+[A-Z]?(?:-W|-V\d+)?|ME-B) \|',l)
    if m:
        for tg in re.findall(r'⟨\[\+\d+ \w+\] from all \[([^\]]+)\] buildings⟩',l): FOLD_TARGET.setdefault(m.group(1),[]).append(tg)
def fold_ok(rid,level):
    return not any(tg in CONVERT and when(CONVERT[tg]) is not None and when(CONVERT[tg])<=level for tg in FOLD_TARGET.get(rid,[]))
_orig=L5.ledger
def _l5(level,side):
    f,p,m=L4.ledger(level,side)
    if side=='fork':
        for lv,st,x,rid in L5.folds:
            if lv<=level and fold_ok(rid,level): f[st]+=x
    return f,p,m
L5.ledger=_l5
if __name__=='__main__':
    print(f"{'era end':13} {'Prod base':>9} {'fork':>6} {'×':>5} {'% base':>7} {'fork':>5} | {'Sci base':>8} {'fork':>6} {'×':>5}")
    for era in Lg.EO:
        L=Lg.ERA_END[era]; (bf,bp,_),(ff,fp,_)=ledger(L,'base'),ledger(L,'fork')
        r=lambda a,b: f"{a/b:>5.2f}" if b>=1 else "    —"
        print(f"{era:13} {bf['Production']:>9.1f} {ff['Production']:>6.1f} {r(ff['Production'],bf['Production'])} {bp['Production']:>7.0f} {fp['Production']:>5.0f} | {bf['Science']:>8.1f} {ff['Science']:>6.1f} {r(ff['Science'],bf['Science'])}")
