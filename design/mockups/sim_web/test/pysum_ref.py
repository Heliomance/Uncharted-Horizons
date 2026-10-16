"""Reference sums from CPython's sum() for test_pysum.js: random float lists of many lengths and mixtures (similar
magnitudes, mixed magnitudes from 1e-300 to 1e300, cancelling signs, zeros and -0.0, tiny and huge, the harness's own kinds
of weights), written as float.hex so nothing is lost. Usage: python3 -I pysum_ref.py <out.json>"""
import random, json, sys, math
r = random.Random(2026)
cases = []
def add(xs): s = sum(xs); cases.append([[x.hex() for x in xs], float(s).hex(), isinstance(s, int)])
for i in range(20000):
    n = r.randint(1, 40); kind = i % 8
    if kind == 0: xs = [r.random() for _ in range(n)]
    elif kind == 1: xs = [r.uniform(-1, 1) * 10 ** r.uniform(-300, 300) for _ in range(n)]
    elif kind == 2: xs = [r.uniform(-1e6, 1e6) for _ in range(n)]; xs += [-x for x in xs[: n // 2]]
    elif kind == 3: xs = [r.choice([0.0, -0.0, 1e-320, -1e-320, 1.0, -1.0, 1e16, -1e16, 0.1]) for _ in range(n)]
    elif kind == 4: xs = [0.85 * (1 + max(0.0, r.uniform(-3, 3))) for _ in range(n)]          # the harness's 'waiting'
    elif kind == 5: xs = [r.random() * 2.5 + 0.1 for _ in range(n)]                            # meters plus momentum
    elif kind == 6: xs = [r.uniform(-1, 1) * 10 ** r.uniform(-20, 20) for _ in range(n)]
    else: xs = [r.choice([1e308, -1e308, 1.7e308, 5e-324, 1.0]) for _ in range(n)]
    add(xs)
add([]); add([-0.0]); add([-0.0, -0.0]); add([1e308, 1e308]); add([1e308, 1e308, -1e308]); add([float('inf'), 1.0]); add([float('inf'), -1.0, 2.0])
json.dump(cases, open(sys.argv[1], 'w'))
print(len(cases), 'sums')
