"""Would a Grand Endeavour get one particular idea under study sooner than ordinary study, and at what cost? And how
often is the one of two ideas studied side by side that is behind discovered first? Benchmark games on a patched private
copy of the engine (the simulator is not modified), then an offline analysis.

Record, through scratch_run.sh with a cell's environment:
  python3 endeavour_oracle.py <world> <games> <suffix>        ORACLELOG=<path prefix> receives, per worker process,
    <prefix>.snap.<pid>: every ORACLEEVERY turns (default 10), each focus with ideas under study: the Insight it would
        receive as the active focus (income x the active share) and, for each idea, its progress, hidden meter (null if
        not yet drawn), price, Endeavour base price (its estimated price), cost multiplier and weight factor;
    <prefix>.pairs.<pid>: every pair of ideas studied side by side in one focus, once one of them is discovered: their
        weights (progress + 0.1) when the pair began, how often their order changed, and which was discovered first.
Analyse:
  python3 endeavour_oracle.py --analyse <path prefix> [runs]
    For every idea in every snapshot: make its focus active and play the focus forward on its own (no new ideas, prices
    and income as they stand; `runs` draws, default 20, for meters not yet drawn), and compare when ordinary study
    discovers the idea with when an Endeavour would, under each design in DESIGNS: today's (2x the price, from nothing,
    fed the active share); priced by the share of the idea's hidden meter still to fill, fed the active share or the
    whole income, at 2x, 1.5x or 1.25x; and a crash programme (delivered at once, its price repaid afterwards). An
    Endeavour always takes at least a turn. (The other prices measured on 15 October, the study done taken off before or
    after the premium, are in commit 2742a1a's version.)
Example (the expert, familiar world, every method; then delete results/w7f_familiar_oracle*.json, which w7f.py writes):
  cd design/simulator/power && for m in Warp Wormhole Hyperspace Tachyonic Tunnelling; do env PYTHONHASHSEED=0 DET=smart \
    ORSMART=1 PARALLEL=1 RUNON=1 DIFF=1 OBS=0 GLIMPSE=0.1 GLIMPSEU=0.03 END=2 ENDRULE=active INSTR_D=5 EXPFIX=1 \
    ENDFROM=theory METHODS=$m ORACLELOG=/tmp/oracle bash scratch_run.sh python3 endeavour_oracle.py familiar 60 _oracle_$m; done
  python3 endeavour_oracle.py --analyse /tmp/oracle
(The measurements of 15 October with a random wobble in the sharing, since scrapped, used commit 622a931's version.)
"""
import sys, os, json, glob, math
POWER = '/home/user/Uncharted-Horizons/design/simulator/power'
SHAPE, MOMENTUM, END_MULT = 4.0, 0.1, 2.0   # the meters' Gamma shape, the momentum and the Endeavour premium, as in the engine

HOOK = (
    "        _pid = str(__import__('os').getpid()); _fd = set(found)\n"
    "        for _f, _ks in pool.items():                                       # pairs studied side by side in one focus\n"
    "            for _i, _a in enumerate(_ks):\n"
    "                for _b in _ks[_i + 1:]:\n"
    "                    _key = (seed, _a, _b); _pr = ORACLE_PAIRS.get(_key)\n"
    "                    if _a in _fd or _b in _fd:\n"
    "                        if _pr is not None:\n"
    "                            with open(ORACLE_PATH + '.pairs.' + _pid, 'a') as _fh:\n"
    "                                _fh.write(json.dumps([seed, turn, _f, _a, _b, _pr[0], _pr[1], _pr[3], ('tie' if (_a in _fd and _b in _fd) else (_a if _a in _fd else _b))]) + '\\n')\n"
    "                            del ORACLE_PAIRS[_key]\n"
    "                        continue\n"
    "                    _wa = (progress.get(_a, 0.0) + prm.momentum) * aw(_a) * ATTN.get(_a, 1.0); _wb = (progress.get(_b, 0.0) + prm.momentum) * aw(_b) * ATTN.get(_b, 1.0)\n"
    "                    _sg = _wa >= _wb\n"
    "                    if _pr is None: ORACLE_PAIRS[_key] = [round(_wa, 5), round(_wb, 5), _sg, 0]\n"
    "                    elif _sg != _pr[2]: _pr[2] = _sg; _pr[3] += 1\n"
    "        if turn % ORACLE_EVERY == 0:                                      # snapshots for the Endeavour question\n"
    "            _F = inc * (0.8 if 'SO05' in have else 0.5); _snap = {}\n"
    "            for _f, _ks in pool.items():\n"
    "                _u = [k for k in _ks if k not in have]\n"
    "                if _u: _snap[_f] = [[k, round(progress.get(k, 0.0), 6), (round(need[k], 6) if k in need else None),\n"
    "                                     PRICE[ROWS[k]['era']] * prm.scale * prm.accel_price.get(k, 1.0) * prm.premium ** max(0.0, ERA_I[k] - d - prm.accelerate.get(k, 0.0)),\n"
    "                                     est_price(k), COSTMULT.get(k, 1.0), aw(k) * ATTN.get(k, 1.0), active == _f] for k in _u]\n"
    "            if _snap:\n"
    "                with open(ORACLE_PATH + '.snap.' + _pid, 'a') as _fh: _fh.write(json.dumps([seed, turn, round(d, 3), _F, _snap, inc]) + '\\n')\n")


