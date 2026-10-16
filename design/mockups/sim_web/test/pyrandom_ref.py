"""Reference draws from CPython's random.Random for test_pyrandom.js: several seeds (small, 32-bit, multi-word, zero,
negative), random(), getrandbits(k) for k = 0..80, _randbelow via choice over lists of many lengths, choices with weights
and with cum_weights, gammavariate(4.0, 0.25) (the harness's meters), gammavariate(1.0, 2.0) and gammavariate(0.5, 1.5).
Floats are written as hex (float.hex) so nothing is lost; big ints as strings.
Usage: python3 -I pyrandom_ref.py <out.json>"""
import random, json, sys
SEEDS = [0, 1, 31, 17000, 17123, 17000 * 7919 + 13, 17000 * 104729 + 7, 2**32 - 1, 2**32, 2**40 + 12345, 2**64 + 99, 10**30 + 7, -5]
out = []
for seed in SEEDS:
    r = random.Random(seed)
    rec = {'seed': str(seed), 'ops': []}
    ops = rec['ops']
    for i in range(3000):
        ops.append(['random', r.random().hex()])
    for k in list(range(0, 81)) * 3:
        v = r.getrandbits(k)
        ops.append(['getrandbits', k, str(v)])
    for n in list(range(1, 300)) + [1000, 4097, 65536, 65537, 2**31, 2**31 + 1, 2**32 + 5, 2**45 + 3]:
        ops.append(['randbelow', str(n), str(r._randbelow(n))])
    for L in list(range(1, 140)) * 4:
        seq = list(range(L))
        ops.append(['choice', L, r.choice(seq)])
    for i in range(1500):
        n = 1 + i % 37
        w = [r.random() * (j + 1) for j in range(n)]
        ws = [x.hex() for x in w]
        ops.append(['choices', ws, r.choices(list(range(n)), w)[0]])
    for i in range(300):
        n = 1 + i % 11
        cw = [float(j + 1) * 1.5 for j in range(n)]
        ops.append(['cum_choices', [x.hex() for x in cw], r.choices(list(range(n)), cum_weights=cw, k=3)])
    for i in range(4000):
        ops.append(['gamma', 4.0, 0.25, r.gammavariate(4.0, 0.25).hex()])
    for i in range(500):
        ops.append(['gamma', 1.0, 2.0, r.gammavariate(1.0, 2.0).hex()])
    for i in range(1000):
        ops.append(['gamma', 0.5, 1.5, r.gammavariate(0.5, 1.5).hex()])
    ops.append(['random', r.random().hex()])
    out.append(rec)
json.dump(out, open(sys.argv[1], 'w'))
print(sum(len(r['ops']) for r in out), 'operations for', len(SEEDS), 'seeds')
