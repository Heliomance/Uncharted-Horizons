"""Endeavours as insurance: compare the distribution of victory times with and without Endeavours.
Target (Tamsin, 13 Oct 2026): average on par with, or slightly worse than, no Endeavours; slow tail (and failures) better."""
import json, statistics as st
R = '/home/user/Uncharted-Horizons/design/simulator/power/results/'
import sys
LABELS = {'T2': 'no Endeavours', 'T4b15': '1.5x, from first Space discovery', 'T4b15t': '1.5x, from the unified theory', 'T4b': '2x, from first Space discovery',
          'T2d': 'no Endeavours', 'T4b15d': '1.5x, from first Space discovery', 'T4b15td': '1.5x, from the unified theory', 'T2r': 'no Endeavours (isolated)', 'T4b20d': '2x, from first Space discovery', 'T4b25d': '2.5x, from first Space discovery', 'G15c': '1.5x, glimpse only', 'G20c': '2x, glimpse only', 'G25c': '2.5x, glimpse only', 'G15i': '1.5x, glimpse only', 'G20i': '2x, glimpse only', 'G25i': '2.5x, glimpse only'}
TESTS = [(t, LABELS.get(t, t)) for t in (sys.argv[1:] or ['T2', 'T4b15', 'T4b15t', 'T4b'])]
def vic(r): return max(r['cert'], r['built']) + 9 - r['space'] if r['cert'] and r['built'] else None
def pct(x, p): x = sorted(x); return x[min(len(x) - 1, int(round(p / 100 * (len(x) - 1))))]
print("Victory-ready turns after the Space era opens. p10 = fast tail, p90 = slow tail; 'no victory' = never certain or never built (counted separately, the worst outcome).")
print(f"{'world':10} {'Endeavours':34} {'mean':>5} {'median':>6} {'p10':>4} {'p90':>4} {'worst':>5} {'SD':>5} {'no victory':>10}")
pool = {t: ([], 0) for t, _ in TESTS}
for w in ('familiar', 'Substance', 'Process'):
    for t, lab in TESTS:
        rs = json.load(open(f'{R}w7f_{w}_{t}.json')); v = [x for x in map(vic, rs) if x is not None]; fails = len(rs) - len(v)
        pool[t] = (pool[t][0] + v, pool[t][1] + fails)
        print(f"{w if t == TESTS[0][0] else '':10} {lab:34} {st.mean(v):>5.1f} {st.median(v):>6.0f} {pct(v,10):>4} {pct(v,90):>4} {max(v):>5} {st.pstdev(v):>5.1f} {fails:>10}")
print("-" * 92)
for t, lab in TESTS:
    v, fails = pool[t]
    print(f"{'all three' if t == TESTS[0][0] else '':10} {lab:34} {st.mean(v):>5.1f} {st.median(v):>6.0f} {pct(v,10):>4} {pct(v,90):>4} {max(v):>5} {st.pstdev(v):>5.1f} {fails:>10}")
