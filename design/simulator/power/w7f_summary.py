"""Summarise W7f tests against the simple-detective baseline (w7d ..._abc). Usage: w7f_summary.py <world> <test>..."""
import sys, json, collections, statistics as st
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
md = lambda x: st.median(x) if x else float('nan')
def q(x): return f"{st.quantiles(x, n=4)[0]:.0f}–{st.quantiles(x, n=4)[2]:.0f}" if len(x) >= 4 else "—"
w = sys.argv[1]; LABEL = {'base': 'simple detective', 'T1': 'smart detective', 'T2': '+ RC06 alongside RC05', 'T3': '+ open questions draw attention', 'T4': '+ Endeavours 2x, naive rule', 'T4b': '+ Endeavours 2x, fair rule', 'T4c': '+ Endeavours 2x, last piece only', 'T4b15': '+ Endeavours 1.5x, fair rule', 'T4c15': '+ Endeavours 1.5x, last piece only', 'T4b15t': '+ Endeavours 1.5x, from the unified theory', 'T5': '+ both'}
print(f"== {w}: turns after the unified theory (theory) and after certainty (engineering); victory-ready = Space era opening to prototype done")
print(f"   {'test':42} certain  theory med (IQR)  ≤15   eng. med (IQR)  victory med (IQR)  Endeavours/game")
for tname in ['base'] + sys.argv[2:]:
    f = R + (f'w7d_{w}_abc.json' if tname == 'base' else f'w7f_{w}_{tname}.json'); rs = json.load(open(f))
    ok = [r for r in rs if r['cert']]; th = [r['cert'] - r['close'] for r in ok]; en = [max(0, r['built'] - r['cert']) for r in ok if r['built']]
    vic = [max(r['cert'], r['built']) + 9 - r['space'] for r in ok if r['built']]
    ends = [sum(1 for e in r.get('ends', []) if e[2] == 'done') for r in rs]
    print(f"   {tname+' '+LABEL.get(tname,''):42} {len(ok):>3}/{len(rs)}  {md(th):>5.0f} ({q(th):>6})  {sum(1 for x in th if x<=15)/len(th):>4.0%}  {md(en):>5.0f} ({q(en):>6})  {md(vic):>6.0f} ({q(vic):>6})  {md(ends) if tname!='base' else '':>5}")
    if any(r.get('ends') for r in rs):
        th_rows, en_rows = collections.Counter(), collections.Counter()
        for r in rs:
            for turn, k, s in r.get('ends', []):
                if s == 'done': (th_rows if (r['cert'] is None or turn <= r['cert']) else en_rows)[k] += 1
        print(f"      Endeavours completed during theory: {sum(th_rows.values())} ({', '.join(f'{k}×{c}' for k, c in th_rows.most_common(6))});"
              f" during engineering: {sum(en_rows.values())} ({', '.join(f'{k}×{c}' for k, c in en_rows.most_common(6))})")
