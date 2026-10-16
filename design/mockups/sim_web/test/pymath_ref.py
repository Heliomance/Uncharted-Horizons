"""Reference values for test_pymath.js: Python's math.exp, math.log, float ** float and math.fma (3.13) on millions of
arguments, written as raw little-endian doubles to <out_dir>/{exp,log,pow,fma}.bin (arguments then result, per case).
The engine's own uses are covered densely (prices 4 ** x, occurrence chances (1 - p) ** (1 / W), rediscovery 0.9 ** n,
the gamma meters' log and exp), and the whole range sparsely: random bit patterns, subnormals, near 1, specials.
Usage: python3 -I pymath_ref.py <out_dir> [millions=1] [seed]"""
import sys, os, math, struct, random
out = sys.argv[1]; M = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
os.makedirs(out, exist_ok=True)
r = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 20261015)
def bits_double(lo_e=0, hi_e=2047, sign=True):
    e = r.randint(lo_e, hi_e); m = r.getrandbits(52); s = r.getrandbits(1) if sign else 0
    return struct.unpack('<d', struct.pack('<Q', (s << 63) | (e << 52) | m))[0]
def write(name, rows):
    with open(os.path.join(out, name + '.bin'), 'wb') as f:
        for row in rows: f.write(struct.pack('<%dd' % len(row), *row))
    print(name, len(rows))
n = int(1_000_000 * M)
# exp
xs = [r.uniform(-6.2, 6.2) for _ in range(n // 2)] + [r.uniform(-745.2, 709.8) for _ in range(n // 4)]
xs += [bits_double(0x3b0, 0x40a) for _ in range(n // 4)] + [0.0, -0.0, 1e-300, -1e-300, 709.78, 709.79, -745.13, -745.14, -708.5, float('inf'), float('-inf')]
rows = []
for x in xs:
    try: y = math.exp(x)
    except OverflowError: y = float('inf')
    rows.append((x, y))
write('exp', rows)
# log
xs = []
for _ in range(n // 4):
    u1 = r.random()
    if 1e-7 < u1 < 0.9999999: xs.append(u1 / (1.0 - u1))
    u = r.random(); xs.append(u * u * (1.0 - r.random()) or 0.5)
xs += [r.uniform(0.9375, 1.0647) for _ in range(n // 4)] + [bits_double(0, 2046, False) for _ in range(n // 4)]
xs += [5e-324, 1e-310, 2.2250738585072014e-308, 1.0, 1.0000000000000002, 0.9999999999999999, 1.7976931348623157e308]
write('log', [(x, math.log(x)) for x in xs if x > 0])
# pow
rows = []
def addp(x, y):
    try: z = x ** y
    except OverflowError: z = float('inf')
    except ZeroDivisionError: return
    if isinstance(z, complex): return
    rows.append((x, y, z))
for _ in range(n // 4): addp(4.0, max(0.0, r.uniform(-1, 7.5)))
for _ in range(n // 4):
    p = r.choice([0.85, 0.4, 0.1, 0.065, 0.999]); W = max(r.uniform(0.3, 70), 1.0); addp(1 - min(p, 0.999), 1 / W)
for k in range(0, 400): addp(1 - 0.1, k); addp(0.9, -k)
for _ in range(n // 4): addp(r.uniform(1e-6, 1e6), r.uniform(-60, 60))
for _ in range(n // 8): addp(bits_double(1, 2046, False), bits_double(0x300, 0x430))
for _ in range(n // 16): addp(-r.uniform(0.01, 100), float(r.randint(-60, 60)))
for x in (0.0, -0.0, 1.0, -1.0, 2.0, 0.5, float('inf'), float('-inf'), 5e-324, 1e308):
    for y in (0.0, -0.0, 1.0, -1.0, 2.0, 3.0, 0.5, -0.5, 1e-70, 1e300, -1e300, float('inf'), float('-inf'), 1075.0, -1075.0):
        addp(x, y)
write('pow', rows)
# fma
rows = []
for _ in range(n // 2):
    a = r.uniform(-4, 4) * 10 ** r.uniform(-5, 5); b = r.uniform(-4, 4) * 10 ** r.uniform(-5, 5)
    c = -(a * b) * (1 + r.uniform(-1e-12, 1e-12)) if r.random() < 0.5 else r.uniform(-1, 1) * 10 ** r.uniform(-10, 10)
    rows.append((a, b, c, math.fma(a, b, c)))
for _ in range(n // 4):
    a, b, c = bits_double(800, 1250), bits_double(800, 1250), bits_double(600, 1450)
    rows.append((a, b, c, math.fma(a, b, c)))
for _ in range(n // 8):
    a, b, c = bits_double(1, 2046), bits_double(1, 2046), bits_double(0, 2046)
    try: rows.append((a, b, c, math.fma(a, b, c)))
    except (OverflowError, ValueError): pass
write('fma', rows)