def record():
    import types, runpy
    sys.path.insert(0, POWER)
    src = open(os.path.join(POWER, 'harness_ftl_e.py'), encoding='utf-8').read()
    anchor = "        log.append((turn, d, len(found)))\n"
    assert src.count(anchor) == 1
    mod = types.ModuleType('harness_ftl_e'); mod.__file__ = os.path.join(POWER, 'harness_ftl_e.py')
    exec(compile(src.replace(anchor, anchor + HOOK), mod.__file__, 'exec'), mod.__dict__)
    mod.ORACLE_PATH = os.environ['ORACLELOG']; mod.ORACLE_EVERY = int(os.environ.get('ORACLEEVERY', '10')); mod.ORACLE_PAIRS = {}
    sys.modules['harness_ftl_e'] = mod
    sys.argv = ['w7f.py'] + sys.argv[1:4]
    os.chdir(POWER)
    try: runpy.run_path(os.path.join(POWER, 'w7f.py'), run_name='__main__')
    except SystemExit: pass


def forward(items, F, runs, rng, tmax=400):
    """play one focus forward as the active focus: the turn each idea is discovered, in each run (inf: not within tmax)"""
    import numpy as np
    n = len(items)
    p0 = np.array([it[1] for it in items]); price = np.array([it[3] for it in items]); wf = np.array([it[6] for it in items])
    need = np.empty((runs, n))
    for j, it in enumerate(items):
        need[:, j] = it[2] if it[2] is not None else rng.gamma(SHAPE, 1 / SHAPE, runs) * it[5]
    need = np.maximum(need, p0 + 1e-9)
    p = np.tile(p0, (runs, 1)); alive = np.ones((runs, n), bool); when = np.full((runs, n), np.inf)
    for t in range(1, tmax + 1):
        left = np.full(runs, float(F))
        for _ in range(n + 1):
            w = wf * (p + MOMENTUM) * alive; tot = w.sum(1)
            go = (left > 1e-9) & (tot > 0)
            if not go.any(): break
            att = np.where(go[:, None], left[:, None] * w / np.where(tot > 0, tot, 1.0)[:, None], 0.0)
            room = (need - p) * price
            fin = alive & go[:, None] & (att >= room)
            spent = np.where(fin, room, att).sum(1)
            p = np.where(fin, need, p + att / price); when[fin] = t; alive &= ~fin
            left = np.where(fin.any(1), left - spent, 0.0)
        if not alive.any(): break
    return when, need


# Endeavour designs: (label, premium, the Insight it receives: 'active' (the active share) or a share of the whole income, delivered at
# once?, what it costs: 'price' (from nothing), 'share' (the price x the share of the hidden meter still to fill) or 'true' (the
# Insight the hidden meter still needs), share of the income lost while it runs)
DESIGNS = (('today', 2.0, 'active', False, 'price', 0.0), ('all, 1.25x', 1.25, 1.0, False, 'share', 0.0),
           ('crash, 2x', 2.0, 1.0, True, 'share', 0.0), ('70%, true', 1.0, 0.7, False, 'true', 0.1),
           ('70%, share', 1.0, 0.7, False, 'share', 0.1), ('60%, true', 1.0, 0.6, False, 'true', 0.2),
           ('50%, true', 1.0, 0.5, False, 'true', 0.3))


