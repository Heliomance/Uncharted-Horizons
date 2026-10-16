"""When did the FTL methods' spread open? Reads saved benchmark results at every checkpoint since round two and, for each
player and world, gives each method's median race finish (max(certainty, build complete)) and median victory (victory.py,
with the checkpoint's Space price and development boundaries) against the world's field (all its methods' games pooled),
the largest and RMS deviation, win shares (a game beats each field game finishing later and half the ties), unfinished
counts, and the medians of the unified theory, certainty and build. Where discovery turns ('t') were saved, also the median
turn of each method's last build requirement and which one it was.

Read-only on the repository. Usage:  python3 ftl_drift.py [--detail] [--only KEY,KEY] [--compact]  (prints to stdout)
Written for the 16 Oct 2026 question why the methods drifted apart (results/ftl_drift_20261016.txt).
"""
import sys, os, json, math, statistics as st, collections, bisect
POWER = '/home/user/Uncharted-Horizons/design/simulator/power'
R = os.path.join(POWER, 'results')
sys.path.insert(0, POWER)
import victory as V   # imports defaults (today's switches) and harness_ftl_e

WORLDS = {'familiar': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling'],
          'Process': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum'],
          'Substance': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum']}
ECON = {'X': 1.0, 'N': 1.0, 'A': 0.8}
PNAME = {'X': 'expert', 'N': 'novice', 'A': 'average'}
# round one's package cells (balance_rounds.py): the K runs replace these cells, the rest stay as XF/NF/AV
PKG = {('familiar', 'Wormhole'), ('familiar', 'Warp'), ('familiar', 'Tachyonic'), ('Substance', 'Wormhole'), ('Substance', 'Warp'),
       ('Substance', 'Plenum'), ('Process', 'Wormhole'), ('Process', 'Warp'), ('Process', 'Plenum')}
DEV_V122 = 'Modern:66231,Atomic:113629,Space:209676'
DEV_NOW = 'Primitive:194,Ancient:1052,Classical:2590,Medieval:6859,Early_Modern:23900,Modern:66231,Atomic:113629,Space:209676'


def cell(lab): return lambda w, m: json.load(open(os.path.join(R, f'w7f_{w}_{lab}_{m}.json')))
def world(lab): return lambda w, m: [g for g in json.load(open(os.path.join(R, f'w7f_{w}_{lab}.json'))) if g['m'] == m]
def round1(base): return lambda w, m: json.load(open(os.path.join(R, f'w7f_{w}_{base + "K" if (w, m) in PKG else base}_{m}.json')))
def cmp(lab): return {p: cell(f'cmp{lab}{p}') for p in 'XNA'}


# Checkpoints in time order. sp/dev: the Space price and development boundaries the runs had (victory.py needs them);
# dev None = the boundaries before v3.122 (DEVENDS empty).
CK = [
    dict(key='P', when='13 Oct (claude.ai)', what='pre-round-one design, LEVERS=abcrw, old expert (no EXPFIX) / novice without Endeavours',
         sp=1.0, dev=None, src={'X': cell('P'), 'N': cell('N')}),
    dict(key='R0', when='13 Oct (claude.ai)', what='"current" before round one: LEVERS=abcrw, expert EXPFIX=1 ENDFROM=theory; novice with Endeavours (NF)',
         sp=1.0, dev=None, src={'X': cell('XF'), 'N': cell('NF'), 'A': cell('AV')}),
    dict(key='R1', when='13 Oct (claude.ai)', what='round one: package (abcrwgxpny) in 9 cells, R0 elsewhere',
         sp=1.0, dev=None, src={'X': round1('XF'), 'N': round1('NF'), 'A': round1('AV')}),
    dict(key='R2', when='14 Oct 07:55 (claude.ai)', what='ROUND TWO: LEVERS=abcrwgpnyhuk WROWX=4, Space x1, no W18 pools (q)',
         sp=1.0, dev=None, src={'X': cell('XF2'), 'N': cell('NF2'), 'A': cell('AV2')}),
    dict(key='R2t', when='14 Oct (claude.ai)', what='round two again, 20 games a method, SAVE_T (TPX/TPN/TPA)',
         sp=1.0, dev=None, src={'X': world('TPX'), 'N': world('TPN'), 'A': world('TPA')}),
    dict(key='R2q', when='14 Oct 09:29 (claude.ai)', what='round two + W18 signature pools (q), Space x1, 20 a method, SAVE_T (TPXq/TPNq/TPAq)',
         sp=1.0, dev=None, src={'X': world('TPXq'), 'N': world('TPNq'), 'A': world('TPAq')}),
    dict(key='TF', when='14 Oct (claude.ai)', what='abcrwgpnyhukq + Space x0.8, 20 a method (TFX/TFN/TFA)',
         sp=0.8, dev=None, src={'X': world('TFX'), 'N': world('TFN'), 'A': world('TFA')}),
    dict(key='TB', when='14 Oct (claude.ai)', what='abcrwgpnyhukq + Space x0.8, 20 a method, SAVE_T (TBX/TBN/TBA)',
         sp=0.8, dev=None, src={'X': world('TBX'), 'N': world('TBN'), 'A': world('TBA')}),
    dict(key='TVC', when='14 Oct (claude.ai)', what='abcrwgpnyhukqvV + Space x0.8, expert only, 20 a method, SAVE_T (TVCX)',
         sp=0.8, dev=None, src={'X': world('TVCX')}),
    dict(key='R3', when='14 Oct 11:24 (claude.ai)', what='FINAL CONFIRMATION ("2,700 games"): abcrwgpnyhukqvV WROWX=4 Space x0.8 (XF3/NF3/AV3)',
         sp=0.8, dev=None, src={'X': cell('XF3'), 'N': cell('NF3'), 'A': cell('AV3')}),
    dict(key='EndFix', when='14 Oct 20:29 (repo 1f5f224)', what='v3.112+ tree, defaults abcrwgpnyhukqvVm (CP10 2x), glimpse by tier, Endeavour split fixed',
         sp=0.8, dev=None, src=cmp('EndFix')),
    dict(key='TierAtt0', when='14 Oct 20:58 (a603864)', what='+ every tier studied alike once occurred (TIERATT=0, became default)',
         sp=0.8, dev=None, src=cmp('TierAtt0')),
    dict(key='B0', when='15 Oct 10:13 (304fd03)', what='v3.114 tree (Experiment/Synthesis/Dialectical removed), seeds 17000',
         sp=0.8, dev=None, src=cmp('B0')),
    dict(key='EF', when='15 Oct 10:13 (304fd03)', what='v3.114 + EARLYFIX=1 (variant)', sp=0.8, dev=None, src=cmp('EF')),
    dict(key='B0s2', when='15 Oct 10:48 (4ffdb12)', what='v3.114, second seed set (SEED0=27000)', sp=0.8, dev=None, src=cmp('B0s2')),
    dict(key='A16', when='15 Oct 10:48 (4ffdb12)', what='v3.115 tree (16 early-row prerequisites)', sp=0.8, dev=None, src=cmp('A16')),
    dict(key='A16s2', when='15 Oct 10:48 (4ffdb12)', what='v3.115, second seed set', sp=0.8, dev=None, src=cmp('A16s2')),
    dict(key='U1', when='15 Oct 10:48 (4ffdb12)', what='v3.115 + UNIV=1 (variant)', sp=0.8, dev=None, src=cmp('U1')),
    dict(key='P120', when='15 Oct 12:28 (2532a7a)', what='v3.120: safety net (REDISCOVER=0.1 ENDUNOCC=1 W16=0)', sp=0.8, dev=None, src=cmp('P120')),
    dict(key='incN', when='15 Oct 15:43 (c1b1b74)', what='v3.121 expert, SAVE_T ("defaults reproduce P120 exactly")', sp=0.8, dev=None, src={'X': cell('incN')}),
    dict(key='xtx0', when='15 Oct 17:54 (d8b2ebb)', what='v3.122 defaults (base Civ V era timing, Mod/Atom x1.25, Space x2), OLD expert, SAVE_T',
         sp=2.0, dev=DEV_V122, src={'X': cell('xtx0')}),
    dict(key='V122', when='15 Oct 17:54 (d8b2ebb)', what='v3.122: base Civ V era timing (DEVENDS late), Mod/Atom x1.25, Space x2, pool122, expert EXPCAP=2 ENDRULE=last',
         sp=2.0, dev=DEV_V122, src=cmp('V122')),
    dict(key='xty2', when='15 Oct 17:54 (d8b2ebb)', what='v3.122 adopted expert (EXPCAP=2 ENDRULE=last), SAVE_T', sp=2.0, dev=DEV_V122, src={'X': cell('xty2')}),
    dict(key='pbXold', when='15 Oct 19:22 (19115bf)', what='PB settings, OLD expert (ENDRULE=active, no cap)', sp=1.0, dev=DEV_V122, src={'X': cell('pbXold')}),
    dict(key='pbXlast', when='15 Oct 19:22 (19115bf)', what='PB settings, expert ENDRULE=last without the cap', sp=1.0, dev=DEV_V122, src={'X': cell('pbXlast')}),
    dict(key='PB', when='15 Oct 19:22 (19115bf)', what='v3.122 timing, Mod/Atom/Space x1, rivals pb', sp=1.0, dev=DEV_V122, src=cmp('PB')),
    dict(key='PD', when='15 Oct 19:22 (19115bf)', what='v3.122 timing, Mod/Atom x1.1, Space x1, rivals pd (variant)', sp=1.0, dev=DEV_V122, src=cmp('PD')),
    dict(key='V123', when='15 Oct 20:30 (1d88689)', what='v3.123: Ancient x1.5 + Primitive span, Space x1, pool123', sp=1.0, dev=DEV_NOW, src=cmp('V123')),
    dict(key='V124', when='15 Oct 21:45 (2a49595)', what='v3.124: merges/cuts/demotions, COMPETE=1, Space x1.05, pool124', sp=1.05, dev=DEV_NOW, src=cmp('V124')),
    dict(key='V125', when='15 Oct 22:51 (c3e0a4d)', what='v3.125: Ring Fortress merged, pool125', sp=1.05, dev=DEV_NOW, src=cmp('V125')),
]
# familiar-only checkpoints, shown separately
CKF = [
    dict(key='V116', when='15 Oct 11:12', what='v3.116 (familiar only)', sp=0.8, dev=None, src=cmp('V116')),
    dict(key='V117', when='15 Oct 11:25', what='v3.117 (familiar only)', sp=0.8, dev=None, src=cmp('V117')),
    dict(key='V118', when='15 Oct 11:36', what='v3.118 (familiar only)', sp=0.8, dev=None, src=cmp('V118')),
    dict(key='PKG119', when='15 Oct 11:46', what='v3.119 + safety net incl. W16 (familiar only)', sp=0.8, dev=None, src=cmp('PKG119')),
    dict(key='PKGNOW119', when='15 Oct 11:46', what='v3.119 + safety net, W16=0 (familiar only)', sp=0.8, dev=None, src=cmp('PKGNOW119')),
]

# build requirements (ftl_balance.py's, which follow w7f.py with the agreed levers); RC01 was RC02 in the claude.ai tree
BUILD = {'atomic': {'Warp': [['RC01', 'RC02'], ['QP08'], ['QP11'], ['MS08'], ['ES06', 'ES07', 'ES14', 'ES08'], ['ES18']],
                    'Wormhole': [['RC01', 'RC02'], ['QP08'], ['QP11'], ['MS08'], ['RC04'], ['QP12'], ['MA13'], ['MS17']],
                    'Hyperspace': [['QP08'], ['MA13'], ['ES06', 'ES07', 'ES14', 'ES08'], ['MA19']],
                    'Tunnelling': [['QP02'], ['CP10'], ['MS02', 'GN05'], ['QP14'], ['CP21']],
                    'Tachyonic': [['QP06'], ['QP08'], ['SE02'], ['ES06', 'ES07', 'ES14', 'ES08'], ['NP15']]},
         'elemental': {'Warp': [['RC01', 'RC02'], ['QM-E27'], ['QM-E06'], ['MS08'], ['ES07', 'ES15', 'QM-E05'], ['ES18']],
                       'Wormhole': [['RC01', 'RC02'], ['QM-E27'], ['QM-E06'], ['MS08'], ['RC04'], ['QM-E13'], ['MA13'], ['MS17']],
                       'Hyperspace': [['QM-E27'], ['MA13'], ['ES07', 'ES15', 'QM-E05'], ['MA19']],
                       'Tachyonic': [['QM-E17'], ['QM-E27'], ['ES07', 'ES15', 'QM-E05'], ['SE02'], ['TH20']],
                       'Plenum': [['QM-E27'], ['MS02'], ['QM-E19'], ['QM-E23'], ['AE20']]}}
ONT = {'familiar': 'atomic', 'Process': 'elemental', 'Substance': 'elemental'}
CLOSE = {'atomic': 'QP08', 'elemental': 'QM-E27'}


def set_era(ck):
    """victory.py with the checkpoint's Space price and development boundaries"""
    V.SPACEPRICE = ck['sp']
    V.HF.DEV_ENDS = {e.replace('_', ' '): float(x) for e, x in (i.split(':') for i in ck['dev'].split(','))} if ck['dev'] else None
    V.HF.SPACE_FROM = None
    V._clocks.clear(); _VC.clear()


def num(x): return x[0] if isinstance(x, (list, tuple)) else x


def finish(g):
    c, b = num(g['cert']), g['built']
    return max(c, b) if c and b else None


_VC = {}


def vic(g, econ):
    """victory.victory(g, econ), memoised on (finish, economy, exotic): all it depends on for a given era setting"""
    fin = finish(g)
    if fin is None: return None
    key = (fin, econ, g['m'] in V.EXOTIC)
    if key not in _VC: _VC[key] = V.victory(dict(g, cert=num(g['cert'])), econ)
    return _VC[key]


def wins(mine, field):
    srt = sorted(field); n = len(srt)
    def beat(x):
        lo, hi = bisect.bisect_left(srt, x), bisect.bisect_right(srt, x)
        return (n - hi + 0.5 * (hi - lo)) / n
    return st.mean(beat(x) for x in mine) if mine else float('nan')


def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


def last_build(g, ont):
    t = g.get('t')
    if not t: return None
    met = {tuple(gr): min((t[o] for o in gr if o in t), default=None) for gr in BUILD[ont][g['m']]}
    if any(v is None for v in met.values()): return None
    k = max(met, key=lambda k: met[k])
    return '/'.join(x for x in k if x in t) or k[0], met[k]


def analyse(ck):
    set_era(ck); out = {}
    for p, loader in ck['src'].items():
        econ = ECON[p]
        for w, ms in WORLDS.items():
            try: games = {m: loader(w, m) for m in ms}
            except FileNotFoundError: continue
            ont = ONT[w]
            F = {m: [finish(g) for g in gs] for m, gs in games.items()}
            Vv = {m: [vic(g, econ) for g in gs] for m, gs in games.items()}
            row = dict(n={m: len(gs) for m, gs in games.items()}, unf={m: sum(x is None for x in F[m]) for m in ms})
            for nm, D in (('fin', F), ('vic', Vv)):
                d = {m: [x for x in xs if x is not None] for m, xs in D.items()}
                field = [x for xs in d.values() for x in xs]; fm = st.median(field)
                dev = {m: st.median(xs) - fm for m, xs in d.items()}
                row[nm] = dict(field=fm, dev=dev, med={m: st.median(xs) for m, xs in d.items()}, win={m: wins(xs, field) for m, xs in d.items()},
                               maxdev=max(abs(x) for x in dev.values()), rms=math.sqrt(st.mean(x * x for x in dev.values())))
            row['close'] = {m: med([g['close'] for g in gs]) for m, gs in games.items()}
            row['cert'] = {m: med([num(g['cert']) for g in gs]) for m, gs in games.items()}
            row['built'] = {m: med([g['built'] for g in gs]) for m, gs in games.items()}
            row['space'] = {m: med([g.get('space') for g in gs]) for m, gs in games.items()}
            row['bbind'] = {m: (sum(1 for g in gs if finish(g) and g['built'] > num(g['cert'])) / max(1, sum(1 for g in gs if finish(g)))) for m, gs in games.items()}
            lbs = {m: [x for x in (last_build(g, ont) for g in gs) if x] for m, gs in games.items()}
            row['lastb'] = {m: (collections.Counter(k for k, _ in xs).most_common(2), st.median(t for _, t in xs), len(xs)) for m, xs in lbs.items() if xs}
            out[(p, w)] = row
    return out


def short(m): return {'Tunnelling': 'Tunn', 'Plenum': 'Plen', 'Hyperspace': 'Hyp', 'Wormhole': 'Worm', 'Tachyonic': 'Tach', 'Warp': 'Warp'}[m]


def main():
    detail = '--detail' in sys.argv
    only = None
    if '--only' in sys.argv: only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    res = {}
    for ck in CK + CKF:
        if only and ck['key'] not in only: continue
        res[ck['key']] = analyse(ck)
    print('Checkpoints (median race finish = max(certainty, build); victory = victory.py with the checkpoint\'s Space price and DEVENDS)')
    for ck in CK + CKF:
        if ck['key'] in res: print(f"  {ck['key']:9} {ck['when']:26} sp x{ck['sp']:<4} dev {'v3.122' if ck['dev'] == DEV_V122 else ('now' if ck['dev'] else 'old')}  {ck['what']}")

    # summary
    print('\n=== SUMMARY: mean over worlds and players of the largest |deviation| and RMS (finish | victory); win shares on victory; unfinished')
    print(f"  {'ckpt':9} {'players':7} {'fin max':>7} {'fin rms':>7} | {'vic max':>7} {'vic rms':>7} | {'win range':>9} | {'>5 (vic)':>8} | unfinished / games")
    for key, out in res.items():
        rs = list(out.values())
        if not rs: continue
        players = ''.join(sorted({p for p, _ in out}, key='XNA'.index))
        wl = [x for r in rs for x in r['vic']['win'].values()]
        over5 = sum(1 for r in rs for x in r['vic']['dev'].values() if abs(x) > 5); cells = sum(len(r['vic']['dev']) for r in rs)
        print(f"  {key:9} {players:7} {st.mean(r['fin']['maxdev'] for r in rs):7.1f} {st.mean(r['fin']['rms'] for r in rs):7.1f} | "
              f"{st.mean(r['vic']['maxdev'] for r in rs):7.1f} {st.mean(r['vic']['rms'] for r in rs):7.1f} | {min(wl):4.0%}-{max(wl):3.0%} | {over5:3d}/{cells:<3d} | "
              f"{sum(sum(r['unf'].values()) for r in rs)} / {sum(sum(r['n'].values()) for r in rs)}")

    # per method story: mean deviation (finish) over worlds and players present
    for nm, lab in (('fin', 'RACE FINISH'), ('vic', 'VICTORY')):
        print(f'\n=== PER METHOD: mean {lab} deviation from the field over worlds and players present (turns; + = slow)')
        print(f"  {'ckpt':9} " + ' '.join(f'{m:>7}' for m in ('Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Plenum')) + '   | expert only: ' + ' '.join(f'{short(m):>5}' for m in ('Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Plenum')))
        for key, out in res.items():
            def mdev(m, ponly=None):
                xs = [r[nm]['dev'][m] for (p, w), r in out.items() if m in r[nm]['dev'] and (ponly is None or p == ponly)]
                return f'{st.mean(xs):+7.1f}' if xs else '      -'
            def mdev5(m):
                xs = [r[nm]['dev'][m] for (p, w), r in out.items() if m in r[nm]['dev'] and p == 'X']
                return f'{st.mean(xs):+5.1f}' if xs else '    -'
            print(f"  {key:9} " + ' '.join(mdev(m) for m in ('Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Plenum'))
                  + '   |              ' + ' '.join(mdev5(m) for m in ('Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling', 'Plenum')))

    # per checkpoint table
    print('\n=== PER CHECKPOINT, PLAYER AND WORLD: field median; each method finish dev / victory dev (win share on victory); max, rms; unfinished')
    for key, out in res.items():
        print(f'\n--- {key}')
        for (p, w), r in out.items():
            ms = WORLDS[w]
            print(f"  {PNAME[p]:7} {w:9} field fin {r['fin']['field']:5.0f} vic {r['vic']['field']:5.0f} | "
                  + '  '.join(f"{short(m)} {r['fin']['dev'][m]:+3.0f}/{r['vic']['dev'][m]:+3.0f} ({r['vic']['win'][m]:.0%})" for m in ms)
                  + f" | fin max {r['fin']['maxdev']:2.0f} rms {r['fin']['rms']:4.1f}; vic max {r['vic']['maxdev']:2.0f} rms {r['vic']['rms']:4.1f}"
                  + (f"; unf {sum(r['unf'].values())}" if sum(r['unf'].values()) else ''))
            if detail:
                print('      theory/cert/built/first-Space (build binds): ' + '  '.join(
                    f"{short(m)} {r['close'][m]:.0f}/{r['cert'][m]:.0f}/{r['built'][m]:.0f}/{r['space'][m]:.0f} ({r['bbind'][m]:.0%})" for m in ms if r['built'][m] is not None))
                if r['lastb']:
                    print('      last build need (share of games, median turn): ' + '  '.join(
                        f"{short(m)} " + ','.join(f'{k} {c / r["lastb"][m][2]:.0%}' for k, c in r['lastb'][m][0]) + f" @{r['lastb'][m][1]:.0f}"
                        for m in ms if m in r['lastb']))




def compact(keys=None):
    """per checkpoint and player: each world's method deviations (finish/victory), max and rms (finish/victory), unfinished;
    and the per-player mean of the largest deviation"""
    W3 = {'familiar': 'fam', 'Process': 'Pro', 'Substance': 'Sub'}
    for ck in CK + CKF:
        if keys and ck['key'] not in keys: continue
        out = analyse(ck)
        print(f"\n--- {ck['key']} ({ck['what']})")
        for p in 'XNA':
            rs = {w: r for (pp, w), r in out.items() if pp == p}
            if not rs: continue
            mx = st.mean(r['fin']['maxdev'] for r in rs.values()); mv = st.mean(r['vic']['maxdev'] for r in rs.values())
            print(f"  {PNAME[p]:7} mean max fin {mx:4.1f} vic {mv:4.1f} | " + ' | '.join(
                f"{W3[w]} " + ' '.join(f"{short(m)[:2]}{r['fin']['dev'][m]:+.0f}/{r['vic']['dev'][m]:+.0f}" for m in WORLDS[w])
                + f" (max {r['fin']['maxdev']:.0f}/{r['vic']['maxdev']:.0f}, rms {r['fin']['rms']:.1f}/{r['vic']['rms']:.1f}" + (f", unf {sum(r['unf'].values())}" if sum(r['unf'].values()) else '') + ')'
                for w, r in rs.items()))


if __name__ == '__main__':
    if '--compact' in sys.argv: compact(set(sys.argv[sys.argv.index('--compact') + 1].split(',')) if len(sys.argv) > sys.argv.index('--compact') + 1 else None)
    else: main()