def _analyse_file(args):
    import numpy as np
    path, runs = args
    rng = np.random.default_rng(abs(hash(os.path.basename(path))) % (2 ** 32))
    rows = []   # one per idea: [ideas in its focus, funded focus?, frontier?, study turns (median)] + per design [P(sooner), mean turns
                #   saved, Endeavour turns, Insight beyond what study would spend, in turns of the whole income]
    for line in open(path):
        rec = json.loads(line)
        if len(rec) < 6: sys.exit('snapshots without the income: record them again')
        seed, turn, d, F, snap, inc = rec
        for f, items in snap.items():
            when, need = forward(items, F, runs, rng)
            for j, it in enumerate(items):
                ts = when[:, j]; ts = np.where(np.isinf(ts), 401.0, ts)
                left_ins = float(np.mean((need[:, j] - it[1]) * it[3]))      # Insight study still needs (the hidden meter's remainder)
                full = it[5] * it[4]; share_left = max(1.0 - it[1] / it[2], 0.0) if it[2] else 1.0
                row = [len(items), bool(it[7]), ERA_I.get(it[0], 0) >= int(d), float(np.median(ts))]
                for label, prem, src, now, basis, lost in DESIGNS:
                    rate = F if src == 'active' else inc * src
                    if basis == 'true':                    # the meter itself: drawn per run where it has not been drawn yet
                        costs = prem * np.maximum(need[:, j] - it[1], 0.0) * it[3]
                    else:
                        costs = np.full(runs, prem * full * (share_left if basis == 'share' else 1.0))
                    te = np.ones(runs) if now else np.maximum(1, np.ceil(costs / rate - 1e-9))
                    extra = float(np.mean(costs + lost * inc * te) - left_ins) / inc
                    row += [float((ts > te).mean()), float((ts - te).mean()), float(np.median(te)), extra]
                rows.append(row)
    return rows


ERA_I = {}


def analyse(prefix, runs):
    import numpy as np, multiprocessing
    sys.path.insert(0, POWER); import harness as H0
    ERA_I.update(H0.ERA_I)
    files = sorted(glob.glob(prefix + '.snap.*'))
    with multiprocessing.get_context('fork').Pool() as pool: parts = pool.map(_analyse_file, [(f, runs) for f in files])
    rows = np.array([r for part in parts for r in part], dtype=float)
    print(f"{len(rows)} ideas under study in {len(files)} snapshot files")
    def block(label, m):
        r = rows[m]
        if not len(r): return
        print(f"  {label}: {len(r)} ideas; switching to their focus, study takes a median {np.median(r[:, 3]):.0f} turns")
        for i, (name, *_) in enumerate(DESIGNS):
            b = 4 + 4 * i
            ratio = r[:, b + 2] / np.maximum(r[:, 3], 1)
            print(f"    {name:12} sooner {100 * r[:, b].mean():5.1f}% | turns saved, mean {r[:, b + 1].mean():5.2f} | Endeavour time / study time, "
                  f"median {np.median(ratio):4.2f} | extra Insight, in turns of the whole income: median {np.median(r[:, b + 3]):5.2f}, mean {r[:, b + 3].mean():5.2f}")
    slow = rows[:, 3] >= 2; front = rows[:, 2] == 1
    block('every idea under study', rows[:, 0] >= 1)
    block('study would take 2 turns or more', slow)
    block('frontier ideas (their era begun or ahead)', front)
    block('frontier, study 2 turns or more', front & slow)
    block('in the funded focus', rows[:, 1] == 1)
    block('alone in its focus, study 2 turns or more', (rows[:, 0] == 1) & slow)
    block('sharing its focus, study 2 turns or more', (rows[:, 0] >= 2) & slow)
    pairs = [json.loads(l) for f in sorted(glob.glob(prefix + '.pairs.*')) for l in open(f)]
    print(f"  pairs studied side by side: {len(pairs)}")
    for lo, hi in ((1, 1.25), (1.25, 1.5), (1.5, 2), (2, 4), (4, 1e9)):
        sel = [p for p in pairs if lo <= max(p[5], p[6]) / max(min(p[5], p[6]), 1e-9) < hi]
        if not sel: continue
        decided = [p for p in sel if p[8] != 'tie']
        behind_first = sum(1 for p in decided if p[8] == (p[4] if p[5] >= p[6] else p[3]))
        print(f"    leader ahead by x{lo:g}-{hi:g}: {len(sel):6d} pairs | the one behind discovered first {100 * behind_first / max(len(decided), 1):5.1f}%")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--analyse':
        analyse(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 20)
    else:
        record()
